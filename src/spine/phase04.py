"""Phase 04 active/nonlinear validation, challenges, and protocols."""

from __future__ import annotations

from pathlib import Path
import math

import numpy as np

from spine.active import (
    ChannelPlacement,
    SynapsePlacement,
    VoltageClamp,
    frozen_gate_impedance,
    peak_depolarization_metrics,
    place_channels,
    simulate_active_network,
)
from spine.channels import audit_channel_gates, default_active_channels, make_channel
from spine.config import load_config
from spine.geometry import cylindrical_neck_resistance_ohm
from spine.impedance import local_input_impedance, transfer_impedance
from spine.morphology import MorphologyBuildResult, procedural_branch_tree, procedural_cable
from spine.network import PassiveNetwork
from spine.phase03 import (
    _write_csv,
    _write_line_svg,
    _write_scatter_svg,
    local_rin_ohm,
    pearson,
    spearman,
    total_area_um2,
    total_capacitance_pF,
)
from spine.phase03 import add_lumped_spine
from spine.synapses import DoubleExponentialSynapse, magnesium_block, make_ampa_nmda_synapse
from spine.units import megaohm_to_ohm, mV_to_V, nS_to_S, ohm_to_megaohm


PHASE04_DT_S = 2e-5
PHASE04_REFINED_DT_S = 5e-6
PHASE04_STOP_S = 0.080
PHASE04_SHORT_STOP_S = 0.045
PHASE04_EVENT_TIME_S = 0.020
PHASE04_WINDOW_S = 0.050
RHO_OHM_CM = 100.0


def _active_synapse(protocol: str, g_scale: float = 1.0, event_times_s: tuple[float, ...] = (PHASE04_EVENT_TIME_S,)):
    if protocol == "AMPA":
        return make_ampa_nmda_synapse(
            event_times_s,
            ampa_g_max_S=nS_to_S(1.4 * g_scale),
            nmda_g_max_S=0.0,
            label="AMPA",
        )
    if protocol == "AMPA_NMDA":
        return make_ampa_nmda_synapse(
            event_times_s,
            ampa_g_max_S=nS_to_S(1.4 * g_scale),
            nmda_g_max_S=nS_to_S(0.7 * g_scale),
            label="AMPA_NMDA",
        )
    raise ValueError(f"unsupported synaptic protocol: {protocol}")


def _channels_for_profile(profile: str):
    return default_active_channels(profile)


def _attach_active_case(
    build: MorphologyBuildResult,
    parent_index: int,
    rneck_ohm: float,
    protocol: str,
    active_profile: str,
    g_scale: float = 1.0,
    event_times_s: tuple[float, ...] = (PHASE04_EVENT_TIME_S,),
) -> tuple[PassiveNetwork, int, list[ChannelPlacement], list[SynapsePlacement]]:
    network, head = add_lumped_spine(build.network, parent_index, rneck_ohm)
    synapse = _active_synapse(protocol, g_scale=g_scale, event_times_s=event_times_s)
    channel_indices = sorted({head, parent_index, build.soma_index})
    channels = _channels_for_profile(active_profile)
    placements = place_channels(channels, channel_indices, label_prefix=active_profile)
    synapses = [SynapsePlacement(head, synapse, label=protocol)]
    return network, head, placements, synapses


def _run_case(
    build: MorphologyBuildResult,
    parent_index: int,
    rneck_ohm: float,
    protocol: str,
    active_profile: str,
    dt_s: float = PHASE04_DT_S,
    stop_s: float = PHASE04_STOP_S,
    method: str = "semi_implicit",
    g_scale: float = 1.0,
    event_times_s: tuple[float, ...] = (PHASE04_EVENT_TIME_S,),
) -> dict[str, float]:
    network, head, channels, synapses = _attach_active_case(
        build,
        parent_index,
        rneck_ohm,
        protocol,
        active_profile,
        g_scale=g_scale,
        event_times_s=event_times_s,
    )
    result = simulate_active_network(
        network,
        channels,
        synapses,
        dt_s=dt_s,
        stop_s=stop_s,
        method=method,
    )
    return peak_depolarization_metrics(
        result,
        head,
        {"d": parent_index, "s": build.soma_index},
        min(event_times_s),
        PHASE04_WINDOW_S,
    )


def _with_predictors(
    row: dict[str, object],
    build: MorphologyBuildResult,
    parent_index: int,
    active_profile: str,
    frequency_hz: float = 50.0,
) -> dict[str, object]:
    z_in = local_input_impedance(build.network, parent_index, frequency_hz)
    z_transfer = transfer_impedance(build.network, parent_index, build.soma_index, frequency_hz)
    passive_gain = abs(z_transfer / z_in) if z_in != 0 else float("nan")
    active_channels = place_channels(
        _channels_for_profile(active_profile),
        sorted({parent_index, build.soma_index}),
        label_prefix=f"frozen_{active_profile}",
    )
    active_zin = frozen_gate_impedance(build.network, active_channels, parent_index, parent_index, frequency_hz)
    active_ztransfer = frozen_gate_impedance(build.network, active_channels, parent_index, build.soma_index, frequency_hz)
    active_gain = abs(active_ztransfer / active_zin) if active_zin != 0 else float("nan")
    row["Zin_50Hz_Mohm"] = abs(z_in) / 1e6
    row["transfer_gain_50Hz"] = passive_gain
    row["electrotonic_distance_50Hz"] = -math.log(passive_gain) if passive_gain > 0 else float("nan")
    row["active_frozen_Zin_50Hz_Mohm"] = abs(active_zin) / 1e6
    row["active_frozen_transfer_gain_50Hz"] = active_gain
    row["active_profile_channel_count"] = len(_channels_for_profile(active_profile))
    return row


def _relative_difference(a: float, b: float) -> float:
    denom = max(abs(b), 1e-12)
    return abs(a - b) / denom


def _linear_r2(rows: list[dict[str, object]], target: str, predictors: list[str]) -> float:
    valid = [row for row in rows if all(p in row for p in predictors) and target in row]
    if len(valid) <= len(predictors) + 1:
        return float("nan")
    x = np.column_stack([[1.0] * len(valid), *[[float(row[p]) for row in valid] for p in predictors]])
    y = np.array([float(row[target]) for row in valid])
    coeffs, *_ = np.linalg.lstsq(x, y, rcond=None)
    yhat = x @ coeffs
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - float(np.mean(y))) ** 2))
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")


def _validation_rows(results_dir: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    ampa = DoubleExponentialSynapse(
        g_max_S=nS_to_S(1.4),
        tau_rise_s=0.0003,
        tau_decay_s=0.003,
        event_time_s=PHASE04_EVENT_TIME_S,
        reversal_V=0.0,
    )
    rows.append(
        {
            "validation": "AMPA_peak_normalization",
            "value": abs(ampa.analytical_peak_conductance_S() - ampa.g_max_S),
            "threshold": 1e-12,
            "units": "S",
            "passed": abs(ampa.analytical_peak_conductance_S() - ampa.g_max_S) <= 1e-12,
        }
    )

    voltages = np.array([-0.080, -0.060, -0.040, -0.020, 0.0, 0.040])
    blocks = [float(magnesium_block(v)) for v in voltages]
    rows.append(
        {
            "validation": "NMDA_magnesium_block_monotonic",
            "value": min(np.diff(blocks)),
            "threshold": 0.0,
            "units": "dimensionless difference",
            "passed": min(np.diff(blocks)) > 0,
        }
    )
    nmda_syn = _active_synapse("AMPA_NMDA", g_scale=1.0)
    i_neg80 = abs(nmda_syn.current_A(PHASE04_EVENT_TIME_S + 0.010, -0.080))
    i_neg20 = abs(nmda_syn.current_A(PHASE04_EVENT_TIME_S + 0.010, -0.020))
    rows.append(
        {
            "validation": "NMDA_IV_relief",
            "value": i_neg20 / i_neg80,
            "threshold": 1.0,
            "units": "ratio",
            "passed": i_neg20 > i_neg80,
        }
    )

    channels = default_active_channels("full_restrained")
    gate_audit = audit_channel_gates(channels, np.linspace(-0.100, 0.040, 15))
    rows.append(
        {
            "validation": "gate_inf_bounds",
            "value": f"{gate_audit['min_gate_inf']},{gate_audit['max_gate_inf']}",
            "threshold": "[0,1]",
            "units": "dimensionless",
            "passed": gate_audit["min_gate_inf"] >= 0 and gate_audit["max_gate_inf"] <= 1,
        }
    )
    rows.append(
        {
            "validation": "gate_tau_positive",
            "value": gate_audit["min_tau_s"],
            "threshold": 0.0,
            "units": "s",
            "passed": gate_audit["min_tau_s"] > 0,
        }
    )

    sign_checks = []
    for channel in channels:
        gates = channel.initialize(-0.070)
        if channel.name in {"na", "cat", "hcn"}:
            sign_checks.append(channel.current_A(-0.070, gates) < 0)
        if channel.name in {"kdr", "ka"}:
            sign_checks.append(channel.current_A(-0.050, channel.initialize(-0.050)) > 0)
    rows.append(
        {
            "validation": "active_current_signs",
            "value": sum(bool(x) for x in sign_checks),
            "threshold": len(sign_checks),
            "units": "checks passed",
            "passed": all(sign_checks),
        }
    )

    build = procedural_cable(120.0, 0.5, 6)
    parent = build.terminal_indices[0]
    rneck = cylindrical_neck_resistance_ohm(RHO_OHM_CM, 0.75, 0.12)
    net, head, channel_placements, _synapses = _attach_active_case(
        build, parent, rneck, "AMPA", "full_restrained", event_times_s=(10.0,)
    )
    rest = simulate_active_network(net, channel_placements, [], dt_s=PHASE04_DT_S, stop_s=PHASE04_STOP_S)
    drift_mV = float(np.max(np.abs(rest.voltage_V - rest.voltage_V[0, :])) * 1e3)
    rows.append(
        {
            "validation": "resting_state_stability",
            "value": drift_mV,
            "threshold": 1.0,
            "units": "mV",
            "passed": drift_mV < 1.0,
        }
    )
    rows.append(
        {
            "validation": "simulated_gate_bounds",
            "value": f"{rest.min_gate_value},{rest.max_gate_value}",
            "threshold": "[0,1]",
            "units": "dimensionless",
            "passed": rest.min_gate_value >= -1e-12 and rest.max_gate_value <= 1.0 + 1e-12,
        }
    )

    coarse = _run_case(build, parent, rneck, "AMPA_NMDA", "hcn", dt_s=1e-5, stop_s=PHASE04_SHORT_STOP_S)
    fine = _run_case(build, parent, rneck, "AMPA_NMDA", "hcn", dt_s=PHASE04_REFINED_DT_S, stop_s=PHASE04_SHORT_STOP_S)
    timestep_error = _relative_difference(float(coarse["A_h_mV"]), float(fine["A_h_mV"]))
    rows.append(
        {
            "validation": "timestep_refinement_A_h",
            "value": timestep_error,
            "threshold": 0.05,
            "units": "relative",
            "passed": timestep_error < 0.05,
        }
    )

    crosscheck_rneck = 500e6
    semi = _run_case(
        build,
        parent,
        crosscheck_rneck,
        "AMPA",
        "none",
        dt_s=PHASE04_REFINED_DT_S,
        stop_s=PHASE04_SHORT_STOP_S,
        g_scale=0.25,
    )
    explicit = _run_case(
        build,
        parent,
        crosscheck_rneck,
        "AMPA",
        "none",
        dt_s=1e-6,
        stop_s=PHASE04_SHORT_STOP_S,
        method="explicit_euler",
        g_scale=0.25,
    )
    solver_error = _relative_difference(float(semi["A_h_mV"]), float(explicit["A_h_mV"]))
    rows.append(
        {
            "validation": "independent_solver_crosscheck_A_h",
            "value": solver_error,
            "threshold": 0.075,
            "units": "relative",
            "passed": solver_error < 0.075,
        }
    )

    strong = _run_case(
        build,
        parent,
        rneck,
        "AMPA_NMDA",
        "full_restrained",
        dt_s=PHASE04_DT_S,
        g_scale=4.0,
    )
    rows.append(
        {
            "validation": "strong_drive_stability",
            "value": f"{strong['min_voltage_mV']},{strong['max_voltage_mV']},{strong['min_gate']},{strong['max_gate']}",
            "threshold": "finite voltage in [-200,150] mV and gates in [0,1]",
            "units": "mixed",
            "passed": (
                strong["min_voltage_mV"] > -200
                and strong["max_voltage_mV"] < 150
                and strong["min_gate"] >= -1e-12
                and strong["max_gate"] <= 1.0 + 1e-12
            ),
        }
    )

    unit_checks = [
        nS_to_S(1.0) == 1e-9,
        mV_to_V(1.0) == 1e-3,
        megaohm_to_ohm(1.0) == 1e6,
    ]
    rows.append(
        {
            "validation": "active_unit_conversions",
            "value": sum(bool(x) for x in unit_checks),
            "threshold": len(unit_checks),
            "units": "checks passed",
            "passed": all(unit_checks),
        }
    )
    return rows


def _challenge_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    morphs: list[tuple[str, MorphologyBuildResult, int]] = []
    for length, radius, nseg in [(80.0, 0.45, 6), (160.0, 0.45, 10), (180.0, 0.35, 10)]:
        build = procedural_cable(length, radius, nseg)
        morphs.append((f"cable_L{length}_r{radius}", build, build.terminal_indices[0]))
    branch = procedural_branch_tree(asymmetric=True)
    morphs.append(("branch_asymmetric", branch, branch.terminal_indices[1]))

    protocols = [
        ("AMPA", "none"),
        ("AMPA_NMDA", "none"),
        ("AMPA_NMDA", "hcn"),
        ("AMPA_NMDA", "full_restrained"),
    ]
    target_smi = 0.8
    fixed_rneck = 100e6

    for experiment in ["iso_smi", "iso_neck_resistance"]:
        for protocol, active_profile in protocols:
            for name, build, parent in morphs:
                rin = local_rin_ohm(build.network, parent)
                rneck = target_smi * rin if experiment == "iso_smi" else fixed_rneck
                metrics = _run_case(build, parent, rneck, protocol, active_profile)
                row: dict[str, object] = {
                    "experiment": experiment,
                    "case": name,
                    "protocol": protocol,
                    "active_profile": active_profile,
                    "R_neck_Mohm": ohm_to_megaohm(rneck),
                    "R_in_d_Mohm": ohm_to_megaohm(rin),
                    "SMI": rneck / rin,
                    "path_length_um": build.path_lengths_um.get(parent, 0.0),
                    "branch_order": build.network.compartments[parent].branch_order,
                    "membrane_area_um2": total_area_um2(build.network),
                    "dendritic_capacitance_pF": total_capacitance_pF(build.network),
                    **metrics,
                }
                rows.append(_with_predictors(row, build, parent, active_profile))

    load_base = procedural_cable(160.0, 0.45, 10)
    parent = load_base.terminal_indices[0]
    for leak_scale, soma_coupling_scale in [(0.5, 1.0), (1.0, 1.0), (2.0, 1.0), (1.0, 0.6), (1.0, 1.6)]:
        net0 = PassiveNetwork()
        for comp in load_base.network.compartments:
            net0.add_compartment(
                type(comp)(
                    name=comp.name,
                    capacitance_F=comp.capacitance_F,
                    leak_conductance_S=comp.leak_conductance_S * leak_scale,
                    leak_reversal_V=comp.leak_reversal_V,
                    area_um2=comp.area_um2,
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
            ci = load_base.network.compartments[conn.i]
            cj = load_base.network.compartments[conn.j]
            scale = soma_coupling_scale if ci.kind == "soma" or cj.kind == "soma" else 1.0
            net0.add_connection(conn.i, conn.j, conn.conductance_S * scale, conn.label)
        build = MorphologyBuildResult(net0, load_base.soma_index, load_base.terminal_indices, load_base.path_lengths_um)
        for protocol, active_profile in [("AMPA_NMDA", "none"), ("AMPA_NMDA", "hcn"), ("AMPA_NMDA", "full_restrained")]:
            rin = local_rin_ohm(build.network, parent)
            metrics = _run_case(build, parent, fixed_rneck, protocol, active_profile)
            row = {
                "experiment": "load",
                "case": f"leak{leak_scale}_coupling{soma_coupling_scale}",
                "protocol": protocol,
                "active_profile": active_profile,
                "R_neck_Mohm": ohm_to_megaohm(fixed_rneck),
                "R_in_d_Mohm": ohm_to_megaohm(rin),
                "SMI": fixed_rneck / rin,
                "path_length_um": build.path_lengths_um.get(parent, 0.0),
                "branch_order": build.network.compartments[parent].branch_order,
                "membrane_area_um2": total_area_um2(build.network),
                "dendritic_capacitance_pF": total_capacitance_pF(build.network),
                "leak_scale": leak_scale,
                "soma_coupling_scale": soma_coupling_scale,
                **metrics,
            }
            rows.append(_with_predictors(row, build, parent, active_profile))

    return rows


def _predictor_rows(challenge_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    predictors = [
        "R_neck_Mohm",
        "R_in_d_Mohm",
        "SMI",
        "Zin_50Hz_Mohm",
        "transfer_gain_50Hz",
        "electrotonic_distance_50Hz",
        "active_frozen_Zin_50Hz_Mohm",
        "active_frozen_transfer_gain_50Hz",
        "path_length_um",
        "branch_order",
        "membrane_area_um2",
        "dendritic_capacitance_pF",
        "active_profile_channel_count",
    ]
    targets = ["Gamma_h_to_d", "Gamma_h_to_s", "A_h_mV", "local_voltage_isolation"]
    protocols = sorted({str(row["protocol"]) + "/" + str(row["active_profile"]) for row in challenge_rows})
    rows: list[dict[str, object]] = []
    for group in ["all", *protocols]:
        subset = challenge_rows
        if group != "all":
            protocol, profile = group.split("/")
            subset = [row for row in challenge_rows if row["protocol"] == protocol and row["active_profile"] == profile]
        for target in targets:
            for predictor in predictors:
                valid = [row for row in subset if predictor in row and target in row]
                if len(valid) < 3:
                    continue
                x = [float(row[predictor]) for row in valid]
                y = [float(row[target]) for row in valid]
                rows.append(
                    {
                        "group": group,
                        "target": target,
                        "predictor": predictor,
                        "pearson": pearson(x, y),
                        "spearman": spearman(x, y),
                        "abs_spearman": abs(spearman(x, y)),
                        "n": len(valid),
                    }
                )
    return rows


def _multivariable_rows(challenge_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    fixed_predictors = ["SMI", "transfer_gain_50Hz", "active_profile_channel_count"]
    rows: list[dict[str, object]] = []
    for target in ["Gamma_h_to_d", "Gamma_h_to_s", "A_h_mV"]:
        rows.append(
            {
                "target": target,
                "predictors": "+".join(fixed_predictors),
                "diagnostic_r2": _linear_r2(challenge_rows, target, fixed_predictors),
                "note": "fixed diagnostic comparison, not Phase 05 predictor ranking",
            }
        )
    return rows


def _falsification_rows(challenge_rows: list[dict[str, object]], predictor_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    iso = [row for row in challenge_rows if row["experiment"] == "iso_smi"]
    for protocol, profile in sorted({(row["protocol"], row["active_profile"]) for row in iso}):
        subset = [row for row in iso if row["protocol"] == protocol and row["active_profile"] == profile]
        for target in ["Gamma_h_to_d", "A_h_mV"]:
            values = [float(row[target]) for row in subset]
            spread = (max(values) - min(values)) / max(abs(float(np.mean(values))), 1e-12)
            rows.append(
                {
                    "criterion": f"iso_smi_{protocol}_{profile}_{target}_spread_gt_25_percent",
                    "value": spread,
                    "threshold": 0.25,
                    "result": "active SMI failure/counterexample" if spread > 0.25 else "no counterexample by spread criterion",
                }
            )
    all_smi = [
        row for row in predictor_rows
        if row["group"] == "all" and row["predictor"] == "SMI"
    ]
    for row in all_smi:
        abs_s = float(row["abs_spearman"])
        target = row["target"]
        group_rows = [r for r in predictor_rows if r["group"] == "all" and r["target"] == target]
        best = max(group_rows, key=lambda r: float(r["abs_spearman"]))
        if abs_s >= 0.80 and float(best["abs_spearman"]) - abs_s <= 0.10:
            result = "active SMI success"
        elif abs_s >= 0.50:
            result = "active SMI weakened"
        else:
            result = "active SMI failure"
        rows.append(
            {
                "criterion": f"all_{target}_SMI_association",
                "value": abs_s,
                "threshold": "0.80 success, 0.50 failure boundary",
                "result": f"{result}; best={best['predictor']} abs_spearman={best['abs_spearman']}",
            }
        )
    return rows


def _impedance_rows() -> list[dict[str, object]]:
    build = procedural_branch_tree(asymmetric=True)
    source = build.terminal_indices[1]
    soma = build.soma_index
    rows: list[dict[str, object]] = []
    for profile in ["none", "hcn", "na_kdr_hcn", "full_restrained"]:
        channels = place_channels(_channels_for_profile(profile), [source, soma], label_prefix=f"imp_{profile}")
        for frequency_hz in [5.0, 50.0, 150.0]:
            z_in = frozen_gate_impedance(build.network, channels, source, source, frequency_hz)
            z_transfer = frozen_gate_impedance(build.network, channels, source, soma, frequency_hz)
            gain = abs(z_transfer / z_in) if z_in != 0 else float("nan")
            rows.append(
                {
                    "profile": profile,
                    "frequency_hz": frequency_hz,
                    "method": "exploratory_frozen_gate_operating_point",
                    "Zin_Mohm": abs(z_in) / 1e6,
                    "Ztransfer_Mohm": abs(z_transfer) / 1e6,
                    "transfer_gain": gain,
                    "phase_rad": float(np.angle(z_transfer / z_in)) if z_in != 0 else float("nan"),
                }
            )
    return rows


def _protocol_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    build = procedural_cable(140.0, 0.5, 8)
    parent = build.terminal_indices[0]
    rneck = cylindrical_neck_resistance_ohm(RHO_OHM_CM, 0.75, 0.12)

    for protocol in ["AMPA", "AMPA_NMDA"]:
        for g_scale in [0.25, 0.5, 1.0, 2.0, 4.0]:
            metrics = _run_case(build, parent, rneck, protocol, "full_restrained", g_scale=g_scale)
            rows.append(
                {
                    "protocol_family": "synaptic_strength_sweep",
                    "protocol": protocol,
                    "active_profile": "full_restrained",
                    "g_scale": g_scale,
                    **metrics,
                }
            )

    cluster_base = procedural_branch_tree(asymmetric=False)
    parent_indices = [cluster_base.terminal_indices[0], cluster_base.terminal_indices[1], cluster_base.terminal_indices[0]]
    for family, event_times in [
        ("clustered_spine_activation", [(PHASE04_EVENT_TIME_S,), (PHASE04_EVENT_TIME_S,), (PHASE04_EVENT_TIME_S,)]),
        ("asynchronous_spine_activation", [(0.020,), (0.022,), (0.025,)]),
    ]:
        network = cluster_base.network.copy()
        heads: list[int] = []
        synapses: list[SynapsePlacement] = []
        for i, parent_idx in enumerate(parent_indices):
            network, head = add_lumped_spine(
                MorphologyBuildResult(network, cluster_base.soma_index, cluster_base.terminal_indices, cluster_base.path_lengths_um).network,
                parent_idx,
                rneck,
            )
            heads.append(head)
            synapses.append(SynapsePlacement(head, _active_synapse("AMPA_NMDA", event_times_s=event_times[i]), label=f"{family}_{i}"))
        channels = place_channels(default_active_channels("full_restrained"), sorted(set(heads + parent_indices + [cluster_base.soma_index])), label_prefix=family)
        result = simulate_active_network(network, channels, synapses, dt_s=PHASE04_DT_S, stop_s=PHASE04_STOP_S)
        metrics = peak_depolarization_metrics(
            result,
            heads[0],
            {"d": parent_indices[0], "s": cluster_base.soma_index},
            PHASE04_EVENT_TIME_S,
            PHASE04_WINDOW_S,
        )
        rows.append(
            {
                "protocol_family": family,
                "protocol": "AMPA_NMDA",
                "active_profile": "full_restrained",
                "spine_count": len(heads),
                **metrics,
            }
        )

    bAP_build = procedural_cable(120.0, 0.5, 6)
    bAP_parent = bAP_build.terminal_indices[0]
    net, head, _channels, _synapses = _attach_active_case(bAP_build, bAP_parent, rneck, "AMPA", "none", event_times_s=(10.0,))
    bAP_channels = place_channels(
        [make_channel("na", 60.0), make_channel("kdr", 18.0)],
        [bAP_build.soma_index, bAP_parent, head],
        label_prefix="bAP",
    )

    bap_pulse_nA = 8.0

    def bap_current(t: float) -> np.ndarray:
        current = np.zeros(net.n)
        if 0.020 <= t <= 0.023:
            current[bAP_build.soma_index] = bap_pulse_nA * 1e-9
        return current

    bap = simulate_active_network(net, bAP_channels, [], dt_s=PHASE04_DT_S, stop_s=0.060, external_current_fn=bap_current)
    bap_metrics = peak_depolarization_metrics(bap, head, {"d": bAP_parent, "s": bAP_build.soma_index}, 0.020, 0.035)
    rows.append(
        {
            "protocol_family": "back_propagating_action_potential",
            "protocol": "somatic_current_pulse",
            "active_profile": "strong_na_kdr",
            "somatic_pulse_nA": bap_pulse_nA,
            "soma_crossed_0mV": bap_metrics["V_s_peak_mV"] > 0,
            **bap_metrics,
        }
    )

    clamp_build = procedural_cable(140.0, 0.5, 8)
    clamp_parent = clamp_build.terminal_indices[0]
    clamp_net, clamp_head, clamp_channels, _ = _attach_active_case(clamp_build, clamp_parent, rneck, "AMPA", "hcn", event_times_s=(10.0,))

    def command(t: float) -> float:
        return -0.030 if 0.020 <= t <= 0.050 else -0.070

    clamp = VoltageClamp(clamp_build.soma_index, nS_to_S(50.0), command)
    clamp_result = simulate_active_network(
        clamp_net,
        clamp_channels,
        [],
        dt_s=PHASE04_DT_S,
        stop_s=0.060,
        voltage_clamps=[clamp],
    )
    clamp_metrics = peak_depolarization_metrics(clamp_result, clamp_head, {"d": clamp_parent, "s": clamp_build.soma_index}, 0.020, 0.035)
    command_peak_mV = -30.0
    rows.append(
        {
            "protocol_family": "somatic_voltage_clamp_escape",
            "protocol": "conductance_clamp_step",
            "active_profile": "hcn",
            "clamp_conductance_nS": 50.0,
            "command_peak_mV": command_peak_mV,
            "head_escape_mV": command_peak_mV - clamp_metrics["V_h_peak_mV"],
            "dendrite_escape_mV": command_peak_mV - clamp_metrics["V_d_peak_mV"],
            **clamp_metrics,
        }
    )
    return rows


def _summary_rows(validation_rows: list[dict[str, object]], falsification_rows: list[dict[str, object]], predictor_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    rows.append(
        {
            "summary_item": "validation_passed",
            "value": all(str(row["passed"]) == "True" or row["passed"] is True for row in validation_rows),
            "numeric_value": sum(1 for row in validation_rows if str(row["passed"]) == "True" or row["passed"] is True),
            "total": len(validation_rows),
        }
    )
    for target in ["Gamma_h_to_d", "Gamma_h_to_s", "A_h_mV"]:
        candidates = [row for row in predictor_rows if row["group"] == "all" and row["target"] == target]
        if not candidates:
            continue
        best = max(candidates, key=lambda row: float(row["abs_spearman"]))
        smi = [row for row in candidates if row["predictor"] == "SMI"][0]
        rows.append(
            {
                "summary_item": f"best_predictor_for_{target}",
                "value": best["predictor"],
                "numeric_value": best["abs_spearman"],
                "smi_abs_spearman": smi["abs_spearman"],
                "interpretation": "SMI best" if best["predictor"] == "SMI" else "alternative outperforms SMI",
            }
        )
    rows.extend(
        {
            "summary_item": row["criterion"],
            "value": row["result"],
            "numeric_value": row["value"],
            "threshold": row["threshold"],
        }
        for row in falsification_rows
    )
    return rows


def run_phase04(
    config_path: str | Path = "configs/active_extension/baseline.toml",
    results_dir: str | Path = "results/phase04",
    figures_dir: str | Path = "figures/phase04",
) -> dict[str, Path]:
    config = load_config(config_path)
    if config.track != "active_extension":
        raise ValueError("Phase 04 must run from an active_extension configuration")

    results = Path(results_dir)
    figures = Path(figures_dir)
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, Path] = {}

    validation = _validation_rows(results)
    outputs["validation"] = _write_csv(results / "active_validation.csv", validation)

    challenge = _challenge_rows()
    outputs["challenge_suite"] = _write_csv(results / "active_smi_challenge_suite.csv", challenge)

    predictors = _predictor_rows(challenge)
    outputs["predictor_comparison"] = _write_csv(results / "active_predictor_comparison.csv", predictors)

    multivariable = _multivariable_rows(challenge)
    outputs["multivariable_diagnostic"] = _write_csv(results / "active_multivariable_diagnostic.csv", multivariable)

    falsification = _falsification_rows(challenge, predictors)
    outputs["falsification"] = _write_csv(results / "active_falsification_summary.csv", falsification)

    impedance = _impedance_rows()
    outputs["impedance"] = _write_csv(results / "active_impedance_operating_point.csv", impedance)

    protocols = _protocol_rows()
    outputs["protocols"] = _write_csv(results / "active_protocol_library.csv", protocols)

    summary = _summary_rows(validation, falsification, predictors)
    outputs["summary"] = _write_csv(results / "phase04_summary.csv", summary)

    _write_scatter_svg(figures / "active_SMI_vs_Gamma_hd.svg", challenge, "SMI", "Gamma_h_to_d", "Active SMI vs local transfer")
    _write_scatter_svg(figures / "active_SMI_vs_Gamma_hs.svg", challenge, "SMI", "Gamma_h_to_s", "Active SMI vs somatic transfer")
    _write_scatter_svg(figures / "active_SMI_vs_Ah.svg", challenge, "SMI", "A_h_mV", "Active SMI vs head amplitude")
    _write_scatter_svg(figures / "active_predictor_gain_vs_Gamma_hs.svg", challenge, "active_frozen_transfer_gain_50Hz", "Gamma_h_to_s", "Frozen-gate gain vs somatic transfer")
    strength_rows = [row for row in protocols if row["protocol_family"] == "synaptic_strength_sweep" and row["protocol"] == "AMPA_NMDA"]
    _write_line_svg(figures / "active_protocol_strength_sweep.svg", strength_rows, "g_scale", "A_h_mV", "AMPA+NMDA strength sweep")
    impedance_rows = [row for row in impedance if row["profile"] == "full_restrained"]
    _write_line_svg(figures / "active_impedance_full_restrained.svg", impedance_rows, "frequency_hz", "transfer_gain", "Frozen-gate active transfer gain")

    return outputs
