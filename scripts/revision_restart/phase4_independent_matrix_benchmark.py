"""Restart Phase 4 independent passive-circuit benchmarks.

This module intentionally reimplements the manuscript three-compartment
passive circuit without importing the production passive solver or matrix
assembly. It reads configuration/source values, assembles the direct matrices
locally, and compares the result with existing SPINE Phase 02 trace outputs.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
import math
from pathlib import Path
import tomllib
from typing import Iterable

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs" / "manuscript_faithful" / "baseline.toml"
PHASE2 = ROOT / "results" / "phase02"
OUT = ROOT / "results" / "revision_restart" / "phase4"
DIAGNOSTICS = OUT / "diagnostic_figures"

TRACE_FILES = {
    "low": PHASE2 / "Figure2_low_trace.csv",
    "intermediate": PHASE2 / "Figure2_intermediate_trace.csv",
    "high": PHASE2 / "Figure2_high_trace.csv",
}


@dataclass(frozen=True)
class IndependentParams:
    leak_reversal_V: float
    synaptic_reversal_V: float
    c_head_F: float
    c_dendrite_F: float
    c_soma_F: float
    g_leak_head_S: float
    g_leak_dendrite_S: float
    g_leak_soma_S: float
    g_dendrite_soma_S: float
    intracellular_resistivity_ohm_cm: float
    syn_g_max_S: float
    syn_tau_rise_s: float
    syn_tau_decay_s: float
    syn_event_time_s: float
    dt_s: float
    stop_s: float
    metric_window_s: float
    input_resistance_current_A: float


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        keys: list[str] = []
        for row in rows:
            for key in row:
                if key not in keys:
                    keys.append(key)
        fieldnames = keys
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def mV_to_V(value: float) -> float:
    return value * 1e-3


def V_to_mV(value: float) -> float:
    return value * 1e3


def nS_to_S(value: float) -> float:
    return value * 1e-9


def pF_to_F(value: float) -> float:
    return value * 1e-12


def pA_to_A(value: float) -> float:
    return value * 1e-12


def ms_to_s(value: float) -> float:
    return value * 1e-3


def ohm_to_Mohm(value: float) -> float:
    return value / 1e6


def load_independent_params(config_path: Path = CONFIG) -> IndependentParams:
    with config_path.open("rb") as handle:
        data = tomllib.load(handle)

    head_radius_um = float(data["spine_head"]["radius_um"])
    head_area_um2 = 4.0 * math.pi * head_radius_um * head_radius_um
    c_head_pF = float(data["spine_head"]["specific_capacitance_pF_per_um2"]) * head_area_um2
    g_head_nS = float(data["spine_head"]["specific_leak_nS_per_um2"]) * head_area_um2

    return IndependentParams(
        leak_reversal_V=mV_to_V(float(data["reversal"]["leak_mV"])),
        synaptic_reversal_V=mV_to_V(float(data["reversal"]["excitatory_synapse_mV"])),
        c_head_F=pF_to_F(c_head_pF),
        c_dendrite_F=pF_to_F(float(data["dendrite"]["capacitance_pF"])),
        c_soma_F=pF_to_F(float(data["soma"]["capacitance_pF"])),
        g_leak_head_S=nS_to_S(g_head_nS),
        g_leak_dendrite_S=nS_to_S(float(data["dendrite"]["leak_conductance_nS"])),
        g_leak_soma_S=nS_to_S(float(data["soma"]["leak_conductance_nS"])),
        g_dendrite_soma_S=nS_to_S(float(data["coupling"]["dendrite_soma_conductance_nS"])),
        intracellular_resistivity_ohm_cm=float(data["coupling"]["intracellular_resistivity_ohm_cm"]),
        syn_g_max_S=nS_to_S(float(data["synapse"]["g_max_nS"])),
        syn_tau_rise_s=ms_to_s(float(data["synapse"]["tau_rise_ms"])),
        syn_tau_decay_s=ms_to_s(float(data["synapse"]["tau_decay_ms"])),
        syn_event_time_s=ms_to_s(float(data["synapse"]["event_time_ms"])),
        dt_s=ms_to_s(float(data["numerics"]["time_step_ms"])),
        stop_s=ms_to_s(float(data["numerics"]["simulation_stop_ms"])),
        metric_window_s=ms_to_s(float(data["numerics"]["metric_window_ms"])),
        input_resistance_current_A=pA_to_A(float(data["numerics"]["input_resistance_current_pA"])),
    )


def neck_resistance_ohm(resistivity_ohm_cm: float, length_um: float, radius_um: float) -> float:
    length_cm = length_um * 1e-4
    radius_cm = radius_um * 1e-4
    return resistivity_ohm_cm * length_cm / (math.pi * radius_cm * radius_cm)


def synaptic_eta(params: IndependentParams) -> float:
    tr = params.syn_tau_rise_s
    td = params.syn_tau_decay_s
    peak_delay_s = tr * td / (td - tr) * math.log(td / tr)
    peak_value = math.exp(-peak_delay_s / td) - math.exp(-peak_delay_s / tr)
    return 1.0 / peak_value


def synaptic_conductance(times_s: np.ndarray, params: IndependentParams) -> np.ndarray:
    dt = times_s - params.syn_event_time_s
    values = np.zeros_like(times_s, dtype=float)
    mask = dt >= 0.0
    eta = synaptic_eta(params)
    values[mask] = params.syn_g_max_S * eta * (
        np.exp(-dt[mask] / params.syn_tau_decay_s)
        - np.exp(-dt[mask] / params.syn_tau_rise_s)
    )
    return values


def assemble_direct_matrix(
    params: IndependentParams, neck_conductance_S: float, synaptic_conductance_S: float
) -> tuple[np.ndarray, np.ndarray]:
    glh = params.g_leak_head_S
    gld = params.g_leak_dendrite_S
    gls = params.g_leak_soma_S
    gds = params.g_dendrite_soma_S
    e_l = params.leak_reversal_V
    e_syn = params.synaptic_reversal_V
    matrix = np.array(
        [
            [glh + synaptic_conductance_S + neck_conductance_S, -neck_conductance_S, 0.0],
            [-neck_conductance_S, gld + neck_conductance_S + gds, -gds],
            [0.0, -gds, gls + gds],
        ],
        dtype=float,
    )
    source = np.array([glh * e_l + synaptic_conductance_S * e_syn, gld * e_l, gls * e_l])
    return matrix, source


def simulate_direct(
    params: IndependentParams,
    neck_resistance_value_ohm: float,
    method: str = "backward_euler",
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    times = np.arange(0.0, params.stop_s + 0.5 * params.dt_s, params.dt_s)
    voltages = np.empty((len(times), 3), dtype=float)
    voltages[0, :] = params.leak_reversal_V
    g_syn = synaptic_conductance(times, params)
    capacitance = np.diag([params.c_head_F, params.c_dendrite_F, params.c_soma_F])
    c_over_dt = capacitance / params.dt_s
    g_neck = 1.0 / neck_resistance_value_ohm
    previous_matrix, previous_source = assemble_direct_matrix(params, g_neck, float(g_syn[0]))
    for i in range(1, len(times)):
        current_matrix, current_source = assemble_direct_matrix(params, g_neck, float(g_syn[i]))
        if method == "backward_euler":
            lhs = c_over_dt + current_matrix
            rhs = c_over_dt @ voltages[i - 1] + current_source
        elif method == "crank_nicolson":
            lhs = c_over_dt + 0.5 * current_matrix
            rhs = (
                (c_over_dt - 0.5 * previous_matrix) @ voltages[i - 1]
                + 0.5 * (previous_source + current_source)
            )
        else:
            raise ValueError(f"unsupported independent method: {method}")
        voltages[i, :] = np.linalg.solve(lhs, rhs)
        previous_matrix = current_matrix
        previous_source = current_source
    return times, voltages, g_syn


def dendritic_input_resistance_formula_ohm(params: IndependentParams) -> float:
    gld = params.g_leak_dendrite_S
    gls = params.g_leak_soma_S
    gds = params.g_dendrite_soma_S
    determinant = gld * gls + gld * gds + gls * gds
    return (gls + gds) / determinant


def dendritic_input_resistance_solve_ohm(params: IndependentParams) -> float:
    matrix = np.array(
        [
            [params.g_leak_dendrite_S + params.g_dendrite_soma_S, -params.g_dendrite_soma_S],
            [-params.g_dendrite_soma_S, params.g_leak_soma_S + params.g_dendrite_soma_S],
        ]
    )
    rhs = np.array([params.input_resistance_current_A, 0.0])
    delta_v = np.linalg.solve(matrix, rhs)
    return float(delta_v[0] / params.input_resistance_current_A)


def attached_input_resistance_matrix_ohm(params: IndependentParams, neck_resistance_value_ohm: float) -> float:
    g_neck = 1.0 / neck_resistance_value_ohm
    matrix = np.array(
        [
            [params.g_leak_head_S + g_neck, -g_neck, 0.0],
            [-g_neck, params.g_leak_dendrite_S + g_neck + params.g_dendrite_soma_S, -params.g_dendrite_soma_S],
            [0.0, -params.g_dendrite_soma_S, params.g_leak_soma_S + params.g_dendrite_soma_S],
        ]
    )
    rhs = np.array([0.0, params.input_resistance_current_A, 0.0])
    delta_v = np.linalg.solve(matrix, rhs)
    return float(delta_v[1] / params.input_resistance_current_A)


def attached_input_resistance_formula_ohm(params: IndependentParams, neck_resistance_value_ohm: float) -> float:
    omitted = dendritic_input_resistance_formula_ohm(params)
    g_neck = 1.0 / neck_resistance_value_ohm
    head_branch_admittance = g_neck * params.g_leak_head_S / (g_neck + params.g_leak_head_S)
    return 1.0 / (1.0 / omitted + head_branch_admittance)


def compute_metrics(times_s: np.ndarray, voltages_V: np.ndarray, params: IndependentParams) -> dict[str, float]:
    mask = (times_s >= params.syn_event_time_s) & (
        times_s <= params.syn_event_time_s + params.metric_window_s
    )
    window_times = times_s[mask]
    window_voltages = voltages_V[mask, :]
    baseline_index = int(np.searchsorted(times_s, params.syn_event_time_s))
    baseline = voltages_V[baseline_index, :]
    out: dict[str, float] = {}
    amplitudes: list[float] = []
    peak_times: list[float] = []
    for index, label in enumerate(("h", "d", "s")):
        depol = window_voltages[:, index] - baseline[index]
        peak_index = int(np.argmax(depol))
        amplitude = float(depol[peak_index])
        peak_time = float(window_times[peak_index] - window_times[0])
        amplitudes.append(amplitude)
        peak_times.append(peak_time)
        out[f"A_{label}_mV"] = V_to_mV(amplitude)
        out[f"peak_time_{label}_ms"] = peak_time * 1e3
        out[f"final_V_{label}_mV"] = V_to_mV(float(voltages_V[-1, index]))
    out["Gamma_h_to_d"] = amplitudes[1] / amplitudes[0] if amplitudes[0] else float("nan")
    out["Gamma_h_to_s"] = amplitudes[2] / amplitudes[0] if amplitudes[0] else float("nan")
    out["Gamma_d_to_s"] = amplitudes[2] / amplitudes[1] if amplitudes[1] else float("nan")
    return out


def read_spine_trace(condition: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows = read_csv_dicts(TRACE_FILES[condition])
    times = np.array([float(row["time_ms"]) * 1e-3 for row in rows], dtype=float)
    voltages = np.array(
        [
            [mV_to_V(float(row["V_h_mV"])), mV_to_V(float(row["V_d_mV"])), mV_to_V(float(row["V_s_mV"]))]
            for row in rows
        ],
        dtype=float,
    )
    g_syn = np.array([float(row["g_syn_nS"]) * 1e-9 for row in rows], dtype=float)
    return times, voltages, g_syn


def trace_differences_mV(
    independent_times: np.ndarray,
    independent_voltages: np.ndarray,
    spine_times: np.ndarray,
    spine_voltages: np.ndarray,
) -> dict[str, float]:
    if len(independent_times) == len(spine_times) and np.max(np.abs(independent_times - spine_times)) < 1e-14:
        aligned = spine_voltages
    else:
        aligned = np.column_stack(
            [np.interp(independent_times, spine_times, spine_voltages[:, i]) for i in range(3)]
        )
    diff_mV = (independent_voltages - aligned) * 1e3
    out = {}
    for index, label in enumerate(("h", "d", "s")):
        out[f"trace_RMSE_{label}_mV"] = float(np.sqrt(np.mean(diff_mV[:, index] ** 2)))
        out[f"trace_max_abs_diff_{label}_mV"] = float(np.max(np.abs(diff_mV[:, index])))
    out["trace_RMSE_all_mV"] = float(np.sqrt(np.mean(diff_mV**2)))
    out["trace_max_abs_diff_all_mV"] = float(np.max(np.abs(diff_mV)))
    return out


def relative_diff(value: float, reference: float) -> float:
    return abs(value - reference) / abs(reference) if reference else float("nan")


def metric_comparison_columns(metric: str, independent: dict[str, float], spine: dict[str, float]) -> dict[str, float]:
    bench = independent[metric]
    ref = spine[metric]
    return {
        f"benchmark_{metric}": bench,
        f"spine_{metric}": ref,
        f"{metric}_abs_diff": abs(bench - ref),
        f"{metric}_rel_diff": relative_diff(bench, ref),
    }


def target_rows() -> list[dict[str, str]]:
    summary_path = PHASE2 / "Figure2_representative_summary.csv"
    rows = read_csv_dicts(summary_path)
    order = {"low": 0, "intermediate": 1, "high": 2}
    return sorted(rows, key=lambda row: order.get(row["condition"], 99))


def run_independent_matrix_benchmark() -> list[dict[str, object]]:
    params = load_independent_params()
    rows: list[dict[str, object]] = []
    trace_payloads: list[tuple[str, np.ndarray, np.ndarray, np.ndarray]] = []
    for target in target_rows():
        condition = target["condition"]
        length_um = float(target["neck_length_um"])
        radius_um = float(target["neck_radius_um"])
        r_neck = neck_resistance_ohm(params.intracellular_resistivity_ohm_cm, length_um, radius_um)
        r_in_d = dendritic_input_resistance_formula_ohm(params)
        smi_value = r_neck / r_in_d
        gamma_divider = 1.0 / (1.0 + smi_value)

        times, voltages, g_syn = simulate_direct(params, r_neck, method="backward_euler")
        bench_metrics = compute_metrics(times, voltages, params)
        spine_times, spine_voltages, spine_g_syn = read_spine_trace(condition)
        spine_metrics = compute_metrics(spine_times, spine_voltages, params)
        diff = trace_differences_mV(times, voltages, spine_times, spine_voltages)
        syn_diff_nS = float(np.max(np.abs(g_syn - spine_g_syn)) * 1e9)

        row: dict[str, object] = {
            "condition": condition,
            "neck_length_um": length_um,
            "neck_radius_um": radius_um,
            "neck_resistance_Mohm": ohm_to_Mohm(r_neck),
            "R_in_d_Mohm": ohm_to_Mohm(r_in_d),
            "SMI": smi_value,
            "Gamma_divider": gamma_divider,
            "benchmark_residual": bench_metrics["Gamma_h_to_d"] - gamma_divider,
            "spine_residual": spine_metrics["Gamma_h_to_d"] - gamma_divider,
            "residual_abs_diff": abs(
                (bench_metrics["Gamma_h_to_d"] - gamma_divider)
                - (spine_metrics["Gamma_h_to_d"] - gamma_divider)
            ),
            "max_synaptic_conductance_abs_diff_nS": syn_diff_nS,
            "benchmark_engine": "independent direct-matrix backward Euler",
            "comparison_source": str(TRACE_FILES[condition].relative_to(ROOT)),
        }
        for metric in (
            "A_h_mV",
            "A_d_mV",
            "A_s_mV",
            "Gamma_h_to_d",
            "Gamma_h_to_s",
            "peak_time_h_ms",
            "peak_time_d_ms",
            "peak_time_s_ms",
            "final_V_h_mV",
            "final_V_d_mV",
            "final_V_s_mV",
        ):
            row.update(metric_comparison_columns(metric, bench_metrics, spine_metrics))
        row.update(diff)
        rows.append(row)
        trace_payloads.append((condition, times, voltages, spine_voltages))

    write_csv(OUT / "phase4_independent_matrix_benchmark.csv", rows)
    write_trace_overlay_svg(trace_payloads)
    return rows


def run_dc_analytic_benchmark() -> list[dict[str, object]]:
    params = load_independent_params()
    rows: list[dict[str, object]] = []
    r_in_formula = dendritic_input_resistance_formula_ohm(params)
    r_in_solve = dendritic_input_resistance_solve_ohm(params)
    rows.append(
        {
            "benchmark_case": "spine_omitted_dendrite_soma_input_resistance",
            "condition": "two_node_load",
            "quantity": "R_in_d",
            "input_description": "closed-form two-node dendrite-soma DC load",
            "expected_value": ohm_to_Mohm(r_in_formula),
            "computed_value": ohm_to_Mohm(r_in_solve),
            "absolute_error": ohm_to_Mohm(abs(r_in_formula - r_in_solve)),
            "relative_error": relative_diff(r_in_solve, r_in_formula),
            "units": "MOhm",
            "interpretation": "validates the omitted-spine DC load formula used by SMI",
            "omitted_R_in_d_Mohm": ohm_to_Mohm(r_in_formula),
            "attached_R_in_d_Mohm": "",
            "SMI": "",
            "neck_resistance_Mohm": "",
        }
    )

    for target in target_rows():
        condition = target["condition"]
        r_neck = neck_resistance_ohm(
            params.intracellular_resistivity_ohm_cm,
            float(target["neck_length_um"]),
            float(target["neck_radius_um"]),
        )
        smi_value = r_neck / r_in_formula
        gamma = 1.0 / (1.0 + smi_value)
        rows.append(
            {
                "benchmark_case": "dc_divider_prediction",
                "condition": condition,
                "quantity": "Gamma_divider",
                "input_description": "1/(1+SMI) from R_neck/R_in,d",
                "expected_value": gamma,
                "computed_value": r_in_formula / (r_in_formula + r_neck),
                "absolute_error": abs(gamma - r_in_formula / (r_in_formula + r_neck)),
                "relative_error": 0.0,
                "units": "dimensionless",
                "interpretation": "algebraic DC divider reference, not a transient peak prediction",
                "omitted_R_in_d_Mohm": ohm_to_Mohm(r_in_formula),
                "attached_R_in_d_Mohm": "",
                "SMI": smi_value,
                "neck_resistance_Mohm": ohm_to_Mohm(r_neck),
            }
        )

        attached_formula = attached_input_resistance_formula_ohm(params, r_neck)
        attached_matrix = attached_input_resistance_matrix_ohm(params, r_neck)
        rows.append(
            {
                "benchmark_case": "attached_versus_omitted_one_port",
                "condition": condition,
                "quantity": "R_in_d_attached",
                "input_description": "passive head leak branch attached through neck at DC",
                "expected_value": ohm_to_Mohm(attached_formula),
                "computed_value": ohm_to_Mohm(attached_matrix),
                "absolute_error": ohm_to_Mohm(abs(attached_matrix - attached_formula)),
                "relative_error": relative_diff(attached_matrix, attached_formula),
                "units": "MOhm",
                "interpretation": "attached one-port differs negligibly in this compact passive-head model",
                "omitted_R_in_d_Mohm": ohm_to_Mohm(r_in_formula),
                "attached_R_in_d_Mohm": ohm_to_Mohm(attached_matrix),
                "attached_minus_omitted_Mohm": ohm_to_Mohm(attached_matrix - r_in_formula),
                "attached_minus_omitted_relative": (attached_matrix - r_in_formula) / r_in_formula,
                "SMI": smi_value,
                "neck_resistance_Mohm": ohm_to_Mohm(r_neck),
            }
        )

    for ratio, expected, case_name in (
        (1e-9, 1.0, "zero_neck_resistance_high_coupling_limit"),
        (1e9, 0.0, "very_large_neck_resistance_limit"),
    ):
        computed = 1.0 / (1.0 + ratio)
        rows.append(
            {
                "benchmark_case": case_name,
                "condition": "limiting_case",
                "quantity": "Gamma_divider",
                "input_description": f"SMI={ratio:g}",
                "expected_value": expected,
                "computed_value": computed,
                "absolute_error": abs(computed - expected),
                "relative_error": "" if expected == 0.0 else relative_diff(computed, expected),
                "units": "dimensionless",
                "interpretation": "validates algebraic limiting behavior of the divider relation",
                "omitted_R_in_d_Mohm": ohm_to_Mohm(r_in_formula),
                "attached_R_in_d_Mohm": "",
                "SMI": ratio,
                "neck_resistance_Mohm": ohm_to_Mohm(ratio * r_in_formula),
            }
        )

    write_csv(OUT / "phase4_dc_analytic_benchmark.csv", rows)
    return rows


def scale_points(values: Iterable[float], low: float, high: float, out_low: float, out_high: float) -> list[float]:
    vals = list(values)
    if high == low:
        return [0.5 * (out_low + out_high) for _ in vals]
    return [out_low + (value - low) / (high - low) * (out_high - out_low) for value in vals]


def polyline(points: list[tuple[float, float]], color: str, width: float, dash: bool = False) -> str:
    coords = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    dash_attr = ' stroke-dasharray="5 4"' if dash else ""
    return f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width}"{dash_attr}/>'


def write_trace_overlay_svg(
    payloads: list[tuple[str, np.ndarray, np.ndarray, np.ndarray]],
    path: Path = DIAGNOSTICS / "phase4_independent_trace_overlay.svg",
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    width = 880
    height = 620
    panel_w = 250
    panel_h = 135
    lefts = [55, 315, 575]
    top = 95
    colors = {"h": "#1f77b4", "d": "#d62728", "s": "#2ca02c"}
    labels = ("h", "d", "s")
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="880" height="620" viewBox="0 0 880 620">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="34" y="34" font-family="Arial" font-size="18">Phase 4 diagnostic: independent matrix benchmark versus SPINE traces</text>',
        '<text x="34" y="58" font-family="Arial" font-size="12">Solid: independent direct matrix benchmark. Dashed: existing SPINE Phase 02 trace CSV. Diagnostic only.</text>',
    ]
    for panel_index, (condition, times, independent_v, spine_v) in enumerate(payloads):
        left = lefts[panel_index]
        all_mV = np.concatenate([independent_v.reshape(-1), spine_v.reshape(-1)]) * 1e3
        ymin = float(np.min(all_mV))
        ymax = float(np.max(all_mV))
        pad = max(0.2, 0.08 * (ymax - ymin))
        ymin -= pad
        ymax += pad
        x_values = scale_points(times * 1e3, 0.0, float(times[-1] * 1e3), left, left + panel_w)
        parts.append(f'<text x="{left}" y="{top - 14}" font-family="Arial" font-size="14">{condition}</text>')
        parts.append(f'<rect x="{left}" y="{top}" width="{panel_w}" height="{panel_h}" fill="#fafafa" stroke="#999"/>')
        parts.append(f'<text x="{left}" y="{top + panel_h + 28}" font-family="Arial" font-size="11">time (ms)</text>')
        parts.append(
            f'<text x="{left - 34}" y="{top + 12}" font-family="Arial" font-size="11" transform="rotate(-90 {left - 34},{top + 12})">mV</text>'
        )
        stride = max(1, len(times) // 450)
        for comp_index, label in enumerate(labels):
            y_ind = scale_points(independent_v[:, comp_index] * 1e3, ymin, ymax, top + panel_h, top)
            y_spine = scale_points(spine_v[:, comp_index] * 1e3, ymin, ymax, top + panel_h, top)
            ind_points = list(zip(x_values[::stride], y_ind[::stride]))
            spine_points = list(zip(x_values[::stride], y_spine[::stride]))
            parts.append(polyline(ind_points, colors[label], 1.6, dash=False))
            parts.append(polyline(spine_points, colors[label], 1.0, dash=True))
    legend_y = 330
    parts.append('<text x="55" y="330" font-family="Arial" font-size="13">Legend</text>')
    x0 = 55
    for offset, label in enumerate(labels):
        y = legend_y + 26 + 22 * offset
        color = colors[label]
        parts.append(f'<line x1="{x0}" y1="{y}" x2="{x0 + 36}" y2="{y}" stroke="{color}" stroke-width="2"/>')
        parts.append(f'<text x="{x0 + 46}" y="{y + 4}" font-family="Arial" font-size="12">independent V_{label}</text>')
        parts.append(
            f'<line x1="{x0 + 180}" y1="{y}" x2="{x0 + 216}" y2="{y}" stroke="{color}" stroke-width="1.5" stroke-dasharray="5 4"/>'
        )
        parts.append(f'<text x="{x0 + 226}" y="{y + 4}" font-family="Arial" font-size="12">SPINE V_{label}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")
    return path


def main() -> int:
    matrix_rows = run_independent_matrix_benchmark()
    dc_rows = run_dc_analytic_benchmark()
    max_trace_diff = max(float(row["trace_max_abs_diff_all_mV"]) for row in matrix_rows)
    print(f"phase4_independent_matrix_rows={len(matrix_rows)}")
    print(f"phase4_dc_analytic_rows={len(dc_rows)}")
    print(f"phase4_independent_max_trace_abs_diff_mV={max_trace_diff:.12g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
