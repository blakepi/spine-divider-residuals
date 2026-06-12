"""Phase 02 manuscript-reproduction protocols."""

from __future__ import annotations

import csv
from dataclasses import asdict, replace
from pathlib import Path
import statistics
from typing import Iterable

import numpy as np

from spine.config import load_config
from spine.geometry import cylindrical_neck_resistance_ohm
from spine.impedance import dendritic_input_resistance_ohm, smi
from spine.metrics import compute_voltage_metrics
from spine.passive import (
    PassiveParameters,
    parameters_from_config,
    simulate_three_compartment,
    simulate_with_neck_resistance,
)
from spine.units import S_to_nS, V_to_mV, ohm_to_megaohm, s_to_ms


TRACE_TARGETS = [
    {
        "condition": "low",
        "neck_length_um": 0.25,
        "neck_radius_um": 0.25,
        "reported_smi": 0.01,
        "reported_gamma_hd": 0.984,
        "reported_gamma_hs": 0.357,
    },
    {
        "condition": "intermediate",
        "neck_length_um": 0.75,
        "neck_radius_um": 0.12,
        "reported_smi": 0.11,
        "reported_gamma_hd": 0.751,
        "reported_gamma_hs": 0.272,
    },
    {
        "condition": "high",
        "neck_length_um": 1.50,
        "neck_radius_um": 0.05,
        "reported_smi": 1.32,
        "reported_gamma_hd": 0.102,
        "reported_gamma_hs": 0.038,
    },
]


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _relative_error(value: float, target: float) -> float:
    return abs(value - target) / abs(target) if target != 0 else float("nan")


def _classification(abs_error: float, rel_error: float) -> str:
    if abs_error <= 0.005 or rel_error <= 0.02:
        return "exact reproduction"
    if abs_error <= 0.05 or rel_error <= 0.20:
        return "approximate reproduction"
    return "failed reproduction"


def _metric_row(
    condition: str,
    metric: str,
    reproduced: float,
    reported: float,
    unit: str,
) -> dict[str, object]:
    abs_error = abs(reproduced - reported)
    rel_error = _relative_error(reproduced, reported)
    return {
        "figure": "Figure 2",
        "condition": condition,
        "metric": metric,
        "reported_value": reported,
        "reproduced_value": reproduced,
        "absolute_error": abs_error,
        "relative_error": rel_error,
        "unit": unit,
        "classification": _classification(abs_error, rel_error),
    }


def _rankdata(values: Iterable[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(indexed)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        rank = 0.5 * (i + j) + 1.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = rank
        i = j + 1
    return ranks


def _pearson(x: Iterable[float], y: Iterable[float]) -> float:
    xs = list(x)
    ys = list(y)
    mx = statistics.fmean(xs)
    my = statistics.fmean(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    den_x = sum((a - mx) ** 2 for a in xs)
    den_y = sum((b - my) ** 2 for b in ys)
    if den_x == 0.0 or den_y == 0.0:
        return float("nan")
    return num / (den_x * den_y) ** 0.5


def _spearman(x: Iterable[float], y: Iterable[float]) -> float:
    return _pearson(_rankdata(x), _rankdata(y))


def _svg_polyline(points: list[tuple[float, float]], color: str, width: float = 1.8) -> str:
    data = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    return f'<polyline points="{data}" fill="none" stroke="{color}" stroke-width="{width}"/>'


def _scale(values: list[float], low: float, high: float, out_low: float, out_high: float) -> list[float]:
    if high == low:
        return [0.5 * (out_low + out_high) for _ in values]
    return [out_low + (value - low) / (high - low) * (out_high - out_low) for value in values]


def _write_trace_svg(path: Path, trace_rows: list[dict[str, object]], title: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    t = [float(row["time_ms"]) for row in trace_rows]
    vh = [float(row["V_h_mV"]) for row in trace_rows]
    vd = [float(row["V_d_mV"]) for row in trace_rows]
    vs = [float(row["V_s_mV"]) for row in trace_rows]
    width = 720
    height = 260
    left = 58
    right = 20
    top = 30
    bottom = 44
    x = _scale(t, min(t), max(t), left, width - right)
    y_min = min(min(vh), min(vd), min(vs))
    y_max = max(max(vh), max(vd), max(vs))
    y = lambda vals: _scale(vals, y_min, y_max, height - bottom, top)
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{left}" y="20" font-family="Arial" font-size="14">{title}</text>',
        f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="black"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="black"/>',
        _svg_polyline(list(zip(x, y(vh))), "#1f77b4"),
        _svg_polyline(list(zip(x, y(vd))), "#d62728"),
        _svg_polyline(list(zip(x, y(vs))), "#2ca02c"),
        f'<text x="{width-155}" y="45" font-family="Arial" font-size="12" fill="#1f77b4">Vh</text>',
        f'<text x="{width-155}" y="62" font-family="Arial" font-size="12" fill="#d62728">Vd</text>',
        f'<text x="{width-155}" y="79" font-family="Arial" font-size="12" fill="#2ca02c">Vs</text>',
        f'<text x="{width/2-35}" y="{height-12}" font-family="Arial" font-size="12">Time (ms)</text>',
        f'<text x="12" y="{height/2}" font-family="Arial" font-size="12" transform="rotate(-90 12,{height/2})">Voltage (mV)</text>',
        f'<text x="{left}" y="{height-28}" font-family="Arial" font-size="10">{min(t):.0f}</text>',
        f'<text x="{width-right-25}" y="{height-28}" font-family="Arial" font-size="10">{max(t):.0f}</text>',
        f'<text x="5" y="{top+4}" font-family="Arial" font-size="10">{y_max:.2f}</text>',
        f'<text x="5" y="{height-bottom}" font-family="Arial" font-size="10">{y_min:.2f}</text>',
        "</svg>",
    ]
    path.write_text("\n".join(svg), encoding="utf-8")
    return path


def _write_scatter_svg(
    path: Path,
    points: list[tuple[float, float]],
    title: str,
    x_label: str,
    y_label: str,
    color: str = "#1f77b4",
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    width = 540
    height = 360
    left = 64
    right = 24
    top = 32
    bottom = 54
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    x_scaled = _scale(xs, min(xs), max(xs), left, width - right)
    y_scaled = _scale(ys, min(ys), max(ys), height - bottom, top)
    circles = [
        f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.6" fill="{color}" fill-opacity="0.75"/>'
        for x, y in zip(x_scaled, y_scaled)
    ]
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{left}" y="22" font-family="Arial" font-size="14">{title}</text>',
        f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="black"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="black"/>',
        *circles,
        f'<text x="{width/2-60}" y="{height-14}" font-family="Arial" font-size="12">{x_label}</text>',
        f'<text x="14" y="{height/2}" font-family="Arial" font-size="12" transform="rotate(-90 14,{height/2})">{y_label}</text>',
        f'<text x="{left}" y="{height-34}" font-family="Arial" font-size="10">{min(xs):.3g}</text>',
        f'<text x="{width-right-42}" y="{height-34}" font-family="Arial" font-size="10">{max(xs):.3g}</text>',
        f'<text x="8" y="{top+4}" font-family="Arial" font-size="10">{max(ys):.3g}</text>',
        f'<text x="8" y="{height-bottom}" font-family="Arial" font-size="10">{min(ys):.3g}</text>',
        "</svg>",
    ]
    path.write_text("\n".join(svg), encoding="utf-8")
    return path


def _write_heatmap_svg(
    path: Path,
    rows: list[dict[str, object]],
    value_key: str,
    title: str,
    x_key: str = "neck_radius_um",
    y_key: str = "neck_length_um",
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    xs = sorted({float(row[x_key]) for row in rows})
    ys = sorted({float(row[y_key]) for row in rows})
    values = {(float(row[x_key]), float(row[y_key])): float(row[value_key]) for row in rows}
    v_min = min(values.values())
    v_max = max(values.values())
    cell = 18
    left = 78
    top = 36
    width = left + cell * len(xs) + 80
    height = top + cell * len(ys) + 68

    def color(value: float) -> str:
        f = 0.0 if v_max == v_min else (value - v_min) / (v_max - v_min)
        r = int(245 * f + 30 * (1 - f))
        g = int(235 * (1 - abs(f - 0.5) * 1.6))
        b = int(220 * (1 - f) + 40 * f)
        return f"rgb({r},{max(0, min(255, g))},{b})"

    rects = []
    for j, yv in enumerate(reversed(ys)):
        for i, xv in enumerate(xs):
            val = values[(xv, yv)]
            rects.append(
                f'<rect x="{left+i*cell}" y="{top+j*cell}" width="{cell}" height="{cell}" fill="{color(val)}"/>'
            )
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{left}" y="22" font-family="Arial" font-size="14">{title}</text>',
        *rects,
        f'<rect x="{left}" y="{top}" width="{cell*len(xs)}" height="{cell*len(ys)}" fill="none" stroke="black"/>',
        f'<text x="{left+cell*len(xs)/2-60}" y="{height-18}" font-family="Arial" font-size="12">neck radius (um)</text>',
        f'<text x="16" y="{top+cell*len(ys)/2+45}" font-family="Arial" font-size="12" transform="rotate(-90 16,{top+cell*len(ys)/2+45})">neck length (um)</text>',
        f'<text x="{left}" y="{height-38}" font-family="Arial" font-size="10">{min(xs):.3g}</text>',
        f'<text x="{left+cell*len(xs)-34}" y="{height-38}" font-family="Arial" font-size="10">{max(xs):.3g}</text>',
        f'<text x="{left-46}" y="{top+cell*len(ys)}" font-family="Arial" font-size="10">{min(ys):.3g}</text>',
        f'<text x="{left-46}" y="{top+8}" font-family="Arial" font-size="10">{max(ys):.3g}</text>',
        f'<text x="{left+cell*len(xs)+12}" y="{top+14}" font-family="Arial" font-size="10">max {v_max:.3g}</text>',
        f'<text x="{left+cell*len(xs)+12}" y="{top+cell*len(ys)}" font-family="Arial" font-size="10">min {v_min:.3g}</text>',
        "</svg>",
    ]
    path.write_text("\n".join(svg), encoding="utf-8")
    return path


def _write_architecture_svg(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="760" height="300" viewBox="0 0 760 300">
<rect width="100%" height="100%" fill="white"/>
<text x="30" y="28" font-family="Arial" font-size="16">SPINE manuscript-faithful architecture</text>
<circle cx="145" cy="145" r="45" fill="#d9ecff" stroke="#1f77b4" stroke-width="2"/>
<text x="117" y="150" font-family="Arial" font-size="14">head h</text>
<line x1="190" y1="145" x2="345" y2="145" stroke="#333" stroke-width="5"/>
<text x="215" y="126" font-family="Arial" font-size="13">R_neck = rho_i L_n/(pi r_n^2)</text>
<text x="250" y="169" font-family="Arial" font-size="13">g_hd = 1/R_neck</text>
<rect x="345" y="105" width="130" height="80" rx="4" fill="#fde0dd" stroke="#d62728" stroke-width="2"/>
<text x="374" y="150" font-family="Arial" font-size="14">dendrite d</text>
<line x1="475" y1="145" x2="585" y2="145" stroke="#333" stroke-width="4"/>
<text x="505" y="126" font-family="Arial" font-size="13">g_DS</text>
<circle cx="645" cy="145" r="50" fill="#dcf5d6" stroke="#2ca02c" stroke-width="2"/>
<text x="622" y="150" font-family="Arial" font-size="14">soma s</text>
<path d="M110 70 C125 40 165 40 180 70" fill="none" stroke="#9467bd" stroke-width="3"/>
<text x="68" y="62" font-family="Arial" font-size="13">g_syn(t), E_syn</text>
<text x="295" y="230" font-family="Arial" font-size="13">SMI = R_neck/R_in,d; R_in,d measured with stimulated spine omitted</text>
</svg>"""
    path.write_text(svg, encoding="utf-8")
    return path


def _simulate_condition(parameters: PassiveParameters, length_um: float, radius_um: float) -> tuple[object, object, float]:
    result = simulate_three_compartment(parameters, length_um, radius_um)
    metrics = compute_voltage_metrics(result)
    rin = dendritic_input_resistance_ohm(parameters).steady_state_ohm
    condition_smi = smi(result.neck_resistance_ohm, rin)
    return result, metrics, condition_smi


def _trace_rows(result, condition: str) -> list[dict[str, object]]:
    rows = []
    for time_s, voltage, g_syn in zip(result.time_s, result.voltage_V, result.g_syn_S):
        rows.append(
            {
                "condition": condition,
                "time_ms": s_to_ms(float(time_s)),
                "V_h_mV": V_to_mV(float(voltage[0])),
                "V_d_mV": V_to_mV(float(voltage[1])),
                "V_s_mV": V_to_mV(float(voltage[2])),
                "g_syn_nS": S_to_nS(float(g_syn)),
            }
        )
    return rows


def _summary_row(condition: str, length_um: float, radius_um: float, result, metrics, condition_smi: float) -> dict[str, object]:
    return {
        "condition": condition,
        "neck_length_um": length_um,
        "neck_radius_um": radius_um,
        "neck_resistance_Mohm": ohm_to_megaohm(result.neck_resistance_ohm),
        "R_in_d_Mohm": ohm_to_megaohm(dendritic_input_resistance_ohm(result.parameters).steady_state_ohm),
        "SMI": condition_smi,
        "A_h_mV": V_to_mV(metrics.amplitude_head_V),
        "A_d_mV": V_to_mV(metrics.amplitude_dendrite_V),
        "A_s_mV": V_to_mV(metrics.amplitude_soma_V),
        "Gamma_h_to_d": metrics.gamma_head_to_dendrite,
        "Gamma_h_to_s": metrics.gamma_head_to_soma,
        "Gamma_d_to_s": metrics.gamma_dendrite_to_soma,
        "latency_h_ms": s_to_ms(metrics.latency_head_s),
        "latency_d_ms": s_to_ms(metrics.latency_dendrite_s),
        "latency_s_ms": s_to_ms(metrics.latency_soma_s),
        "half_width_h_ms": s_to_ms(metrics.half_width_head_s),
        "peak_synaptic_current_pA_signed": metrics.peak_synaptic_current_A * 1e12,
        "integrated_synaptic_current_pC_signed": metrics.integrated_synaptic_current_C * 1e12,
        "peak_neck_current_pA_head_to_dendrite": metrics.peak_neck_current_A * 1e12,
        "dendritic_charge_from_neck_pC": metrics.dendritic_charge_from_neck_C * 1e12,
        "driving_force_reduction_mV": V_to_mV(metrics.driving_force_reduction_V),
    }


def _run_geometry_sweep(parameters: PassiveParameters, lengths: np.ndarray, radii: np.ndarray) -> list[dict[str, object]]:
    rin = dendritic_input_resistance_ohm(parameters).steady_state_ohm
    rows = []
    for length_um in lengths:
        for radius_um in radii:
            result = simulate_three_compartment(parameters, float(length_um), float(radius_um))
            metrics = compute_voltage_metrics(result)
            rows.append(
                {
                    "neck_length_um": float(length_um),
                    "neck_radius_um": float(radius_um),
                    "neck_resistance_Mohm": ohm_to_megaohm(result.neck_resistance_ohm),
                    "R_in_d_Mohm": ohm_to_megaohm(rin),
                    "SMI": smi(result.neck_resistance_ohm, rin),
                    "Gamma_h_to_s": metrics.gamma_head_to_soma,
                    "Gamma_h_to_d": metrics.gamma_head_to_dendrite,
                    "A_h_mV": V_to_mV(metrics.amplitude_head_V),
                    "A_s_mV": V_to_mV(metrics.amplitude_soma_V),
                }
            )
    return rows


def _run_matched_neck(parameters: PassiveParameters, gld_values_nS: np.ndarray, neck_resistance_ohm: float) -> list[dict[str, object]]:
    rows = []
    for gld_nS in gld_values_nS:
        varied = replace(parameters, g_leak_dendrite_S=float(gld_nS) * 1e-9)
        result = simulate_with_neck_resistance(varied, neck_resistance_ohm)
        metrics = compute_voltage_metrics(result)
        rin = dendritic_input_resistance_ohm(varied).steady_state_ohm
        rows.append(
            {
                "g_L_d_nS": float(gld_nS),
                "neck_resistance_Mohm": ohm_to_megaohm(neck_resistance_ohm),
                "R_in_d_Mohm": ohm_to_megaohm(rin),
                "SMI": smi(neck_resistance_ohm, rin),
                "Gamma_h_to_s": metrics.gamma_head_to_soma,
                "Gamma_h_to_d": metrics.gamma_head_to_dendrite,
                "A_h_mV": V_to_mV(metrics.amplitude_head_V),
                "A_s_mV": V_to_mV(metrics.amplitude_soma_V),
            }
        )
    return rows


def _run_convergence(parameters: PassiveParameters) -> list[dict[str, object]]:
    rows = []
    for dt_ms in [0.02, 0.01, 0.005, 0.0025]:
        varied = replace(parameters, dt_s=dt_ms * 1e-3)
        result = simulate_three_compartment(varied, 0.75, 0.12)
        metrics = compute_voltage_metrics(result)
        rows.append(
            {
                "condition": "intermediate",
                "dt_ms": dt_ms,
                "SMI": smi(result.neck_resistance_ohm, dendritic_input_resistance_ohm(varied).steady_state_ohm),
                "A_h_mV": V_to_mV(metrics.amplitude_head_V),
                "Gamma_h_to_d": metrics.gamma_head_to_dendrite,
                "Gamma_h_to_s": metrics.gamma_head_to_soma,
            }
        )
    finest = rows[-1]
    for row in rows:
        for key in ["A_h_mV", "Gamma_h_to_d", "Gamma_h_to_s"]:
            row[f"{key}_abs_diff_vs_0_0025_ms"] = abs(float(row[key]) - float(finest[key]))
    return rows


def run_manuscript_reproduction(
    config_path: str | Path = "configs/manuscript_faithful/baseline.toml",
    results_dir: str | Path = "results/phase02",
    figures_dir: str | Path = "figures/phase02",
) -> dict[str, Path]:
    config = load_config(config_path)
    parameters = parameters_from_config(config)
    results_path = Path(results_dir)
    figures_path = Path(figures_dir)
    results_path.mkdir(parents=True, exist_ok=True)
    figures_path.mkdir(parents=True, exist_ok=True)

    outputs: dict[str, Path] = {}
    _write_architecture_svg(figures_path / "Figure1_architecture.svg")

    summary_rows: list[dict[str, object]] = []
    discrepancy_rows: list[dict[str, object]] = []
    for target in TRACE_TARGETS:
        result, metrics, condition_smi = _simulate_condition(
            parameters, target["neck_length_um"], target["neck_radius_um"]
        )
        trace_rows = _trace_rows(result, target["condition"])
        trace_csv = results_path / f"Figure2_{target['condition']}_trace.csv"
        _write_csv(trace_csv, trace_rows)
        _write_trace_svg(figures_path / f"Figure2_{target['condition']}_trace.svg", trace_rows, f"Figure 2 {target['condition']} SMI trace")
        summary_rows.append(
            _summary_row(
                target["condition"],
                target["neck_length_um"],
                target["neck_radius_um"],
                result,
                metrics,
                condition_smi,
            )
        )
        discrepancy_rows.extend(
            [
                _metric_row(target["condition"], "SMI", condition_smi, target["reported_smi"], "dimensionless"),
                _metric_row(
                    target["condition"],
                    "Gamma_h_to_d",
                    metrics.gamma_head_to_dendrite,
                    target["reported_gamma_hd"],
                    "dimensionless",
                ),
                _metric_row(
                    target["condition"],
                    "Gamma_h_to_s",
                    metrics.gamma_head_to_soma,
                    target["reported_gamma_hs"],
                    "dimensionless",
                ),
            ]
        )
    outputs["representative_summary"] = _write_csv(results_path / "Figure2_representative_summary.csv", summary_rows)
    outputs["caption_discrepancy"] = _write_csv(results_path / "caption_discrepancy_table.csv", discrepancy_rows)

    lengths = np.linspace(
        config.get("sweeps", "neck_length")["start_um"],
        config.get("sweeps", "neck_length")["stop_um"],
        int(config.get("sweeps", "neck_length")["steps"]),
    )
    radii = np.linspace(
        config.get("sweeps", "neck_radius")["start_um"],
        config.get("sweeps", "neck_radius")["stop_um"],
        int(config.get("sweeps", "neck_radius")["steps"]),
    )
    sweep_rows = _run_geometry_sweep(parameters, lengths, radii)
    outputs["geometry_sweep"] = _write_csv(results_path / "Figure3_geometry_sweep.csv", sweep_rows)
    _write_heatmap_svg(figures_path / "Figure3A_Gamma_hs_heatmap.svg", sweep_rows, "Gamma_h_to_s", "Figure 3A Gamma h-to-s")
    _write_heatmap_svg(figures_path / "Figure3B_SMI_heatmap.svg", sweep_rows, "SMI", "Figure 3B SMI")
    _write_scatter_svg(
        figures_path / "Figure3C_SMI_vs_Gamma_hs.svg",
        [(float(row["SMI"]), float(row["Gamma_h_to_s"])) for row in sweep_rows],
        "Figure 3C SMI vs Gamma h-to-s",
        "SMI",
        "Gamma h-to-s",
        "#d62728",
    )
    _write_scatter_svg(
        figures_path / "Figure3D_SMI_vs_Ah.svg",
        [(float(row["SMI"]), float(row["A_h_mV"])) for row in sweep_rows],
        "Figure 3D SMI vs A_h",
        "SMI",
        "A_h (mV)",
        "#1f77b4",
    )

    gld_values = np.geomspace(
        config.get("validation", "matched_neck")["dendritic_leak_start_nS"],
        config.get("validation", "matched_neck")["dendritic_leak_stop_nS"],
        30,
    )
    matched_neck_ohm = config.get("validation", "matched_neck")["neck_resistance_Mohm"] * 1e6
    matched_rows = _run_matched_neck(parameters, gld_values, matched_neck_ohm)
    outputs["matched_neck"] = _write_csv(results_path / "Figure4_matched_neck_heterogeneous_load.csv", matched_rows)
    _write_scatter_svg(
        figures_path / "Figure4A_Rneck_vs_Gamma_hs.svg",
        [(float(row["neck_resistance_Mohm"]), float(row["Gamma_h_to_s"])) for row in matched_rows],
        "Figure 4A R_neck vs Gamma h-to-s",
        "R_neck (Mohm)",
        "Gamma h-to-s",
        "#9467bd",
    )
    _write_scatter_svg(
        figures_path / "Figure4B_SMI_vs_Gamma_hs.svg",
        [(float(row["SMI"]), float(row["Gamma_h_to_s"])) for row in matched_rows],
        "Figure 4B SMI vs Gamma h-to-s",
        "SMI",
        "Gamma h-to-s",
        "#d62728",
    )
    _write_scatter_svg(
        figures_path / "Figure4C_SMI_vs_Ah.svg",
        [(float(row["SMI"]), float(row["A_h_mV"])) for row in matched_rows],
        "Figure 4C SMI vs A_h",
        "SMI",
        "A_h (mV)",
        "#1f77b4",
    )

    convergence_rows = _run_convergence(parameters)
    outputs["convergence"] = _write_csv(results_path / "convergence_dt_intermediate.csv", convergence_rows)
    _write_scatter_svg(
        figures_path / "convergence_dt_vs_Ah.svg",
        [(float(row["dt_ms"]), float(row["A_h_mV"])) for row in convergence_rows],
        "Convergence: dt vs A_h",
        "dt (ms)",
        "A_h (mV)",
        "#2ca02c",
    )

    smi_values = [float(row["SMI"]) for row in sweep_rows]
    rneck_values = [float(row["neck_resistance_Mohm"]) for row in sweep_rows]
    gamma_values = [float(row["Gamma_h_to_s"]) for row in sweep_rows]
    ah_values = [float(row["A_h_mV"]) for row in sweep_rows]
    matched_smi = [float(row["SMI"]) for row in matched_rows]
    matched_gamma = [float(row["Gamma_h_to_s"]) for row in matched_rows]
    claim_rows = [
        {
            "claim": "fixed_load_SMI_and_Rneck_identical_rank_order",
            "statistic": "Spearman(SMI,R_neck)",
            "value": _spearman(smi_values, rneck_values),
            "interpretation": "supporting" if abs(_spearman(smi_values, rneck_values) - 1.0) < 1e-12 else "contradictory",
        },
        {
            "claim": "fixed_load_downstream_transfer_decreases_with_SMI",
            "statistic": "Spearman(SMI,Gamma_h_to_s)",
            "value": _spearman(smi_values, gamma_values),
            "interpretation": "supporting" if _spearman(smi_values, gamma_values) < -0.8 else "contradictory",
        },
        {
            "claim": "fixed_load_head_amplitude_increases_with_SMI",
            "statistic": "Spearman(SMI,A_h)",
            "value": _spearman(smi_values, ah_values),
            "interpretation": "supporting" if _spearman(smi_values, ah_values) > 0.8 else "contradictory",
        },
        {
            "claim": "matched_neck_Rneck_cannot_rank_transfer",
            "statistic": "unique_R_neck_values",
            "value": len({float(row["neck_resistance_Mohm"]) for row in matched_rows}),
            "interpretation": "supporting",
        },
        {
            "claim": "matched_neck_SMI_orders_transfer_by_load",
            "statistic": "Spearman(SMI,Gamma_h_to_s)",
            "value": _spearman(matched_smi, matched_gamma),
            "interpretation": "supporting" if abs(_spearman(matched_smi, matched_gamma)) > 0.8 else "contradictory",
        },
    ]
    outputs["central_claims"] = _write_csv(results_path / "central_smi_claim_tests.csv", claim_rows)

    parameters_rows = [
        {"field": "track", "value": config.track, "unit": ""},
        {"field": "dt", "value": s_to_ms(parameters.dt_s), "unit": "ms"},
        {"field": "stop", "value": s_to_ms(parameters.stop_s), "unit": "ms"},
        {"field": "metric_window", "value": s_to_ms(parameters.metric_window_s), "unit": "ms"},
        {"field": "E_L", "value": V_to_mV(parameters.leak_reversal_V), "unit": "mV"},
        {"field": "E_syn", "value": V_to_mV(parameters.synaptic_reversal_V), "unit": "mV"},
        {"field": "g_max", "value": S_to_nS(parameters.synapse.g_max_S), "unit": "nS"},
        {"field": "tau_rise", "value": s_to_ms(parameters.synapse.tau_rise_s), "unit": "ms"},
        {"field": "tau_decay", "value": s_to_ms(parameters.synapse.tau_decay_s), "unit": "ms"},
        {"field": "t0", "value": s_to_ms(parameters.synapse.event_time_s), "unit": "ms"},
    ]
    outputs["parameters"] = _write_csv(results_path / "reproduction_parameters.csv", parameters_rows)
    return outputs
