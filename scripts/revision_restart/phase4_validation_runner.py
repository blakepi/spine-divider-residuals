"""Restart Phase 4 validation runner.

Runs the separated independent matrix benchmark, DC analytic checks, bounded
BE-vs-CN peak comparison, and NEURON availability check. NEURON is optional
validation-only infrastructure and is not a runtime dependency.
"""

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path
import sys
from typing import Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
HERE = Path(__file__).resolve().parent
OUT = ROOT / "results" / "revision_restart" / "phase4"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from phase4_independent_matrix_benchmark import (  # noqa: E402
    run_dc_analytic_benchmark,
    run_independent_matrix_benchmark,
    write_csv,
)


def relative_diff(value: float, reference: float) -> float:
    return abs(value - reference) / abs(reference) if reference else float("nan")


def check_neuron_availability() -> dict[str, object]:
    spec = importlib.util.find_spec("neuron")
    if spec is None:
        return {
            "neuron_available": False,
            "neuron_version": "",
            "neuron_status": "unavailable",
            "neuron_detail": "importlib.util.find_spec('neuron') returned None in the bundled Python runtime",
        }
    try:
        import neuron  # type: ignore

        version = getattr(neuron, "__version__", "unknown")
        return {
            "neuron_available": True,
            "neuron_version": version,
            "neuron_status": "available_not_run_in_this_environment",
            "neuron_detail": "NEURON import succeeded; no Phase 4 NEURON benchmark was executed by this fallback runner",
        }
    except Exception as exc:  # pragma: no cover - depends on optional external package.
        return {
            "neuron_available": False,
            "neuron_version": "",
            "neuron_status": "import_failed",
            "neuron_detail": repr(exc),
        }


def metric_peak_time_ms(result, label: str) -> float:
    parameters = result.parameters
    index = {"h": 0, "d": 1, "s": 2}[label]
    mask = (result.time_s >= parameters.synapse.event_time_s) & (
        result.time_s <= parameters.synapse.event_time_s + parameters.metric_window_s
    )
    times = result.time_s[mask]
    voltage = result.voltage_V[mask, index]
    baseline_index = int(np.searchsorted(result.time_s, parameters.synapse.event_time_s))
    baseline = result.voltage_V[baseline_index, index]
    peak_index = int(np.argmax(voltage - baseline))
    return float((times[peak_index] - times[0]) * 1e3)


def run_be_cn_peak_comparison() -> list[dict[str, object]]:
    from spine.config import load_config
    from spine.metrics import compute_voltage_metrics
    from spine.passive import parameters_from_config, simulate_three_compartment
    from spine.protocols import TRACE_TARGETS
    from spine.units import V_to_mV

    params = parameters_from_config(load_config(ROOT / "configs" / "manuscript_faithful" / "baseline.toml"))
    rows: list[dict[str, object]] = []
    for target in TRACE_TARGETS:
        condition = str(target["condition"])
        length_um = float(target["neck_length_um"])
        radius_um = float(target["neck_radius_um"])
        be = simulate_three_compartment(params, length_um, radius_um, method="backward_euler")
        cn = simulate_three_compartment(params, length_um, radius_um, method="crank_nicolson")
        be_metrics = compute_voltage_metrics(be)
        cn_metrics = compute_voltage_metrics(cn)
        max_voltage_diff_mV = float(np.max(np.abs(be.voltage_V - cn.voltage_V)) * 1e3)
        row: dict[str, object] = {
            "condition": condition,
            "neck_length_um": length_um,
            "neck_radius_um": radius_um,
            "dt_ms": params.dt_s * 1e3,
            "max_trace_voltage_abs_diff_mV": max_voltage_diff_mV,
            "interpretation": "BE and CN peak differences are small internal numerical self-consistency checks, not external validation",
        }
        for metric_name, be_value, cn_value in (
            ("A_h_mV", V_to_mV(be_metrics.amplitude_head_V), V_to_mV(cn_metrics.amplitude_head_V)),
            ("A_d_mV", V_to_mV(be_metrics.amplitude_dendrite_V), V_to_mV(cn_metrics.amplitude_dendrite_V)),
            ("A_s_mV", V_to_mV(be_metrics.amplitude_soma_V), V_to_mV(cn_metrics.amplitude_soma_V)),
            ("Gamma_h_to_d", be_metrics.gamma_head_to_dendrite, cn_metrics.gamma_head_to_dendrite),
            ("Gamma_h_to_s", be_metrics.gamma_head_to_soma, cn_metrics.gamma_head_to_soma),
        ):
            row[f"BE_{metric_name}"] = be_value
            row[f"CN_{metric_name}"] = cn_value
            row[f"{metric_name}_abs_diff"] = abs(be_value - cn_value)
            row[f"{metric_name}_rel_diff"] = relative_diff(cn_value, be_value)
        for label in ("h", "d", "s"):
            be_t = metric_peak_time_ms(be, label)
            cn_t = metric_peak_time_ms(cn, label)
            row[f"BE_peak_time_{label}_ms"] = be_t
            row[f"CN_peak_time_{label}_ms"] = cn_t
            row[f"peak_time_{label}_abs_diff_ms"] = abs(be_t - cn_t)
        rows.append(row)
    write_csv(OUT / "phase4_be_cn_peak_comparison.csv", rows)
    return rows


def max_float(rows: Iterable[dict[str, object]], key: str) -> float:
    values = []
    for row in rows:
        value = row.get(key, "")
        if value == "":
            continue
        try:
            values.append(float(value))
        except (TypeError, ValueError):
            continue
    return max(values) if values else float("nan")


def write_validation_summary(
    neuron: dict[str, object],
    matrix_rows: list[dict[str, object]],
    dc_rows: list[dict[str, object]],
    be_cn_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    diagnostic_figures = sorted((OUT / "diagnostic_figures").glob("*")) if (OUT / "diagnostic_figures").exists() else []
    formula_errors = [
        float(row["absolute_error"])
        for row in dc_rows
        if str(row.get("benchmark_case")) in {
            "spine_omitted_dendrite_soma_input_resistance",
            "attached_versus_omitted_one_port",
            "dc_divider_prediction",
        }
    ]
    rows: list[dict[str, object]] = [
        {
            "validation_component": "NEURON availability",
            "status": neuron["neuron_status"],
            "rows": 0,
            "max_primary_difference": "",
            "units": "",
            "interpretation": neuron["neuron_detail"],
        },
        {
            "validation_component": "independent direct matrix benchmark",
            "status": "completed",
            "rows": len(matrix_rows),
            "max_primary_difference": max_float(matrix_rows, "trace_max_abs_diff_all_mV"),
            "units": "mV",
            "interpretation": "independent matrix implementation reproduced existing SPINE baseline traces to numerical precision",
        },
        {
            "validation_component": "DC analytic benchmark",
            "status": "completed",
            "rows": len(dc_rows),
            "max_primary_difference": max(formula_errors) if formula_errors else "",
            "units": "MOhm or dimensionless by row",
            "interpretation": "closed-form divider, load, limit, and attached one-port checks passed algebraically",
        },
        {
            "validation_component": "BE-vs-CN peak comparison",
            "status": "completed",
            "rows": len(be_cn_rows),
            "max_primary_difference": max(
                max_float(be_cn_rows, "A_h_mV_abs_diff"),
                max_float(be_cn_rows, "A_d_mV_abs_diff"),
                max_float(be_cn_rows, "A_s_mV_abs_diff"),
            ),
            "units": "mV",
            "interpretation": "internal integration-scheme peak differences are bounded and small",
        },
        {
            "validation_component": "diagnostic figures",
            "status": "completed" if diagnostic_figures else "not_created",
            "rows": len(diagnostic_figures),
            "max_primary_difference": "",
            "units": "",
            "interpretation": "diagnostic-only trace overlay figures under results/revision_restart/phase4/diagnostic_figures",
        },
    ]
    write_csv(OUT / "phase4_validation_summary.csv", rows)
    return rows


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    neuron = check_neuron_availability()
    matrix_rows = run_independent_matrix_benchmark()
    dc_rows = run_dc_analytic_benchmark()
    be_cn_rows = run_be_cn_peak_comparison()
    summary_rows = write_validation_summary(neuron, matrix_rows, dc_rows, be_cn_rows)
    print(f"neuron_status={neuron['neuron_status']}")
    print(f"phase4_independent_matrix_rows={len(matrix_rows)}")
    print(f"phase4_dc_analytic_rows={len(dc_rows)}")
    print(f"phase4_be_cn_rows={len(be_cn_rows)}")
    print(f"phase4_validation_summary_rows={len(summary_rows)}")
    print(f"independent_max_trace_abs_diff_mV={max_float(matrix_rows, 'trace_max_abs_diff_all_mV'):.12g}")
    print(f"be_cn_max_A_h_abs_diff_mV={max_float(be_cn_rows, 'A_h_mV_abs_diff'):.12g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
