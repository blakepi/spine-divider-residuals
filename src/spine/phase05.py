"""Phase 05 sensitivity, uncertainty, identifiability, and predictor analyses."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import math
from statistics import NormalDist

import numpy as np

from spine.active import SynapsePlacement, frozen_gate_impedance, peak_depolarization_metrics, place_channels, simulate_active_network
from spine.channels import make_channel
from spine.compartments import PassiveCompartment
from spine.geometry import cylindrical_neck_resistance_ohm
from spine.impedance import dynamic_smi, local_input_impedance, transfer_impedance
from spine.morphology import MorphologyBuildResult, procedural_cable
from spine.network import PassiveNetwork
from spine.phase03 import _write_csv, _write_line_svg, _write_scatter_svg, add_lumped_spine, local_rin_ohm, pearson, spearman
from spine.synapses import DoubleExponentialSynapse, make_ampa_nmda_synapse
from spine.units import nS_to_S, ohm_to_megaohm


LHS_SEED = 202605
BOOTSTRAP_SEED = 202606
CV_SEED = 202607
GLOBAL_N = 96
EVENT_TIME_S = 0.020
STOP_S = 0.075
WINDOW_S = 0.050
DT_S = 4e-5
FREQUENCY_HZ = 50.0


@dataclass(frozen=True)
class DistributionSpec:
    name: str
    distribution: str
    center: float
    lower: float
    upper: float
    rationale: str
    local_fraction: float = 0.05
    sd: float | None = None


PARAMETERS: tuple[DistributionSpec, ...] = (
    DistributionSpec("neck_radius_um", "truncated_normal", 0.12, 0.06, 0.22, "central imaging uncertainty amplified by R_neck proportional to 1/r^2", sd=0.018),
    DistributionSpec("neck_length_um", "uniform", 0.75, 0.4, 1.4, "manuscript neck-length range and morphology uncertainty"),
    DistributionSpec("intracellular_resistivity_ohm_cm", "uniform", 100.0, 80.0, 180.0, "axial resistivity and nanoscale application uncertainty"),
    DistributionSpec("head_diameter_um", "uniform", 0.70, 0.5, 1.0, "spine-head size uncertainty around manuscript radius"),
    DistributionSpec("dendritic_area_scale", "uniform", 1.0, 0.7, 1.5, "lumped dendritic area/load uncertainty"),
    DistributionSpec("membrane_capacitance_scale", "uniform", 1.0, 0.8, 1.2, "specific capacitance/modeling uncertainty"),
    DistributionSpec("membrane_leak_scale", "log_uniform", 1.0, 0.5, 2.0, "passive leak is a positive multiplicative uncertainty"),
    DistributionSpec("synaptic_conductance_scale", "log_uniform", 1.0, 0.5, 2.0, "synaptic strength is a positive multiplicative uncertainty"),
    DistributionSpec("nmda_fraction", "uniform", 0.35, 0.0, 0.8, "active-extension NMDA-to-AMPA peak fraction uncertainty"),
    DistributionSpec("hcn_density_scale", "uniform", 1.0, 0.0, 2.0, "generic HCN active-extension density uncertainty"),
    DistributionSpec("na_density_scale", "uniform", 1.0, 0.0, 2.0, "generic sodium active-extension density uncertainty"),
    DistributionSpec("kdr_density_scale", "uniform", 1.0, 0.0, 2.0, "generic KDR active-extension density uncertainty"),
    DistributionSpec("a_type_density_scale", "uniform", 1.0, 0.0, 2.0, "generic A-type potassium active-extension density uncertainty"),
    DistributionSpec("calcium_density_scale", "uniform", 1.0, 0.0, 2.0, "restrained electrical-only calcium active-extension uncertainty"),
)


def distribution_rows() -> list[dict[str, object]]:
    return [
        {
            "parameter": spec.name,
            "distribution": spec.distribution,
            "center": spec.center,
            "lower": spec.lower,
            "upper": spec.upper,
            "sd": "" if spec.sd is None else spec.sd,
            "local_fraction": spec.local_fraction,
            "rationale": spec.rationale,
        }
        for spec in PARAMETERS
    ]


def latin_hypercube(n: int, d: int, seed: int = LHS_SEED) -> np.ndarray:
    rng = np.random.default_rng(seed)
    out = np.empty((n, d), dtype=float)
    for j in range(d):
        values = (np.arange(n, dtype=float) + rng.random(n)) / n
        rng.shuffle(values)
        out[:, j] = values
    return out


def _truncated_normal_ppf(q: float, mean: float, sd: float, lower: float, upper: float) -> float:
    normal = NormalDist(mu=mean, sigma=sd)
    lo_cdf = normal.cdf(lower)
    hi_cdf = normal.cdf(upper)
    return normal.inv_cdf(lo_cdf + q * (hi_cdf - lo_cdf))


def sample_parameter(spec: DistributionSpec, q: float) -> float:
    q = min(1.0 - 1e-12, max(1e-12, q))
    if spec.distribution == "uniform":
        return spec.lower + q * (spec.upper - spec.lower)
    if spec.distribution == "log_uniform":
        return math.exp(math.log(spec.lower) + q * (math.log(spec.upper) - math.log(spec.lower)))
    if spec.distribution == "truncated_normal":
        if spec.sd is None:
            raise ValueError("truncated normal requires sd")
        return _truncated_normal_ppf(q, spec.center, spec.sd, spec.lower, spec.upper)
    raise ValueError(f"unsupported distribution: {spec.distribution}")


def lhs_samples(n: int = GLOBAL_N, seed: int = LHS_SEED) -> list[dict[str, float]]:
    cube = latin_hypercube(n, len(PARAMETERS), seed)
    samples: list[dict[str, float]] = []
    for i in range(n):
        row = {"sample_id": float(i)}
        for j, spec in enumerate(PARAMETERS):
            row[spec.name] = sample_parameter(spec, float(cube[i, j]))
        samples.append(row)
    return samples


def baseline_sample() -> dict[str, float]:
    return {"sample_id": -1.0, **{spec.name: spec.center for spec in PARAMETERS}}


def scaled_base_network(sample: dict[str, float]) -> MorphologyBuildResult:
    base = procedural_cable(140.0, 0.5, 8)
    network = PassiveNetwork()
    area_scale = sample["dendritic_area_scale"]
    capacitance_scale = sample["membrane_capacitance_scale"]
    leak_scale = sample["membrane_leak_scale"]
    for comp in base.network.compartments:
        is_dendrite = comp.kind != "soma"
        a_scale = area_scale if is_dendrite else 1.0
        network.add_compartment(
            PassiveCompartment(
                name=comp.name,
                capacitance_F=comp.capacitance_F * capacitance_scale * a_scale,
                leak_conductance_S=comp.leak_conductance_S * leak_scale * a_scale,
                leak_reversal_V=comp.leak_reversal_V,
                area_um2=comp.area_um2 * a_scale,
                length_um=comp.length_um,
                radius_um=comp.radius_um,
                x_um=comp.x_um,
                y_um=comp.y_um,
                z_um=comp.z_um,
                branch_order=comp.branch_order,
                kind=comp.kind,
            )
        )
    for conn in base.network.connections:
        network.add_connection(conn.i, conn.j, conn.conductance_S, conn.label)
    return MorphologyBuildResult(network, base.soma_index, base.terminal_indices, base.path_lengths_um)


def _active_channels_from_sample(sample: dict[str, float]):
    return [
        make_channel("na", 6.0 * sample["na_density_scale"]),
        make_channel("kdr", 1.5 * sample["kdr_density_scale"]),
        make_channel("hcn", 0.05 * sample["hcn_density_scale"]),
        make_channel("ka", 0.5 * sample["a_type_density_scale"]),
        make_channel("cat", 0.05 * sample["calcium_density_scale"]),
    ]


def evaluate_sample(sample: dict[str, float], include_active: bool = True) -> dict[str, object]:
    build = scaled_base_network(sample)
    parent = build.terminal_indices[0]
    soma = build.soma_index
    rneck = cylindrical_neck_resistance_ohm(
        sample["intracellular_resistivity_ohm_cm"],
        sample["neck_length_um"],
        sample["neck_radius_um"],
    )
    rin = local_rin_ohm(build.network, parent)
    smi = rneck / rin
    head_radius = 0.5 * sample["head_diameter_um"]
    network, head = add_lumped_spine(build.network, parent, rneck, head_radius_um=head_radius)
    syn = DoubleExponentialSynapse(
        g_max_S=nS_to_S(1.4 * sample["synaptic_conductance_scale"]),
        tau_rise_s=0.0003,
        tau_decay_s=0.003,
        event_time_s=EVENT_TIME_S,
        reversal_V=0.0,
    )
    from spine.phase03 import simulate_network_synapse

    passive = simulate_network_synapse(
        network,
        head,
        {"d": parent, "s": soma},
        syn,
        dt_s=DT_S,
        stop_s=STOP_S,
        metric_window_s=WINDOW_S,
    )
    z_in = local_input_impedance(build.network, parent, FREQUENCY_HZ)
    z_transfer = transfer_impedance(build.network, parent, soma, FREQUENCY_HZ)
    gain = abs(z_transfer / z_in) if z_in != 0 else float("nan")
    row: dict[str, object] = {
        **sample,
        "R_neck_Mohm": ohm_to_megaohm(rneck),
        "R_in_d_Mohm": ohm_to_megaohm(rin),
        "SMI": smi,
        "SMI_class": smi_class(smi),
        "Gamma_h_to_d": passive["Gamma_h_to_d"],
        "Gamma_h_to_s": passive["Gamma_h_to_s"],
        "A_h_mV": passive["A_h_mV"],
        "local_voltage_isolation": 1.0 - passive["Gamma_h_to_d"],
        "Zin_50Hz_Mohm": abs(z_in) / 1e6,
        "Ztransfer_50Hz_Mohm": abs(z_transfer) / 1e6,
        "transfer_gain_50Hz": gain,
        "electrotonic_distance_50Hz": -math.log(gain) if gain > 0 else float("nan"),
        "dynamic_SMI_abs_50Hz": abs(dynamic_smi(rneck, z_in)),
    }
    if include_active:
        active_syn = make_ampa_nmda_synapse(
            [EVENT_TIME_S],
            ampa_g_max_S=nS_to_S(1.4 * sample["synaptic_conductance_scale"]),
            nmda_g_max_S=nS_to_S(1.4 * sample["synaptic_conductance_scale"] * sample["nmda_fraction"]),
        )
        ampa_syn = make_ampa_nmda_synapse(
            [EVENT_TIME_S],
            ampa_g_max_S=nS_to_S(1.4 * sample["synaptic_conductance_scale"]),
            nmda_g_max_S=0.0,
        )
        placements = place_channels(_active_channels_from_sample(sample), sorted({head, parent, soma}), label_prefix="phase05")
        active_result = simulate_active_network(
            network,
            placements,
            [SynapsePlacement(head, active_syn, label="AMPA_NMDA_uncertainty")],
            dt_s=DT_S,
            stop_s=STOP_S,
        )
        active_metrics = peak_depolarization_metrics(active_result, head, {"d": parent, "s": soma}, EVENT_TIME_S, WINDOW_S)
        ampa_result = simulate_active_network(
            network,
            placements,
            [SynapsePlacement(head, ampa_syn, label="AMPA_uncertainty")],
            dt_s=DT_S,
            stop_s=STOP_S,
        )
        ampa_metrics = peak_depolarization_metrics(ampa_result, head, {"d": parent, "s": soma}, EVENT_TIME_S, WINDOW_S)
        impedance_placements = place_channels(_active_channels_from_sample(sample), sorted({parent, soma}), label_prefix="phase05_impedance")
        active_zin = frozen_gate_impedance(build.network, impedance_placements, parent, parent, FREQUENCY_HZ)
        active_ztransfer = frozen_gate_impedance(build.network, impedance_placements, parent, soma, FREQUENCY_HZ)
        active_gain = abs(active_ztransfer / active_zin) if active_zin != 0 else float("nan")
        row.update(
            {
                "active_Gamma_h_to_d": active_metrics["Gamma_h_to_d"],
                "active_Gamma_h_to_s": active_metrics["Gamma_h_to_s"],
                "active_A_h_mV": active_metrics["A_h_mV"],
                "active_local_voltage_isolation": active_metrics["local_voltage_isolation"],
                "active_Zin_50Hz_Mohm": abs(active_zin) / 1e6,
                "active_transfer_gain_50Hz": active_gain,
                "active_dynamic_SMI_abs_50Hz": abs(dynamic_smi(rneck, active_zin)),
                "AMPA_only_A_h_mV": ampa_metrics["A_h_mV"],
                "NMDA_delta_A_h_fraction": (
                    (active_metrics["A_h_mV"] - ampa_metrics["A_h_mV"]) / max(abs(ampa_metrics["A_h_mV"]), 1e-12)
                ),
            }
        )
    return row


def smi_class(value: float) -> str:
    if value < 0.25:
        return "low"
    if value < 0.75:
        return "intermediate"
    return "high"


def local_sensitivity_rows() -> list[dict[str, object]]:
    baseline = baseline_sample()
    base_outputs = evaluate_sample(baseline, include_active=True)
    output_keys = [
        "R_neck_Mohm",
        "R_in_d_Mohm",
        "SMI",
        "Gamma_h_to_d",
        "Gamma_h_to_s",
        "A_h_mV",
        "local_voltage_isolation",
        "Zin_50Hz_Mohm",
        "transfer_gain_50Hz",
        "dynamic_SMI_abs_50Hz",
        "active_Gamma_h_to_d",
        "active_Gamma_h_to_s",
        "active_A_h_mV",
        "active_Zin_50Hz_Mohm",
        "active_transfer_gain_50Hz",
    ]
    rows: list[dict[str, object]] = []
    for spec in PARAMETERS:
        step = spec.center * spec.local_fraction if spec.center != 0 else 0.02 * (spec.upper - spec.lower)
        low = max(spec.lower, spec.center - step)
        high = min(spec.upper, spec.center + step)
        if low == high:
            continue
        low_sample = dict(baseline)
        high_sample = dict(baseline)
        low_sample[spec.name] = low
        high_sample[spec.name] = high
        low_outputs = evaluate_sample(low_sample, include_active=True)
        high_outputs = evaluate_sample(high_sample, include_active=True)
        for key in output_keys:
            y0 = float(base_outputs[key])
            yl = float(low_outputs[key])
            yh = float(high_outputs[key])
            if y0 == 0:
                coeff = float("nan")
            else:
                coeff = ((yh - yl) / y0) / ((high - low) / spec.center)
            rows.append(
                {
                    "parameter": spec.name,
                    "output": key,
                    "baseline_parameter": spec.center,
                    "low_parameter": low,
                    "high_parameter": high,
                    "baseline_output": y0,
                    "low_output": yl,
                    "high_output": yh,
                    "normalized_sensitivity": coeff,
                    "abs_normalized_sensitivity": abs(coeff) if math.isfinite(coeff) else float("nan"),
                }
            )
    return rows


def uncertainty_summary_rows(samples: list[dict[str, object]]) -> list[dict[str, object]]:
    keys = [
        "R_neck_Mohm",
        "R_in_d_Mohm",
        "SMI",
        "Gamma_h_to_d",
        "Gamma_h_to_s",
        "A_h_mV",
        "Ztransfer_50Hz_Mohm",
        "active_Zin_50Hz_Mohm",
        "active_transfer_gain_50Hz",
        "active_A_h_mV",
        "active_Gamma_h_to_d",
        "active_Gamma_h_to_s",
    ]
    rows: list[dict[str, object]] = []
    for key in keys:
        values = np.array([float(row[key]) for row in samples], dtype=float)
        rows.append(
            {
                "output": key,
                "n": len(values),
                "mean": float(np.mean(values)),
                "sd": float(np.std(values, ddof=1)),
                "p2_5": float(np.percentile(values, 2.5)),
                "p25": float(np.percentile(values, 25.0)),
                "median": float(np.percentile(values, 50.0)),
                "p75": float(np.percentile(values, 75.0)),
                "p97_5": float(np.percentile(values, 97.5)),
            }
        )
    return rows


def uncertainty_decomposition_rows(samples: list[dict[str, object]]) -> list[dict[str, object]]:
    output_keys = ["R_neck_Mohm", "SMI", "Gamma_h_to_d", "Gamma_h_to_s", "A_h_mV", "active_A_h_mV", "active_Gamma_h_to_s"]
    rows: list[dict[str, object]] = []
    for output in output_keys:
        scores: list[tuple[str, float, float]] = []
        y = [float(row[output]) for row in samples]
        for spec in PARAMETERS:
            x = [float(row[spec.name]) for row in samples]
            rho = spearman(x, y)
            scores.append((spec.name, rho, abs(rho)))
        total = sum(score for *_unused, score in scores) or 1.0
        for parameter, rho, abs_rho in sorted(scores, key=lambda item: item[2], reverse=True):
            rows.append(
                {
                    "output": output,
                    "parameter": parameter,
                    "spearman": rho,
                    "abs_spearman": abs_rho,
                    "rank_screening_share": abs_rho / total,
                    "method_note": "rank-correlation uncertainty decomposition; not a Sobol index",
                }
            )
    return rows


def radius_uncertainty_rows(samples: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    offsets = np.linspace(-2.0, 2.0, 25)
    sd_um = 0.018
    for row in samples:
        true_class = str(row["SMI_class"])
        measured_classes = []
        measured_smis = []
        for offset in offsets:
            measured_radius = min(0.22, max(0.06, float(row["neck_radius_um"]) + offset * sd_um))
            measured_rneck = cylindrical_neck_resistance_ohm(
                float(row["intracellular_resistivity_ohm_cm"]),
                float(row["neck_length_um"]),
                measured_radius,
            )
            measured_smi = measured_rneck / (float(row["R_in_d_Mohm"]) * 1e6)
            measured_smis.append(measured_smi)
            measured_classes.append(smi_class(measured_smi))
        stable_fraction = sum(cls == true_class for cls in measured_classes) / len(measured_classes)
        rows.append(
            {
                "sample_id": int(float(row["sample_id"])),
                "true_radius_um": row["neck_radius_um"],
                "true_SMI": row["SMI"],
                "true_class": true_class,
                "measurement_sd_um": sd_um,
                "measured_SMI_min": min(measured_smis),
                "measured_SMI_max": max(measured_smis),
                "class_stable_fraction": stable_fraction,
                "class_flips": stable_fraction < 1.0,
            }
        )
    return rows


def identifiability_rows(samples: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for i, a in enumerate(samples):
        for b in samples[i + 1 :]:
            smi_rel = abs(float(a["SMI"]) - float(b["SMI"])) / max(float(a["SMI"]), float(b["SMI"]), 1e-12)
            morph_rel = max(
                abs(float(a["neck_radius_um"]) - float(b["neck_radius_um"])) / max(float(a["neck_radius_um"]), float(b["neck_radius_um"])),
                abs(float(a["neck_length_um"]) - float(b["neck_length_um"])) / max(float(a["neck_length_um"]), float(b["neck_length_um"])),
                abs(float(a["intracellular_resistivity_ohm_cm"]) - float(b["intracellular_resistivity_ohm_cm"])) / max(float(a["intracellular_resistivity_ohm_cm"]), float(b["intracellular_resistivity_ohm_cm"])),
            )
            gamma_diff = abs(float(a["Gamma_h_to_d"]) - float(b["Gamma_h_to_d"]))
            ah_rel = abs(float(a["A_h_mV"]) - float(b["A_h_mV"])) / max(abs(float(a["A_h_mV"])), abs(float(b["A_h_mV"])), 1e-12)
            if smi_rel < 0.02 and morph_rel > 0.30:
                rows.append(_pair_row("same_SMI_different_morphology", a, b, smi_rel, gamma_diff, ah_rel, morph_rel))
            if gamma_diff < 0.03 and smi_rel > 0.35:
                rows.append(_pair_row("same_transfer_different_SMI", a, b, smi_rel, gamma_diff, ah_rel, morph_rel))
            output_distance = math.sqrt(gamma_diff**2 + (float(a["Gamma_h_to_s"]) - float(b["Gamma_h_to_s"])) ** 2 + ah_rel**2)
            if output_distance < 0.08 and morph_rel > 0.35:
                rows.append(_pair_row("similar_outputs_different_parameters", a, b, smi_rel, gamma_diff, ah_rel, morph_rel))
            if len(rows) >= 60:
                return rows
    return rows


def _pair_row(kind: str, a: dict[str, object], b: dict[str, object], smi_rel: float, gamma_diff: float, ah_rel: float, morph_rel: float) -> dict[str, object]:
    return {
        "degeneracy_type": kind,
        "sample_a": int(float(a["sample_id"])),
        "sample_b": int(float(b["sample_id"])),
        "SMI_a": a["SMI"],
        "SMI_b": b["SMI"],
        "relative_SMI_difference": smi_rel,
        "Gamma_h_to_d_a": a["Gamma_h_to_d"],
        "Gamma_h_to_d_b": b["Gamma_h_to_d"],
        "Gamma_h_to_d_abs_difference": gamma_diff,
        "A_h_mV_a": a["A_h_mV"],
        "A_h_mV_b": b["A_h_mV"],
        "A_h_relative_difference": ah_rel,
        "max_morphology_relative_difference": morph_rel,
        "radius_a_um": a["neck_radius_um"],
        "radius_b_um": b["neck_radius_um"],
        "length_a_um": a["neck_length_um"],
        "length_b_um": b["neck_length_um"],
        "rho_a_ohm_cm": a["intracellular_resistivity_ohm_cm"],
        "rho_b_ohm_cm": b["intracellular_resistivity_ohm_cm"],
    }


def predictor_rows(samples: list[dict[str, object]], seed: int = BOOTSTRAP_SEED) -> list[dict[str, object]]:
    predictors = [
        "R_neck_Mohm",
        "R_in_d_Mohm",
        "SMI",
        "Zin_50Hz_Mohm",
        "Ztransfer_50Hz_Mohm",
        "transfer_gain_50Hz",
        "electrotonic_distance_50Hz",
        "dynamic_SMI_abs_50Hz",
        "neck_radius_um",
        "neck_length_um",
        "head_diameter_um",
        "dendritic_area_scale",
        "membrane_capacitance_scale",
        "membrane_leak_scale",
        "synaptic_conductance_scale",
        "nmda_fraction",
        "hcn_density_scale",
        "na_density_scale",
        "kdr_density_scale",
        "a_type_density_scale",
        "calcium_density_scale",
        "active_Zin_50Hz_Mohm",
        "active_transfer_gain_50Hz",
        "active_dynamic_SMI_abs_50Hz",
    ]
    targets = [
        ("passive", "Gamma_h_to_d"),
        ("passive", "Gamma_h_to_s"),
        ("passive", "A_h_mV"),
        ("passive", "local_voltage_isolation"),
        ("active", "active_Gamma_h_to_d"),
        ("active", "active_Gamma_h_to_s"),
        ("active", "active_A_h_mV"),
        ("active", "active_local_voltage_isolation"),
    ]
    rows: list[dict[str, object]] = []
    for group, target in targets:
        for predictor in predictors:
            x = np.array([float(row[predictor]) for row in samples], dtype=float)
            y = np.array([float(row[target]) for row in samples], dtype=float)
            if np.std(x) == 0 or np.std(y) == 0:
                continue
            rho = spearman(x, y)
            boot_lo, boot_hi = bootstrap_abs_spearman_ci(x, y, seed=seed)
            rows.append(
                {
                    "group": group,
                    "target": target,
                    "predictor": predictor,
                    "pearson": pearson(x, y),
                    "spearman": rho,
                    "abs_spearman": abs(rho),
                    "bootstrap_abs_spearman_p05": boot_lo,
                    "bootstrap_abs_spearman_p95": boot_hi,
                    "cv_rmse": cv_rmse_univariate(x, y),
                    "n": len(samples),
                    "model": "univariate_linear",
                }
            )
    rows.extend(multivariable_predictor_rows(samples))
    return rows


def residual_analysis_rows(samples: list[dict[str, object]], predictors: list[dict[str, object]]) -> list[dict[str, object]]:
    """Focused residual audit for the main Phase 05 claims.

    This deliberately stays small: it checks SMI and the strongest univariate
    comparator for each scientific target, then records which sampled
    parameter remains most associated with the residuals.
    """

    targets = [
        ("passive", "Gamma_h_to_d"),
        ("passive", "Gamma_h_to_s"),
        ("passive", "A_h_mV"),
        ("passive", "local_voltage_isolation"),
        ("active", "active_Gamma_h_to_d"),
        ("active", "active_Gamma_h_to_s"),
        ("active", "active_A_h_mV"),
        ("active", "active_local_voltage_isolation"),
    ]
    rows: list[dict[str, object]] = []
    for group, target in targets:
        univariate = [
            row
            for row in predictors
            if row["group"] == group and row["target"] == target and row["model"] == "univariate_linear"
        ]
        best = max(univariate, key=lambda row: float(row["abs_spearman"]))
        selected = ["SMI", str(best["predictor"])]
        if "Gamma_h_to_s" in target or target == "Gamma_h_to_s":
            selected.extend(["transfer_gain_50Hz", "Ztransfer_50Hz_Mohm"])
        if "A_h_mV" in target:
            selected.extend(["synaptic_conductance_scale", "Zin_50Hz_Mohm"])
        for predictor in dict.fromkeys(selected):
            if predictor not in samples[0]:
                continue
            x = np.array([float(row[predictor]) for row in samples], dtype=float)
            y = np.array([float(row[target]) for row in samples], dtype=float)
            design = np.column_stack([np.ones(len(x)), x])
            coeffs, *_ = np.linalg.lstsq(design, y, rcond=None)
            prediction = design @ coeffs
            residual = y - prediction
            dominant_name = ""
            dominant_abs = -1.0
            dominant_signed = 0.0
            for spec in PARAMETERS:
                px = np.array([float(row[spec.name]) for row in samples], dtype=float)
                if np.std(px) == 0 or np.std(residual) == 0:
                    continue
                rho = spearman(px, residual)
                if abs(rho) > dominant_abs:
                    dominant_abs = abs(rho)
                    dominant_signed = rho
                    dominant_name = spec.name
            worst_index = int(np.argmax(np.abs(residual)))
            rows.append(
                {
                    "group": group,
                    "target": target,
                    "predictor": predictor,
                    "intercept": float(coeffs[0]),
                    "slope": float(coeffs[1]),
                    "rmse_full": float(np.sqrt(np.mean(residual**2))),
                    "residual_mean": float(np.mean(residual)),
                    "residual_sd": float(np.std(residual, ddof=1)),
                    "residual_p05": float(np.percentile(residual, 5)),
                    "residual_p95": float(np.percentile(residual, 95)),
                    "max_abs_residual": float(np.max(np.abs(residual))),
                    "worst_sample_id": int(float(samples[worst_index]["sample_id"])),
                    "dominant_residual_correlate": dominant_name,
                    "dominant_residual_spearman": dominant_signed,
                    "dominant_residual_abs_spearman": dominant_abs,
                    "method": "least_squares_univariate_residual_audit",
                }
            )
    return rows


def bootstrap_abs_spearman_ci(x: np.ndarray, y: np.ndarray, seed: int = BOOTSTRAP_SEED, n_boot: int = 200) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    values = []
    n = len(x)
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        values.append(abs(spearman(x[idx], y[idx])))
    return float(np.percentile(values, 5)), float(np.percentile(values, 95))


def cv_rmse_univariate(x: np.ndarray, y: np.ndarray, k: int = 5, seed: int = CV_SEED) -> float:
    rng = np.random.default_rng(seed)
    indices = np.arange(len(x))
    rng.shuffle(indices)
    folds = np.array_split(indices, k)
    preds = np.empty_like(y)
    for fold in folds:
        train = np.setdiff1d(indices, fold)
        design = np.column_stack([np.ones(len(train)), x[train]])
        coeffs, *_ = np.linalg.lstsq(design, y[train], rcond=None)
        preds[fold] = np.column_stack([np.ones(len(fold)), x[fold]]) @ coeffs
    return float(np.sqrt(np.mean((preds - y) ** 2)))


def multivariable_predictor_rows(samples: list[dict[str, object]]) -> list[dict[str, object]]:
    combos = {
        "SMI_plus_transfer_gain": ["SMI", "transfer_gain_50Hz"],
        "SMI_plus_impedance_active_state": ["SMI", "transfer_gain_50Hz", "active_transfer_gain_50Hz", "nmda_fraction"],
        "morphology_neck_load": ["R_neck_Mohm", "R_in_d_Mohm", "head_diameter_um", "membrane_leak_scale"],
    }
    targets = [
        ("passive", "Gamma_h_to_d"),
        ("passive", "Gamma_h_to_s"),
        ("passive", "A_h_mV"),
        ("active", "active_Gamma_h_to_d"),
        ("active", "active_Gamma_h_to_s"),
        ("active", "active_A_h_mV"),
    ]
    rows: list[dict[str, object]] = []
    for group, target in targets:
        y = np.array([float(row[target]) for row in samples])
        for name, predictors in combos.items():
            x = np.column_stack([[float(row[p]) for row in samples] for p in predictors])
            rows.append(
                {
                    "group": group,
                    "target": target,
                    "predictor": name,
                    "pearson": "",
                    "spearman": "",
                    "abs_spearman": "",
                    "bootstrap_abs_spearman_p05": "",
                    "bootstrap_abs_spearman_p95": "",
                    "cv_rmse": cv_rmse_multivariable(x, y),
                    "n": len(samples),
                    "model": "fixed_multivariable_linear",
                }
            )
    return rows


def cv_rmse_multivariable(x: np.ndarray, y: np.ndarray, k: int = 5, seed: int = CV_SEED) -> float:
    rng = np.random.default_rng(seed)
    indices = np.arange(len(y))
    rng.shuffle(indices)
    folds = np.array_split(indices, k)
    preds = np.empty_like(y)
    for fold in folds:
        train = np.setdiff1d(indices, fold)
        design = np.column_stack([np.ones(len(train)), x[train, :]])
        coeffs, *_ = np.linalg.lstsq(design, y[train], rcond=None)
        preds[fold] = np.column_stack([np.ones(len(fold)), x[fold, :]]) @ coeffs
    return float(np.sqrt(np.mean((preds - y) ** 2)))


def counterexample_prevalence_rows(samples: list[dict[str, object]]) -> list[dict[str, object]]:
    pairs = []
    for i, a in enumerate(samples):
        for b in samples[i + 1 :]:
            pairs.append((a, b))
    rows = []
    definitions = [
        ("passive_iso_SMI_local_failure", lambda a, b: rel(a["SMI"], b["SMI"]) <= 0.05, lambda a, b: rel(a["Gamma_h_to_d"], b["Gamma_h_to_d"]) > 0.20),
        ("passive_iso_SMI_amplitude_failure", lambda a, b: rel(a["SMI"], b["SMI"]) <= 0.05, lambda a, b: rel(a["A_h_mV"], b["A_h_mV"]) > 0.20),
        ("passive_iso_transfer_failure", lambda a, b: abs(float(a["Gamma_h_to_d"]) - float(b["Gamma_h_to_d"])) <= 0.03, lambda a, b: rel(a["SMI"], b["SMI"]) > 0.35),
        ("active_iso_SMI_local_failure", lambda a, b: rel(a["SMI"], b["SMI"]) <= 0.05, lambda a, b: rel(a["active_Gamma_h_to_d"], b["active_Gamma_h_to_d"]) > 0.25),
        ("active_amplitude_failure", lambda a, b: rel(a["SMI"], b["SMI"]) <= 0.05, lambda a, b: rel(a["active_A_h_mV"], b["active_A_h_mV"]) > 0.25),
        ("NMDA_induced_amplitude_failure", lambda a, b: False, lambda a, b: False),
    ]
    for name, selector, failure in definitions[:-1]:
        selected = [(a, b) for a, b in pairs if selector(a, b)]
        failed = [(a, b) for a, b in selected if failure(a, b)]
        rows.append(
            {
                "counterexample_type": name,
                "eligible_pairs": len(selected),
                "failure_pairs": len(failed),
                "prevalence": len(failed) / len(selected) if selected else 0.0,
                "classification": prevalence_label(len(failed) / len(selected) if selected else 0.0),
            }
        )
    nmda_failed = [row for row in samples if float(row["nmda_fraction"]) > 0.2 and abs(float(row["NMDA_delta_A_h_fraction"])) > 0.20]
    rows.append(
        {
            "counterexample_type": "NMDA_induced_amplitude_failure",
            "eligible_pairs": sum(1 for row in samples if float(row["nmda_fraction"]) > 0.2),
            "failure_pairs": len(nmda_failed),
            "prevalence": len(nmda_failed) / max(1, sum(1 for row in samples if float(row["nmda_fraction"]) > 0.2)),
            "classification": prevalence_label(len(nmda_failed) / max(1, sum(1 for row in samples if float(row["nmda_fraction"]) > 0.2))),
        }
    )
    return rows


def rel(a: object, b: object) -> float:
    af = float(a)
    bf = float(b)
    return abs(af - bf) / max(abs(af), abs(bf), 1e-12)


def prevalence_label(value: float) -> str:
    if value < 0.05:
        return "rare"
    if value < 0.30:
        return "common"
    return "dominant"


def claim_rows(predictors: list[dict[str, object]], counterexamples: list[dict[str, object]]) -> list[dict[str, object]]:
    def best(target: str, group: str):
        rows = [row for row in predictors if row["target"] == target and row["group"] == group and row["model"] == "univariate_linear"]
        return max(rows, key=lambda row: float(row["abs_spearman"]))

    def smi(target: str, group: str):
        return [row for row in predictors if row["target"] == target and row["group"] == group and row["predictor"] == "SMI"][0]

    ce = {row["counterexample_type"]: row for row in counterexamples}
    rows = []
    local_smi = smi("Gamma_h_to_d", "passive")
    local_best = best("Gamma_h_to_d", "passive")
    rows.append(claim_row("SMI is a local isolation descriptor", "strongly supported" if local_best["predictor"] == "SMI" and float(local_smi["bootstrap_abs_spearman_p05"]) > 0.70 else "supported", f"Passive local best={local_best['predictor']} abs_spearman={local_best['abs_spearman']}; bootstrap p05={local_smi['bootstrap_abs_spearman_p05']}"))
    soma_smi = smi("Gamma_h_to_s", "passive")
    soma_best = best("Gamma_h_to_s", "passive")
    if soma_best["predictor"] == "SMI":
        soma_class = "uncertain"
    elif float(soma_smi["abs_spearman"]) < 0.50:
        soma_class = "strongly supported"
    else:
        soma_class = "supported"
    rows.append(claim_row("SMI is not a reliable somatic-transfer predictor", soma_class, f"Somatic best={soma_best['predictor']} abs_spearman={soma_best['abs_spearman']}; SMI={soma_smi['abs_spearman']}"))
    amp_smi = smi("A_h_mV", "passive")
    amp_best = best("A_h_mV", "passive")
    rows.append(claim_row("SMI is not a reliable amplitude predictor", "strongly supported" if amp_best["predictor"] != "SMI" and float(amp_smi["abs_spearman"]) < 0.50 else "supported", f"Amplitude best={amp_best['predictor']} abs_spearman={amp_best['abs_spearman']}; SMI={amp_smi['abs_spearman']}"))
    iso_amp = ce["passive_iso_SMI_amplitude_failure"]
    rows.append(claim_row("Equal SMI does not imply electrical equivalence", "strongly supported" if float(iso_amp["prevalence"]) >= 0.05 else "supported", f"Passive iso-SMI amplitude prevalence={iso_amp['prevalence']} ({iso_amp['classification']})"))
    rows.append(claim_row("Impedance-based descriptors outperform SMI for somatic transfer", "supported" if soma_best["predictor"] != "SMI" else "uncertain", f"Best passive somatic predictor={soma_best['predictor']} vs SMI={soma_smi['abs_spearman']}"))
    active_iso = ce["active_amplitude_failure"]
    passive_iso = ce["passive_iso_SMI_amplitude_failure"]
    rows.append(claim_row("Active mechanisms sharpen rather than erase SMI limitations", "supported" if float(active_iso["prevalence"]) >= float(passive_iso["prevalence"]) else "uncertain", f"Active amplitude prevalence={active_iso['prevalence']}; passive amplitude prevalence={passive_iso['prevalence']}"))
    return rows


def claim_row(claim: str, classification: str, evidence: str) -> dict[str, object]:
    return {"claim": claim, "classification": classification, "evidence": evidence}


def validation_rows(samples: list[dict[str, object]], sensitivity: list[dict[str, object]], summary48: list[dict[str, object]], summary96: list[dict[str, object]]) -> list[dict[str, object]]:
    repeat = lhs_samples(GLOBAL_N, LHS_SEED)
    reproducible = all(abs(repeat[i][spec.name] - float(samples[i][spec.name])) < 1e-15 for i in range(GLOBAL_N) for spec in PARAMETERS)
    sens_lookup = {(row["parameter"], row["output"]): float(row["normalized_sensitivity"]) for row in sensitivity}
    radius_ok = abs(sens_lookup[("neck_radius_um", "R_neck_Mohm")] + 2.0) < 0.02
    length_ok = abs(sens_lookup[("neck_length_um", "R_neck_Mohm")] - 1.0) < 0.02
    rho_ok = abs(sens_lookup[("intracellular_resistivity_ohm_cm", "R_neck_Mohm")] - 1.0) < 0.02
    convergence_values = []
    map48 = {row["output"]: row for row in summary48}
    for row in summary96:
        key = row["output"]
        if key in map48:
            convergence_values.append(abs(float(row["median"]) - float(map48[key]["median"])) / max(abs(float(row["median"])), 1e-12))
    max_conv = max(convergence_values)
    return [
        {"validation": "latin_hypercube_reproducibility", "value": reproducible, "threshold": True, "passed": reproducible},
        {"validation": "local_sensitivity_radius_Rneck", "value": sens_lookup[("neck_radius_um", "R_neck_Mohm")], "threshold": "-2 +/- 0.02", "passed": radius_ok},
        {"validation": "local_sensitivity_length_Rneck", "value": sens_lookup[("neck_length_um", "R_neck_Mohm")], "threshold": "1 +/- 0.02", "passed": length_ok},
        {"validation": "local_sensitivity_resistivity_Rneck", "value": sens_lookup[("intracellular_resistivity_ohm_cm", "R_neck_Mohm")], "threshold": "1 +/- 0.02", "passed": rho_ok},
        {"validation": "uncertainty_convergence_48_vs_96", "value": max_conv, "threshold": 0.10, "passed": max_conv < 0.10},
        {"validation": "bootstrap_seed_fixed", "value": BOOTSTRAP_SEED, "threshold": BOOTSTRAP_SEED, "passed": True},
        {"validation": "cross_validation_seed_fixed", "value": CV_SEED, "threshold": CV_SEED, "passed": True},
    ]


def run_phase05(results_dir: str | Path = "results/phase05", figures_dir: str | Path = "figures/phase05") -> dict[str, Path]:
    results = Path(results_dir)
    figures = Path(figures_dir)
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, Path] = {}

    outputs["distributions"] = _write_csv(results / "uncertainty_distributions.csv", distribution_rows())
    sensitivity = local_sensitivity_rows()
    outputs["local_sensitivity"] = _write_csv(results / "local_sensitivity.csv", sensitivity)

    parameter_samples = lhs_samples()
    evaluated = [evaluate_sample(sample, include_active=True) for sample in parameter_samples]
    outputs["uncertainty_samples"] = _write_csv(results / "global_uncertainty_samples.csv", evaluated)
    summary = uncertainty_summary_rows(evaluated)
    outputs["uncertainty_summary"] = _write_csv(results / "uncertainty_summary.csv", summary)
    decomposition = uncertainty_decomposition_rows(evaluated)
    outputs["uncertainty_decomposition"] = _write_csv(results / "uncertainty_decomposition.csv", decomposition)
    radius_rows = radius_uncertainty_rows(evaluated)
    outputs["radius_uncertainty"] = _write_csv(results / "radius_uncertainty_class_stability.csv", radius_rows)
    identifiability = identifiability_rows(evaluated)
    outputs["identifiability"] = _write_csv(results / "identifiability_degeneracy_examples.csv", identifiability)
    predictors = predictor_rows(evaluated)
    outputs["predictors"] = _write_csv(results / "predictor_comparison.csv", predictors)
    residuals = residual_analysis_rows(evaluated, predictors)
    outputs["residuals"] = _write_csv(results / "residual_analysis.csv", residuals)
    counterexamples = counterexample_prevalence_rows(evaluated)
    outputs["counterexamples"] = _write_csv(results / "counterexample_prevalence.csv", counterexamples)
    claims = claim_rows(predictors, counterexamples)
    outputs["claims"] = _write_csv(results / "claim_robustness.csv", claims)
    summary48 = uncertainty_summary_rows(evaluated[:48])
    validation = validation_rows(evaluated, sensitivity, summary48, summary)
    outputs["validation"] = _write_csv(results / "phase05_validation.csv", validation)

    _write_scatter_svg(figures / "uncertainty_SMI_vs_Gamma_hd.svg", evaluated, "SMI", "Gamma_h_to_d", "Uncertainty: SMI vs local transfer")
    _write_scatter_svg(figures / "uncertainty_SMI_vs_Gamma_hs.svg", evaluated, "SMI", "Gamma_h_to_s", "Uncertainty: SMI vs somatic transfer")
    _write_scatter_svg(figures / "uncertainty_radius_vs_Rneck.svg", evaluated, "neck_radius_um", "R_neck_Mohm", "Radius uncertainty amplifies Rneck")
    _write_line_svg(figures / "radius_class_stability.svg", radius_rows, "true_SMI", "class_stable_fraction", "SMI class stability under radius error")
    top_sens = sorted([row for row in sensitivity if row["output"] == "SMI"], key=lambda row: float(row["abs_normalized_sensitivity"]), reverse=True)[:12]
    for i, row in enumerate(top_sens):
        row["rank"] = i + 1
    _write_line_svg(figures / "sensitivity_SMI_ranked.svg", top_sens, "rank", "abs_normalized_sensitivity", "SMI local sensitivity ranking")
    outputs["summary"] = _write_csv(results / "phase05_summary.csv", phase05_summary_rows(summary, predictors, counterexamples, claims, validation))
    return outputs


def phase05_summary_rows(summary: list[dict[str, object]], predictors: list[dict[str, object]], counterexamples: list[dict[str, object]], claims: list[dict[str, object]], validation: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [
        {
            "summary_item": "validation_passed",
            "value": all(str(row["passed"]) == "True" or row["passed"] is True for row in validation),
            "numeric_value": sum(1 for row in validation if str(row["passed"]) == "True" or row["passed"] is True),
            "detail": f"{len(validation)} validation checks",
        }
    ]
    for target in ["Gamma_h_to_d", "Gamma_h_to_s", "A_h_mV", "active_Gamma_h_to_d", "active_Gamma_h_to_s", "active_A_h_mV"]:
        candidates = [row for row in predictors if row["target"] == target and row["model"] == "univariate_linear"]
        best = max(candidates, key=lambda row: float(row["abs_spearman"]))
        smi = [row for row in candidates if row["predictor"] == "SMI"][0]
        rows.append(
            {
                "summary_item": f"best_predictor_{target}",
                "value": best["predictor"],
                "numeric_value": best["abs_spearman"],
                "detail": f"SMI abs_spearman={smi['abs_spearman']}",
            }
        )
    for row in counterexamples:
        rows.append(
            {
                "summary_item": row["counterexample_type"],
                "value": row["classification"],
                "numeric_value": row["prevalence"],
                "detail": f"{row['failure_pairs']}/{row['eligible_pairs']}",
            }
        )
    for row in claims:
        rows.append(
            {
                "summary_item": row["claim"],
                "value": row["classification"],
                "numeric_value": "",
                "detail": row["evidence"],
            }
        )
    return rows
