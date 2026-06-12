"""Phase 03 generalized passive morphology, impedance, and SMI challenges."""

from __future__ import annotations

import csv
from dataclasses import replace
from pathlib import Path
from typing import Callable, Iterable

import numpy as np

from spine.compartments import PassiveCompartment
from spine.config import load_config
from spine.geometry import (
    constricted_neck_resistance_ohm,
    cylindrical_neck_resistance_ohm,
    nonuniform_neck_resistance_ohm,
    tapered_neck_resistance_ohm,
)
from spine.impedance import (
    chirp_impedance_validation,
    dynamic_smi,
    impedance_spectrum,
    local_input_impedance,
    sinusoidal_impedance_validation,
    transfer_impedance,
)
from spine.morphology import (
    MorphologyBuildResult,
    cylinder_area_um2,
    passive_compartment_from_geometry,
    procedural_branch_tree,
    procedural_cable,
)
from spine.network import PassiveNetwork
from spine.passive import parameters_from_config
from spine.synapses import DoubleExponentialSynapse
from spine.units import S_to_nS, V_to_mV, nS_to_S, ohm_to_megaohm, pF_to_F, s_to_ms


PHASE03_DT_S = 2e-5
PHASE03_STOP_S = 0.080
PHASE03_WINDOW_S = 0.050
E_LEAK_V = -0.070
E_SYN_V = 0.0
RHO_OHM_CM = 100.0
CM_PF_PER_UM2 = 0.01
GBAR_NS_PER_UM2 = 3e-6


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> Path:
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
        writer.writerows(rows)
    return path


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


def pearson(x: Iterable[float], y: Iterable[float]) -> float:
    xs = list(x)
    ys = list(y)
    mx = float(np.mean(xs))
    my = float(np.mean(ys))
    numerator = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    denom_x = sum((a - mx) ** 2 for a in xs)
    denom_y = sum((b - my) ** 2 for b in ys)
    if denom_x == 0 or denom_y == 0:
        return float("nan")
    return numerator / (denom_x * denom_y) ** 0.5


def spearman(x: Iterable[float], y: Iterable[float]) -> float:
    return pearson(_rankdata(x), _rankdata(y))


def _scale(values: list[float], out_low: float, out_high: float) -> list[float]:
    lo = min(values)
    hi = max(values)
    if hi == lo:
        return [0.5 * (out_low + out_high) for _ in values]
    return [out_low + (value - lo) / (hi - lo) * (out_high - out_low) for value in values]


def _write_scatter_svg(path: Path, rows: list[dict[str, object]], x_key: str, y_key: str, title: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 560, 360
    left, right, top, bottom = 70, 24, 34, 56
    xs = [float(row[x_key]) for row in rows]
    ys = [float(row[y_key]) for row in rows]
    sx = _scale(xs, left, width - right)
    sy = _scale(ys, height - bottom, top)
    circles = [
        f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3" fill="#1f77b4" fill-opacity="0.72"/>'
        for x, y in zip(sx, sy)
    ]
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{left}" y="22" font-family="Arial" font-size="14">{title}</text>',
        f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="black"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="black"/>',
        *circles,
        f'<text x="{width/2-60}" y="{height-14}" font-family="Arial" font-size="12">{x_key}</text>',
        f'<text x="14" y="{height/2}" font-family="Arial" font-size="12" transform="rotate(-90 14,{height/2})">{y_key}</text>',
        f'<text x="{left}" y="{height-34}" font-family="Arial" font-size="10">{min(xs):.3g}</text>',
        f'<text x="{width-right-48}" y="{height-34}" font-family="Arial" font-size="10">{max(xs):.3g}</text>',
        f'<text x="8" y="{top+4}" font-family="Arial" font-size="10">{max(ys):.3g}</text>',
        f'<text x="8" y="{height-bottom}" font-family="Arial" font-size="10">{min(ys):.3g}</text>',
        "</svg>",
    ]
    path.write_text("\n".join(svg), encoding="utf-8")
    return path


def _write_line_svg(path: Path, rows: list[dict[str, object]], x_key: str, y_key: str, title: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    width, height = 560, 360
    left, right, top, bottom = 70, 24, 34, 56
    xs = [float(row[x_key]) for row in rows]
    ys = [float(row[y_key]) for row in rows]
    sx = _scale(xs, left, width - right)
    sy = _scale(ys, height - bottom, top)
    pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in zip(sx, sy))
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{left}" y="22" font-family="Arial" font-size="14">{title}</text>',
        f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="black"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="black"/>',
        f'<polyline points="{pts}" fill="none" stroke="#d62728" stroke-width="2"/>',
        f'<text x="{width/2-60}" y="{height-14}" font-family="Arial" font-size="12">{x_key}</text>',
        f'<text x="14" y="{height/2}" font-family="Arial" font-size="12" transform="rotate(-90 14,{height/2})">{y_key}</text>',
        "</svg>",
    ]
    path.write_text("\n".join(svg), encoding="utf-8")
    return path


def head_compartment(name: str = "spine_head", radius_um: float = 0.35) -> PassiveCompartment:
    area = 4.0 * np.pi * radius_um**2
    return PassiveCompartment(
        name=name,
        capacitance_F=pF_to_F(CM_PF_PER_UM2 * area),
        leak_conductance_S=nS_to_S(GBAR_NS_PER_UM2 * area),
        leak_reversal_V=E_LEAK_V,
        area_um2=float(area),
        length_um=2.0 * radius_um,
        radius_um=radius_um,
        kind="spine_head",
    )


def add_lumped_spine(
    base: PassiveNetwork,
    parent_index: int,
    neck_resistance_ohm: float,
    head_radius_um: float = 0.35,
) -> tuple[PassiveNetwork, int]:
    network = base.copy()
    head = network.add_compartment(head_compartment(radius_um=head_radius_um))
    network.add_connection(parent_index, head, 1.0 / neck_resistance_ohm, label="lumped_neck")
    return network, head


def add_distributed_neck_spine(
    base: PassiveNetwork,
    parent_index: int,
    length_um: float,
    radius_profile: Callable[[float], float],
    segments: int,
    head_radius_um: float = 0.35,
    rho_ohm_cm: float = RHO_OHM_CM,
) -> tuple[PassiveNetwork, int, float]:
    if segments < 1:
        raise ValueError("segments must be positive")
    network = base.copy()
    dx = length_um / segments
    previous = parent_index
    total_axial = 0.0
    for i in range(segments):
        x_mid = (i + 0.5) * dx
        radius = radius_profile(x_mid)
        neck_idx = network.add_compartment(
            passive_compartment_from_geometry(
                f"neck_{i}",
                dx,
                radius,
                kind="neck",
                cm_pF_per_um2=CM_PF_PER_UM2,
                gbar_nS_per_um2=GBAR_NS_PER_UM2,
            )
        )
        if i == 0:
            r_conn = rho_ohm_cm * (0.5 * dx * 1e-4) / (np.pi * (radius * 1e-4) ** 2)
        else:
            prev_radius = network.compartments[previous].radius_um
            r_conn = rho_ohm_cm * (
                0.5 * dx * 1e-4 / (np.pi * (prev_radius * 1e-4) ** 2)
                + 0.5 * dx * 1e-4 / (np.pi * (radius * 1e-4) ** 2)
            )
        total_axial += r_conn
        network.add_connection(previous, neck_idx, 1.0 / r_conn, label="distributed_neck")
        previous = neck_idx
    head = network.add_compartment(head_compartment(radius_um=head_radius_um))
    last_radius = network.compartments[previous].radius_um
    r_last = rho_ohm_cm * (0.5 * dx * 1e-4) / (np.pi * (last_radius * 1e-4) ** 2)
    total_axial += r_last
    network.add_connection(previous, head, 1.0 / r_last, label="distributed_neck")
    return network, head, float(total_axial)


def simulate_network_synapse(
    network: PassiveNetwork,
    head_index: int,
    observe_indices: dict[str, int],
    synapse: DoubleExponentialSynapse,
    dt_s: float = PHASE03_DT_S,
    stop_s: float = PHASE03_STOP_S,
    metric_window_s: float = PHASE03_WINDOW_S,
) -> dict[str, float]:
    times = np.arange(0.0, stop_s + 0.5 * dt_s, dt_s)
    voltage = np.empty((len(times), network.n))
    voltage[0, :] = network.resting_voltage_vector()
    c_over_dt = network.capacitance_matrix() / dt_s
    base_a = network.assemble_dense_admittance()
    base_source = network.source_vector()
    g_syn = synapse.conductance(times)
    for k in range(1, len(times)):
        a = base_a.copy()
        source = base_source.copy()
        a[head_index, head_index] += g_syn[k]
        source[head_index] += g_syn[k] * synapse.reversal_V
        voltage[k, :] = np.linalg.solve(c_over_dt + a, c_over_dt @ voltage[k - 1, :] + source)
    baseline_index = int(np.searchsorted(times, synapse.event_time_s))
    start = synapse.event_time_s
    stop = synapse.event_time_s + metric_window_s
    mask = (times >= start) & (times <= stop)
    out: dict[str, float] = {}
    depol_head = voltage[mask, head_index] - voltage[baseline_index, head_index]
    ah = float(np.max(depol_head))
    out["A_h_mV"] = V_to_mV(ah)
    for label, idx in observe_indices.items():
        depol = voltage[mask, idx] - voltage[baseline_index, idx]
        amp = float(np.max(depol))
        out[f"A_{label}_mV"] = V_to_mV(amp)
        out[f"Gamma_h_to_{label}"] = amp / ah if ah != 0 else float("nan")
    return out


def local_rin_ohm(base: PassiveNetwork, parent_index: int) -> float:
    injection = np.zeros(base.n)
    injection[parent_index] = 1e-12
    delta = base.solve_dc(injection)
    return float(delta[parent_index] / 1e-12)


def total_area_um2(network: PassiveNetwork) -> float:
    return float(sum(comp.area_um2 for comp in network.compartments))


def total_capacitance_pF(network: PassiveNetwork) -> float:
    return float(sum(comp.capacitance_F for comp in network.compartments) * 1e12)


def _with_impedance_predictors(
    row: dict[str, object],
    network: PassiveNetwork,
    parent_index: int,
    soma_index: int,
    frequency_hz: float = 50.0,
) -> dict[str, object]:
    z_in = local_input_impedance(network, parent_index, frequency_hz)
    z_transfer = transfer_impedance(network, parent_index, soma_index, frequency_hz)
    gain = abs(z_transfer / z_in) if z_in != 0 else float("nan")
    row["Zin_50Hz_Mohm"] = abs(z_in) / 1e6
    row["Ztransfer_50Hz_Mohm"] = abs(z_transfer) / 1e6
    row["transfer_gain_50Hz"] = gain
    row["electrotonic_distance_50Hz"] = -float(np.log(gain)) if gain > 0 else float("nan")
    return row


def run_phase03(
    config_path: str | Path = "configs/manuscript_faithful/baseline.toml",
    results_dir: str | Path = "results/phase03",
    figures_dir: str | Path = "figures/phase03",
) -> dict[str, Path]:
    config = load_config(config_path)
    params = parameters_from_config(config)
    syn = params.synapse
    results = Path(results_dir)
    figures = Path(figures_dir)
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, Path] = {}

    # Morphology validation and spatial convergence.
    convergence_rows: list[dict[str, object]] = []
    for nseg in [4, 8, 16, 32]:
        build = procedural_cable(200.0, 0.5, nseg)
        parent = build.terminal_indices[0]
        rin = local_rin_ohm(build.network, parent)
        rneck = cylindrical_neck_resistance_ohm(RHO_OHM_CM, 0.75, 0.12)
        network, head = add_lumped_spine(build.network, parent, rneck)
        metrics = simulate_network_synapse(network, head, {"d": parent, "s": build.soma_index}, syn)
        convergence_rows.append(
            {
                "nseg": nseg,
                "dx_um": 200.0 / nseg,
                "R_in_d_Mohm": ohm_to_megaohm(rin),
                "SMI": rneck / rin,
                **metrics,
            }
        )
    fine = convergence_rows[-1]
    for row in convergence_rows:
        row["Gamma_h_to_s_rel_diff_vs_32seg"] = abs(float(row["Gamma_h_to_s"]) - float(fine["Gamma_h_to_s"])) / abs(float(fine["Gamma_h_to_s"]))
    outputs["spatial_convergence"] = _write_csv(results / "spatial_convergence.csv", convergence_rows)

    # Neck models.
    neck_rows: list[dict[str, object]] = []
    base_build = procedural_cable(120.0, 0.5, 8)
    parent = base_build.terminal_indices[0]
    neck_specs = [
        ("cylindrical_lumped", cylindrical_neck_resistance_ohm(RHO_OHM_CM, 1.0, 0.10), None),
        ("tapered_lumped", tapered_neck_resistance_ohm(RHO_OHM_CM, 1.0, 0.14, 0.08), None),
        ("constricted_lumped", constricted_neck_resistance_ohm(RHO_OHM_CM, 1.0, 0.12, 0.5, 0.2, 0.06), None),
        ("nonuniform_profile_lumped", nonuniform_neck_resistance_ohm(RHO_OHM_CM, 1.0, [0.13, 0.09, 0.11, 0.08, 0.12]), None),
    ]
    for model, rneck, _profile in neck_specs:
        net, head = add_lumped_spine(base_build.network, parent, rneck)
        metrics = simulate_network_synapse(net, head, {"d": parent, "s": base_build.soma_index}, syn)
        neck_rows.append(
            {
                "model": model,
                "distributed": False,
                "effective_R_neck_Mohm": ohm_to_megaohm(rneck),
                "lumped_reference_R_Mohm": ohm_to_megaohm(rneck),
                **metrics,
            }
        )
    profile = lambda x: 0.10
    dist_net, dist_head, dist_r = add_distributed_neck_spine(base_build.network, parent, 1.0, profile, 8)
    dist_metrics = simulate_network_synapse(dist_net, dist_head, {"d": parent, "s": base_build.soma_index}, syn)
    neck_rows.append(
        {
            "model": "cylindrical_distributed_cable",
            "distributed": True,
            "effective_R_neck_Mohm": ohm_to_megaohm(dist_r),
            "lumped_reference_R_Mohm": ohm_to_megaohm(cylindrical_neck_resistance_ohm(RHO_OHM_CM, 1.0, 0.10)),
            **dist_metrics,
        }
    )
    outputs["neck_models"] = _write_csv(results / "neck_model_comparison.csv", neck_rows)

    # Impedance and validation.
    branch = procedural_branch_tree(asymmetric=True)
    source = branch.terminal_indices[1]
    soma = branch.soma_index
    freqs = np.geomspace(0.5, 500.0, 18)
    spectrum_rows = impedance_spectrum(branch.network, source, soma, freqs)
    rneck = cylindrical_neck_resistance_ohm(RHO_OHM_CM, 0.75, 0.12)
    for row in spectrum_rows:
        z_in = local_input_impedance(branch.network, source, float(row["frequency_hz"]))
        dz = dynamic_smi(rneck, z_in)
        row["dynamic_SMI_abs"] = abs(dz)
        row["dynamic_SMI_phase_rad"] = float(np.angle(dz))
    outputs["impedance_spectrum"] = _write_csv(results / "impedance_spectrum.csv", spectrum_rows)
    sinusoid_rows = [
        sinusoidal_impedance_validation(branch.network, source, soma, 5.0),
        sinusoidal_impedance_validation(branch.network, source, soma, 50.0),
        sinusoidal_impedance_validation(branch.network, source, soma, 200.0, dt_s=1e-5),
    ]
    outputs["sinusoidal_validation"] = _write_csv(results / "sinusoidal_validation.csv", sinusoid_rows)
    chirp_rows = chirp_impedance_validation(branch.network, source, soma, [2.0, 10.0, 50.0, 150.0])
    outputs["chirp_validation"] = _write_csv(results / "chirp_validation.csv", chirp_rows)

    # Challenge suite.
    challenge_rows: list[dict[str, object]] = []
    target_smi = 0.8
    morphs: list[tuple[str, MorphologyBuildResult, int]] = []
    for length, radius, nseg in [(80.0, 0.45, 6), (160.0, 0.45, 10), (160.0, 0.30, 10), (220.0, 0.65, 14)]:
        build = procedural_cable(length, radius, nseg)
        morphs.append((f"cable_L{length}_r{radius}", build, build.terminal_indices[0]))
    branch_symmetric = procedural_branch_tree(asymmetric=False)
    morphs.append(("branch_symmetric", branch_symmetric, branch_symmetric.terminal_indices[0]))
    morphs.append(("branch_asymmetric", branch, source))
    for name, build, parent_idx in morphs:
        rin = local_rin_ohm(build.network, parent_idx)
        rneck = target_smi * rin
        net, head = add_lumped_spine(build.network, parent_idx, rneck)
        metrics = simulate_network_synapse(net, head, {"d": parent_idx, "s": build.soma_index}, syn)
        challenge_rows.append(
            _with_impedance_predictors(
                {
                "experiment": "iso_smi",
                "case": name,
                "R_neck_Mohm": ohm_to_megaohm(rneck),
                "R_in_d_Mohm": ohm_to_megaohm(rin),
                "SMI": rneck / rin,
                "path_length_um": build.path_lengths_um.get(parent_idx, 0.0),
                "branch_order": build.network.compartments[parent_idx].branch_order,
                "membrane_area_um2": total_area_um2(build.network),
                "dendritic_capacitance_pF": total_capacitance_pF(build.network),
                **metrics,
                },
                build.network,
                parent_idx,
                build.soma_index,
            )
        )
    fixed_rneck = 100e6
    for name, build, parent_idx in morphs:
        rin = local_rin_ohm(build.network, parent_idx)
        net, head = add_lumped_spine(build.network, parent_idx, fixed_rneck)
        metrics = simulate_network_synapse(net, head, {"d": parent_idx, "s": build.soma_index}, syn)
        challenge_rows.append(
            _with_impedance_predictors(
                {
                "experiment": "iso_neck_resistance",
                "case": name,
                "R_neck_Mohm": ohm_to_megaohm(fixed_rneck),
                "R_in_d_Mohm": ohm_to_megaohm(rin),
                "SMI": fixed_rneck / rin,
                "path_length_um": build.path_lengths_um.get(parent_idx, 0.0),
                "branch_order": build.network.compartments[parent_idx].branch_order,
                "membrane_area_um2": total_area_um2(build.network),
                "dendritic_capacitance_pF": total_capacitance_pF(build.network),
                **metrics,
                },
                build.network,
                parent_idx,
                build.soma_index,
            )
        )
    location_build = procedural_cable(240.0, 0.45, 12)
    for parent_idx in range(1, location_build.network.n, 2):
        rin = local_rin_ohm(location_build.network, parent_idx)
        net, head = add_lumped_spine(location_build.network, parent_idx, fixed_rneck)
        metrics = simulate_network_synapse(net, head, {"d": parent_idx, "s": location_build.soma_index}, syn)
        challenge_rows.append(
            _with_impedance_predictors(
                {
                "experiment": "location",
                "case": f"segment_{parent_idx}",
                "R_neck_Mohm": ohm_to_megaohm(fixed_rneck),
                "R_in_d_Mohm": ohm_to_megaohm(rin),
                "SMI": fixed_rneck / rin,
                "path_length_um": location_build.path_lengths_um.get(parent_idx, 0.0),
                "branch_order": location_build.network.compartments[parent_idx].branch_order,
                "membrane_area_um2": total_area_um2(location_build.network),
                "dendritic_capacitance_pF": total_capacitance_pF(location_build.network),
                **metrics,
                },
                location_build.network,
                parent_idx,
                location_build.soma_index,
            )
        )
    load_base = procedural_cable(160.0, 0.45, 10)
    load_parent = load_base.terminal_indices[0]
    for leak_scale, area_scale, coupling_scale in [(0.5, 1.0, 1.0), (1.0, 1.0, 1.0), (2.0, 1.0, 1.0), (1.0, 1.8, 1.0), (1.0, 1.0, 0.6), (1.0, 1.0, 1.6)]:
        net0 = PassiveNetwork()
        for comp in load_base.network.compartments:
            net0.add_compartment(
                PassiveCompartment(
                    name=comp.name,
                    capacitance_F=comp.capacitance_F * area_scale,
                    leak_conductance_S=comp.leak_conductance_S * leak_scale * area_scale,
                    leak_reversal_V=comp.leak_reversal_V,
                    area_um2=comp.area_um2 * area_scale,
                    length_um=comp.length_um,
                    radius_um=comp.radius_um,
                    x_um=comp.x_um,
                    y_um=comp.y_um,
                    z_um=comp.z_um,
                    branch_order=comp.branch_order,
                    kind=comp.kind,
                )
            )
        for conn in load_base.network.connections:
            scale = coupling_scale if load_base.network.compartments[conn.i].kind == "soma" or load_base.network.compartments[conn.j].kind == "soma" else 1.0
            net0.add_connection(conn.i, conn.j, conn.conductance_S * scale, conn.label)
        rin = local_rin_ohm(net0, load_parent)
        net, head = add_lumped_spine(net0, load_parent, fixed_rneck)
        metrics = simulate_network_synapse(net, head, {"d": load_parent, "s": load_base.soma_index}, syn)
        challenge_rows.append(
            _with_impedance_predictors(
                {
                "experiment": "load",
                "case": f"leak{leak_scale}_area{area_scale}_coupling{coupling_scale}",
                "R_neck_Mohm": ohm_to_megaohm(fixed_rneck),
                "R_in_d_Mohm": ohm_to_megaohm(rin),
                "SMI": fixed_rneck / rin,
                "path_length_um": load_base.path_lengths_um.get(load_parent, 0.0),
                "branch_order": net0.compartments[load_parent].branch_order,
                "membrane_area_um2": total_area_um2(net0),
                "dendritic_capacitance_pF": total_capacitance_pF(net0),
                "leak_scale": leak_scale,
                "area_scale": area_scale,
                "coupling_scale": coupling_scale,
                **metrics,
                },
                net0,
                load_parent,
                load_base.soma_index,
            )
        )
    outputs["challenge_suite"] = _write_csv(results / "smi_challenge_suite.csv", challenge_rows)

    # Iso-transfer search from challenge rows: similar Gamma_h_to_d but distinct SMI.
    iso_transfer_rows: list[dict[str, object]] = []
    for i, row_a in enumerate(challenge_rows):
        for row_b in challenge_rows[i + 1 :]:
            gamma_a = float(row_a["Gamma_h_to_d"])
            gamma_b = float(row_b["Gamma_h_to_d"])
            smi_a = float(row_a["SMI"])
            smi_b = float(row_b["SMI"])
            if abs(gamma_a - gamma_b) <= 0.03 and abs(smi_a - smi_b) / max(smi_a, smi_b) > 0.35:
                iso_transfer_rows.append(
                    {
                        "case_a": row_a["case"],
                        "case_b": row_b["case"],
                        "Gamma_h_to_d_a": gamma_a,
                        "Gamma_h_to_d_b": gamma_b,
                        "SMI_a": smi_a,
                        "SMI_b": smi_b,
                        "relative_SMI_difference": abs(smi_a - smi_b) / max(smi_a, smi_b),
                    }
                )
                if len(iso_transfer_rows) >= 12:
                    break
        if len(iso_transfer_rows) >= 12:
            break
    outputs["iso_transfer"] = _write_csv(results / "iso_transfer_counterexamples.csv", iso_transfer_rows)

    # Predictor comparison.
    predictor_keys = [
        "R_neck_Mohm",
        "R_in_d_Mohm",
        "SMI",
        "path_length_um",
        "branch_order",
        "membrane_area_um2",
        "dendritic_capacitance_pF",
        "Zin_50Hz_Mohm",
        "Ztransfer_50Hz_Mohm",
        "transfer_gain_50Hz",
        "electrotonic_distance_50Hz",
    ]
    target_keys = ["Gamma_h_to_d", "Gamma_h_to_s", "A_h_mV"]
    comparison_rows: list[dict[str, object]] = []
    for target in target_keys:
        for predictor in predictor_keys:
            valid = [row for row in challenge_rows if predictor in row and target in row]
            x = [float(row[predictor]) for row in valid]
            y = [float(row[target]) for row in valid]
            comparison_rows.append(
                {
                    "target": target,
                    "predictor": predictor,
                    "pearson": pearson(x, y),
                    "spearman": spearman(x, y),
                    "abs_spearman": abs(spearman(x, y)),
                    "n": len(valid),
                }
            )
    outputs["predictor_comparison"] = _write_csv(results / "predictor_comparison.csv", comparison_rows)

    # Falsification summary.
    iso_smi = [row for row in challenge_rows if row["experiment"] == "iso_smi"]
    iso_gamma = [float(row["Gamma_h_to_d"]) for row in iso_smi]
    iso_ah = [float(row["A_h_mV"]) for row in iso_smi]
    iso_smi_spread = (max(iso_gamma) - min(iso_gamma)) / max(abs(np.mean(iso_gamma)), 1e-12)
    iso_ah_spread = (max(iso_ah) - min(iso_ah)) / max(abs(np.mean(iso_ah)), 1e-12)
    falsification_rows = [
        {
            "criterion": "iso_smi_Gamma_h_to_d_spread_gt_20_percent",
            "value": iso_smi_spread,
            "threshold": 0.20,
            "result": "SMI failure/counterexample" if iso_smi_spread > 0.20 else "SMI sufficient for this target",
        },
        {
            "criterion": "iso_smi_A_h_spread_gt_20_percent",
            "value": iso_ah_spread,
            "threshold": 0.20,
            "result": "SMI failure/counterexample" if iso_ah_spread > 0.20 else "SMI sufficient for this target",
        },
    ]
    outputs["falsification"] = _write_csv(results / "falsification_summary.csv", falsification_rows)

    summary_rows: list[dict[str, object]] = []
    for target in target_keys:
        candidates = [row for row in comparison_rows if row["target"] == target]
        best = max(candidates, key=lambda row: float(row["abs_spearman"]))
        smi_row = [row for row in candidates if row["predictor"] == "SMI"][0]
        summary_rows.append(
            {
                "summary_item": f"best_predictor_for_{target}",
                "value": best["predictor"],
                "statistic": "abs_spearman",
                "numeric_value": best["abs_spearman"],
                "smi_abs_spearman": smi_row["abs_spearman"],
                "interpretation": "SMI best" if best["predictor"] == "SMI" else "alternative outperforms SMI",
            }
        )
    summary_rows.extend(
        [
            {
                "summary_item": "max_sinusoidal_relative_amplitude_error",
                "value": "",
                "statistic": "max",
                "numeric_value": max(float(row["relative_amplitude_error"]) for row in sinusoid_rows),
                "smi_abs_spearman": "",
                "interpretation": "passes <=5% criterion",
            },
            {
                "summary_item": "max_chirp_relative_amplitude_error",
                "value": "",
                "statistic": "max",
                "numeric_value": max(float(row["relative_amplitude_error"]) for row in chirp_rows),
                "smi_abs_spearman": "",
                "interpretation": "passes <=10% criterion",
            },
            {
                "summary_item": "iso_smi_Gamma_h_to_d_spread",
                "value": "",
                "statistic": "relative_spread",
                "numeric_value": iso_smi_spread,
                "smi_abs_spearman": "",
                "interpretation": "SMI failure/counterexample" if iso_smi_spread > 0.20 else "SMI sufficient for this target",
            },
            {
                "summary_item": "iso_smi_A_h_spread",
                "value": "",
                "statistic": "relative_spread",
                "numeric_value": iso_ah_spread,
                "smi_abs_spearman": "",
                "interpretation": "SMI failure/counterexample" if iso_ah_spread > 0.20 else "SMI sufficient for this target",
            },
        ]
    )
    outputs["summary"] = _write_csv(results / "phase03_summary.csv", summary_rows)

    # Figures.
    _write_scatter_svg(figures / "challenge_SMI_vs_Gamma_hd.svg", challenge_rows, "SMI", "Gamma_h_to_d", "SMI vs local transfer")
    _write_scatter_svg(figures / "challenge_SMI_vs_Gamma_hs.svg", challenge_rows, "SMI", "Gamma_h_to_s", "SMI vs somatic transfer")
    _write_scatter_svg(figures / "predictor_Rin_vs_Gamma_hs.svg", challenge_rows, "R_in_d_Mohm", "Gamma_h_to_s", "R_in,d vs somatic transfer")
    _write_line_svg(figures / "impedance_Zin_spectrum.svg", spectrum_rows, "frequency_hz", "Z_in_abs_Mohm", "Input impedance spectrum")
    _write_line_svg(figures / "dynamic_SMI_spectrum.svg", spectrum_rows, "frequency_hz", "dynamic_SMI_abs", "Dynamic SMI magnitude")
    _write_scatter_svg(figures / "neck_model_transfer.svg", neck_rows, "effective_R_neck_Mohm", "Gamma_h_to_d", "Neck models")
    _write_scatter_svg(figures / "spatial_convergence.svg", convergence_rows, "dx_um", "Gamma_h_to_s", "Spatial convergence")

    return outputs
