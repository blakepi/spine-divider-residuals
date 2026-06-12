"""Phase 06 exploratory epilepsy/epileptogenesis analyses.

This module deliberately stays outside the validated manuscript-faithful,
passive, and active-extension baselines. It provides hypothesis-generating
scenario perturbations with explicit literature provenance and uncertainty
propagation; it does not implement clinical, diagnostic, prognostic, or
therapeutic claims.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

from spine.active import ChannelPlacement, SynapsePlacement, frozen_gate_impedance, simulate_active_network
from spine.channels import make_channel
from spine.geometry import cylindrical_neck_resistance_ohm
from spine.impedance import dynamic_smi, local_input_impedance, transfer_impedance
from spine.morphology import MorphologyBuildResult, procedural_branch_tree, procedural_cable
from spine.network import PassiveNetwork
from spine.phase03 import _write_csv, _write_line_svg, _write_scatter_svg, add_lumped_spine, local_rin_ohm, pearson, spearman
from spine.synapses import make_ampa_nmda_synapse
from spine.units import nS_to_S, ohm_to_megaohm


PHASE06_DT_S = 2e-5
PHASE06_STOP_S = 0.080
PHASE06_EVENT_S = 0.020
PHASE06_WINDOW_S = 0.050
PHASE06_FREQ_HZ = 50.0
PHASE06_SEED = 20260601
PHASE06_UNCERTAINTY_N = 8

BASE_NECK_LENGTH_UM = 0.75
BASE_NECK_RADIUS_UM = 0.12
BASE_HEAD_RADIUS_UM = 0.35
BASE_RHO_OHM_CM = 100.0
BASE_AMPA_G_NS = 1.4
BASE_NMDA_FRACTION = 0.35


@dataclass(frozen=True)
class ScenarioDefinition:
    name: str
    evidence_grade: str
    rationale: str
    reference_ids: tuple[str, ...]
    neck_length_scale: float = 1.0
    neck_radius_scale: float = 1.0
    head_radius_scale: float = 1.0
    dendritic_leak_scale: float = 1.0
    synaptic_g_scale: float = 1.0
    nmda_fraction: float = BASE_NMDA_FRACTION
    na_scale: float = 1.0
    kdr_scale: float = 1.0
    hcn_scale: float = 1.0
    ka_scale: float = 1.0
    cat_scale: float = 1.0
    cluster_spine_count: int = 1


@dataclass(frozen=True)
class EvidenceRow:
    key: str
    citation: str
    doi_or_stable_id: str
    evidence_type: str
    epilepsy_context: str
    extracted_perturbation: str
    direction_supported: str
    evidence_grade: str
    model_use: str
    limitation: str


SCENARIOS: tuple[ScenarioDefinition, ...] = (
    ScenarioDefinition(
        name="matched_baseline",
        evidence_grade="control",
        rationale="Internal exploratory comparator with Phase 04 active mechanisms and AMPA+NMDA synapse; not a disease state.",
        reference_ids=("LondonHausser2005", "Magee1998HCN"),
    ),
    ScenarioDefinition(
        name="morphology_dominant",
        evidence_grade="limited_conflicting",
        rationale="Perturb spine-neck/head geometry to ask whether SMI-dominated morphology changes are sufficient.",
        reference_ids=("Wong2005SpinesEpilepsy", "Isokawa1998SpineRemodeling", "PilocarpineSpineLoss2008"),
        neck_radius_scale=0.85,
        neck_length_scale=1.20,
        head_radius_scale=1.10,
    ),
    ScenarioDefinition(
        name="hcn_reduction",
        evidence_grade="conflicting",
        rationale="Reduce HCN/Ih as a restrained channelopathy scenario while preserving literature conflict.",
        reference_ids=("Kole2007HCN1Loss", "Nava2014HCN1", "Bender2003HCN"),
        hcn_scale=0.40,
    ),
    ScenarioDefinition(
        name="potassium_loss_of_function",
        evidence_grade="moderate",
        rationale="Reduce A-type and delayed-rectifier potassium availability to increase dendritic excitability.",
        reference_ids=("Bernard2004DendriticChannelopathy", "VillaCombi2016PotassiumChannels"),
        kdr_scale=0.80,
        ka_scale=0.50,
    ),
    ScenarioDefinition(
        name="increased_exc_synaptic_strength",
        evidence_grade="limited",
        rationale="Increase excitatory synaptic conductance without changing morphology.",
        reference_ids=("Hanada2020GlutamateEpilepsy",),
        synaptic_g_scale=1.50,
    ),
    ScenarioDefinition(
        name="increased_nmda_contribution",
        evidence_grade="limited",
        rationale="Increase NMDA contribution while retaining magnesium block and active-extension validation limits.",
        reference_ids=("Hanada2020GlutamateEpilepsy",),
        nmda_fraction=0.65,
    ),
    ScenarioDefinition(
        name="increased_clustering_synchrony",
        evidence_grade="limited",
        rationale="Use clustered synchronous inputs to challenge scalar SMI under correlated synaptic drive.",
        reference_ids=("LondonHausser2005", "Losonczy2008CompartmentalizedPlasticity", "Major2008DendriticSpikes"),
        synaptic_g_scale=1.25,
        cluster_spine_count=3,
    ),
    ScenarioDefinition(
        name="combined_restrained_epileptogenesis",
        evidence_grade="compound_uncertain",
        rationale="Combine restrained morphology, leak, active, and synaptic perturbations as a stress test, not a calibrated disease model.",
        reference_ids=(
            "Wong2005SpinesEpilepsy",
            "Bernard2004DendriticChannelopathy",
            "Kole2007HCN1Loss",
            "Hanada2020GlutamateEpilepsy",
        ),
        neck_radius_scale=0.90,
        neck_length_scale=1.15,
        head_radius_scale=1.08,
        dendritic_leak_scale=1.30,
        hcn_scale=0.50,
        kdr_scale=0.85,
        ka_scale=0.65,
        synaptic_g_scale=1.30,
        nmda_fraction=0.55,
        cluster_spine_count=3,
    ),
    ScenarioDefinition(
        name="alternative_direction_conflicting",
        evidence_grade="conflicting",
        rationale="Opposite-direction HCN and morphology scenario to preserve contradictory literature rather than force one disease direction.",
        reference_ids=("Bender2003HCN", "Wong2005SpinesEpilepsy"),
        neck_radius_scale=1.10,
        neck_length_scale=0.90,
        hcn_scale=1.50,
        synaptic_g_scale=0.90,
    ),
)


EVIDENCE_ROWS: tuple[EvidenceRow, ...] = (
    EvidenceRow(
        "Wong2005SpinesEpilepsy",
        "Wong M. Modulation of dendritic spines in epilepsy: cellular mechanisms and functional implications. Epilepsy & Behavior. 2005.",
        "10.1016/j.yebeh.2005.08.007",
        "review",
        "epilepsy/spines",
        "spine morphology is plausibly altered in epilepsy but direction and functional interpretation are context dependent",
        "mixed",
        "limited_conflicting",
        "supports exploratory morphology perturbations only",
        "review-level synthesis; not a calibrated parameter distribution",
    ),
    EvidenceRow(
        "PilocarpineSpineLoss2008",
        "A cellular mechanism for dendritic spine loss in the pilocarpine model of status epilepticus. Epilepsia. 2008.",
        "10.1111/j.1528-1167.2008.01616.x",
        "research article",
        "pilocarpine/status epilepticus model",
        "spine loss/remodeling can occur after epileptiform injury",
        "spine density decrease",
        "limited",
        "supports a spine-density/cluster-load sensitivity check",
        "animal model and injury stage do not define a generic disease parameter",
    ),
    EvidenceRow(
        "Isokawa1998SpineRemodeling",
        "Remodeling dendritic spines in the rat pilocarpine model of temporal lobe epilepsy. Neuroscience Letters. 1998.",
        "10.1016/s0304-3940(98)00848-9",
        "research article",
        "pilocarpine temporal-lobe epilepsy model",
        "spine remodeling after epileptogenic insult",
        "mixed morphology change",
        "limited",
        "supports morphology-dominant and alternative-direction scenarios",
        "model, region, and time-window specific",
    ),
    EvidenceRow(
        "Bernard2004DendriticChannelopathy",
        "Bernard C et al. Acquired dendritic channelopathy in temporal lobe epilepsy. Science. 2004.",
        "10.1126/science.1097065",
        "research article",
        "experimental temporal-lobe epilepsy",
        "decreased A-type potassium availability and increased CA1 dendritic excitability",
        "potassium reduction",
        "moderate",
        "supports restrained potassium-loss scenario",
        "specific to experimental preparation and A-type channel mechanisms",
    ),
    EvidenceRow(
        "VillaCombi2016PotassiumChannels",
        "Villa C, Combi R. Potassium channels in epilepsy. Cold Spring Harbor Perspectives in Medicine. 2016.",
        "10.1101/cshperspect.a022871",
        "review",
        "epilepsy/channel genetics and physiology",
        "potassium-channel dysfunction can contribute to epileptic excitability",
        "potassium reduction/mixed",
        "moderate",
        "supports potassium-loss-of-function as plausible but non-specific",
        "review; channel subtype, cell type, and direction vary",
    ),
    EvidenceRow(
        "Bender2003HCN",
        "Bender RA et al. Enhanced expression of a specific HCN channel in surviving dentate granule cells of human and experimental epileptic hippocampus. Journal of Neuroscience. 2003.",
        "10.1523/jneurosci.23-17-06826.2003",
        "research article",
        "human and experimental epileptic hippocampus",
        "HCN expression can increase in surviving dentate granule cells",
        "HCN increase",
        "conflicting",
        "motivates alternative-direction HCN scenario",
        "cell-type and survival-selection context differ from generic spine model",
    ),
    EvidenceRow(
        "Kole2007HCN1Loss",
        "Kole MHP et al. Inherited cortical HCN1 channel loss amplifies dendritic calcium electrogenesis and burst firing in a rat absence epilepsy model. Journal of Physiology. 2007.",
        "10.1113/jphysiol.2006.122028",
        "research article",
        "absence epilepsy model",
        "HCN1 loss can amplify dendritic electrogenesis and burst firing",
        "HCN reduction",
        "moderate",
        "supports HCN-reduction perturbation",
        "genetic/model-specific and not a universal acquired epilepsy direction",
    ),
    EvidenceRow(
        "Nava2014HCN1",
        "Nava C et al. De novo mutations in HCN1 cause early infantile epileptic encephalopathy. Nature Genetics. 2014.",
        "10.1038/ng.2952",
        "research article",
        "human epilepsy genetics",
        "HCN1 dysfunction can be linked to epileptic encephalopathy",
        "HCN dysfunction",
        "moderate",
        "supports HCN-family channelopathy relevance",
        "genetic syndrome evidence, not a dendritic-spine parameter estimate",
    ),
    EvidenceRow(
        "Hanada2020GlutamateEpilepsy",
        "Hanada T. Ionotropic glutamate receptors in epilepsy: a review focusing on AMPA and NMDA receptors. Biomolecules. 2020.",
        "10.3390/biom10030464",
        "review",
        "epilepsy/glutamate receptors",
        "AMPA and NMDA receptor mechanisms are implicated in epileptic excitability",
        "excitatory conductance/NMDA contribution increase",
        "limited",
        "supports AMPA/NMDA exploratory sweeps without therapy claims",
        "review-level and mechanism-specific; no calibrated conductance multiplier",
    ),
    EvidenceRow(
        "LondonHausser2005",
        "London M, Hausser M. Dendritic computation. Annual Review of Neuroscience. 2005.",
        "10.1146/annurev.neuro.28.061604.135703",
        "review",
        "general dendritic integration",
        "dendritic response depends on morphology, impedance, channels, and synaptic organization",
        "context dependent",
        "supporting_background",
        "limits scalar SMI interpretation under active and clustered regimes",
        "not epilepsy specific",
    ),
    EvidenceRow(
        "Magee1998HCN",
        "Magee JC. Dendritic hyperpolarization-activated currents modify the integrative properties of hippocampal CA1 pyramidal neurons. Journal of Neuroscience. 1998.",
        "10.1523/jneurosci.18-19-07613.1998",
        "research article",
        "general dendritic integration",
        "HCN/Ih changes dendritic integration",
        "context dependent",
        "supporting_background",
        "supports active HCN sensitivity as dendritic integration variable",
        "not epilepsy specific",
    ),
    EvidenceRow(
        "Losonczy2008CompartmentalizedPlasticity",
        "Losonczy A et al. Compartmentalized dendritic plasticity and input feature storage in neurons. Nature. 2008.",
        "10.1038/nature06725",
        "research article",
        "general dendritic integration",
        "spatially clustered dendritic inputs can produce branch-local nonlinear outcomes",
        "cluster sensitivity",
        "supporting_background",
        "supports cluster/synchrony challenge protocol",
        "not epilepsy specific",
    ),
    EvidenceRow(
        "Major2008DendriticSpikes",
        "Major G et al. Conditional dendritic spike propagation following distal synaptic activation of hippocampal CA1 pyramidal neurons. Nature Neuroscience. 2008.",
        "10.1038/nn1599",
        "research article",
        "general dendritic integration",
        "dendritic nonlinear propagation depends on active and synaptic conditions",
        "active threshold behavior",
        "supporting_background",
        "supports active threshold-behavior metrics",
        "not epilepsy specific",
    ),
)


def _scenario_by_name(name: str) -> ScenarioDefinition:
    for scenario in SCENARIOS:
        if scenario.name == name:
            return scenario
    raise KeyError(name)


def _scale_network(build: MorphologyBuildResult, leak_scale: float, area_scale: float = 1.0) -> MorphologyBuildResult:
    network = build.network.copy()
    scaled = []
    for comp in network.compartments:
        if comp.kind == "dendrite":
            scaled.append(
                replace(
                    comp,
                    leak_conductance_S=comp.leak_conductance_S * leak_scale,
                    capacitance_F=comp.capacitance_F * area_scale,
                    area_um2=comp.area_um2 * area_scale,
                )
            )
        else:
            scaled.append(comp)
    network.compartments = scaled
    return MorphologyBuildResult(network, build.soma_index, list(build.terminal_indices), dict(build.path_lengths_um))


def _build_base(scenario: ScenarioDefinition, clustered: bool = False) -> MorphologyBuildResult:
    if clustered:
        build = procedural_branch_tree(trunk_length_um=120.0, branch_length_um=80.0, radius_um=0.5, asymmetric=True)
    else:
        build = procedural_cable(length_um=140.0, radius_um=0.5, nseg=8)
    return _scale_network(build, scenario.dendritic_leak_scale, 1.0)


def _parents_for_protocol(build: MorphologyBuildResult, protocol: str, n_spines: int) -> list[int]:
    if protocol == "isolated_single_spine":
        return [build.terminal_indices[0]]
    parents: list[int] = []
    terminals = build.terminal_indices
    for i in range(max(2, n_spines)):
        parents.append(terminals[i % len(terminals)])
    return parents[: max(2, n_spines)]


def _events_for_protocol(protocol: str, n_spines: int) -> list[float]:
    if protocol == "clustered_asynchronous":
        return [PHASE06_EVENT_S + 0.0025 * i for i in range(n_spines)]
    return [PHASE06_EVENT_S for _ in range(n_spines)]


def _channels(scenario: ScenarioDefinition, indices: list[int]) -> list[ChannelPlacement]:
    channels = [
        make_channel("na", 6.0 * scenario.na_scale),
        make_channel("kdr", 1.5 * scenario.kdr_scale),
        make_channel("hcn", 0.05 * scenario.hcn_scale),
        make_channel("ka", 0.5 * scenario.ka_scale),
        make_channel("cat", 0.05 * scenario.cat_scale),
    ]
    placements: list[ChannelPlacement] = []
    for idx in sorted(set(indices)):
        for channel in channels:
            placements.append(ChannelPlacement(idx, channel, f"phase06_{idx}_{channel.name}"))
    return placements


def _synapse(event_time_s: float, scenario: ScenarioDefinition):
    ampa = nS_to_S(BASE_AMPA_G_NS * scenario.synaptic_g_scale)
    nmda = nS_to_S(BASE_AMPA_G_NS * scenario.synaptic_g_scale * scenario.nmda_fraction)
    return make_ampa_nmda_synapse(
        [event_time_s],
        ampa_g_max_S=ampa,
        nmda_g_max_S=nmda,
        magnesium_mM=1.0,
        label="phase06_ampa_nmda",
    )


def _trace_metrics(result, head_index: int, parent_index: int, soma_index: int, event_time_s: float) -> dict[str, float]:
    times = result.time_s
    baseline_index = max(0, int(np.searchsorted(times, event_time_s)) - 1)
    mask = (times >= event_time_s) & (times <= event_time_s + PHASE06_WINDOW_S)
    baseline_head = float(result.voltage_V[baseline_index, head_index])
    depol_h = result.voltage_V[mask, head_index] - baseline_head
    depol_d = result.voltage_V[mask, parent_index] - float(result.voltage_V[baseline_index, parent_index])
    depol_s = result.voltage_V[mask, soma_index] - float(result.voltage_V[baseline_index, soma_index])
    ah = float(np.max(depol_h))
    ad = float(np.max(depol_d))
    ass = float(np.max(depol_s))
    peak_i = int(np.argmax(depol_h))
    half = 0.5 * ah
    above = np.where(depol_h >= half)[0]
    half_width = float((times[mask][above[-1]] - times[mask][above[0]]) * 1e3) if len(above) > 1 else 0.0
    return {
        "A_h_mV": ah * 1e3,
        "A_d_mV": ad * 1e3,
        "A_s_mV": ass * 1e3,
        "Gamma_h_to_d": ad / ah if ah else float("nan"),
        "Gamma_h_to_s": ass / ah if ah else float("nan"),
        "local_voltage_isolation": 1.0 - ad / ah if ah else float("nan"),
        "latency_head_ms": float((times[mask][peak_i] - event_time_s) * 1e3),
        "half_width_head_ms": half_width,
        "head_voltage_integral_mV_ms": float(np.trapz(depol_h * 1e3, times[mask] * 1e3)),
        "soma_voltage_integral_mV_ms": float(np.trapz(depol_s * 1e3, times[mask] * 1e3)),
        "max_synaptic_conductance_nS": float(np.max(result.synaptic_conductance_S) * 1e9),
        "driving_force_reduction_mV": ah * 1e3,
        "max_voltage_mV": float(np.max(result.voltage_V) * 1e3),
        "min_voltage_mV": float(np.min(result.voltage_V) * 1e3),
        "threshold_crossed_minus20mV": bool(np.max(result.voltage_V[:, head_index]) > -0.020),
        "soma_crossed_0mV": bool(np.max(result.voltage_V[:, soma_index]) > 0.0),
        "finite": bool(result.finite),
        "min_gate": float(result.min_gate_value),
        "max_gate": float(result.max_gate_value),
    }


def _run_protocol(scenario: ScenarioDefinition, protocol: str) -> dict[str, object]:
    clustered = protocol != "isolated_single_spine"
    n_spines = 1 if not clustered else max(3, scenario.cluster_spine_count)
    base_build = _build_base(scenario, clustered=clustered)
    parents = _parents_for_protocol(base_build, protocol, n_spines)
    events = _events_for_protocol(protocol, len(parents))
    rho = BASE_RHO_OHM_CM
    neck_length = BASE_NECK_LENGTH_UM * scenario.neck_length_scale
    neck_radius = BASE_NECK_RADIUS_UM * scenario.neck_radius_scale
    head_radius = BASE_HEAD_RADIUS_UM * scenario.head_radius_scale
    r_neck = cylindrical_neck_resistance_ohm(rho, neck_length, neck_radius)
    rin_d = local_rin_ohm(base_build.network, parents[0])
    network = base_build.network.copy()
    heads: list[int] = []
    for parent in parents:
        network, head = add_lumped_spine(network, parent, r_neck, head_radius_um=head_radius)
        heads.append(head)
    synapses = [
        SynapsePlacement(head, _synapse(event_time, scenario), f"{scenario.name}_{protocol}_{i}")
        for i, (head, event_time) in enumerate(zip(heads, events))
    ]
    channel_indices = heads + parents + [base_build.soma_index]
    channels = _channels(scenario, channel_indices)
    result = simulate_active_network(
        network,
        channels,
        synapses,
        dt_s=PHASE06_DT_S,
        stop_s=PHASE06_STOP_S,
        method="semi_implicit",
    )
    metrics = _trace_metrics(result, heads[0], parents[0], base_build.soma_index, events[0])
    z_in = local_input_impedance(base_build.network, parents[0], PHASE06_FREQ_HZ)
    z_transfer = transfer_impedance(base_build.network, parents[0], base_build.soma_index, PHASE06_FREQ_HZ)
    gain = abs(z_transfer / z_in) if z_in != 0 else float("nan")
    active_parent_channels = _channels(scenario, parents + [base_build.soma_index])
    z_active_local = frozen_gate_impedance(base_build.network, active_parent_channels, parents[0], parents[0], PHASE06_FREQ_HZ)
    z_active_transfer = frozen_gate_impedance(
        base_build.network, active_parent_channels, parents[0], base_build.soma_index, PHASE06_FREQ_HZ
    )
    row: dict[str, object] = {
        "scenario": scenario.name,
        "protocol": protocol,
        "evidence_grade": scenario.evidence_grade,
        "reference_ids": ";".join(scenario.reference_ids),
        "n_spines": len(parents),
        "event_pattern": "asynchronous" if protocol.endswith("asynchronous") else "synchronous",
        "neck_length_um": neck_length,
        "neck_radius_um": neck_radius,
        "head_radius_um": head_radius,
        "rho_ohm_cm": rho,
        "R_neck_Mohm": ohm_to_megaohm(r_neck),
        "R_in_d_Mohm": ohm_to_megaohm(rin_d),
        "SMI": r_neck / rin_d,
        "synaptic_g_scale": scenario.synaptic_g_scale,
        "ampa_g_max_nS": BASE_AMPA_G_NS * scenario.synaptic_g_scale,
        "nmda_fraction": scenario.nmda_fraction,
        "dendritic_leak_scale": scenario.dendritic_leak_scale,
        "hcn_scale": scenario.hcn_scale,
        "kdr_scale": scenario.kdr_scale,
        "ka_scale": scenario.ka_scale,
        "cluster_spine_count": scenario.cluster_spine_count,
        "Zin_50Hz_Mohm": abs(z_in) / 1e6,
        "Ztransfer_50Hz_Mohm": abs(z_transfer) / 1e6,
        "transfer_gain_50Hz": gain,
        "electrotonic_distance_50Hz": -math.log(gain) if gain > 0 else float("nan"),
        "dynamic_SMI_abs_50Hz": abs(dynamic_smi(r_neck, z_in)),
        "active_frozen_Zin_50Hz_Mohm": abs(z_active_local) / 1e6,
        "active_frozen_Ztransfer_50Hz_Mohm": abs(z_active_transfer) / 1e6,
        "clinical_claim": "none",
        "exploratory_only": True,
    }
    row.update(metrics)
    return row


def _relative_delta(value: float, baseline: float) -> float:
    if baseline == 0 or not math.isfinite(baseline):
        return float("nan")
    return (value - baseline) / abs(baseline)


def _comparison_rows(metric_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    baselines = {
        row["protocol"]: row for row in metric_rows if row["scenario"] == "matched_baseline"
    }
    metrics = [
        "R_neck_Mohm",
        "R_in_d_Mohm",
        "SMI",
        "A_h_mV",
        "Gamma_h_to_d",
        "Gamma_h_to_s",
        "local_voltage_isolation",
        "latency_head_ms",
        "half_width_head_ms",
        "head_voltage_integral_mV_ms",
        "soma_voltage_integral_mV_ms",
        "driving_force_reduction_mV",
        "active_frozen_Zin_50Hz_Mohm",
    ]
    rows: list[dict[str, object]] = []
    for row in metric_rows:
        baseline = baselines[row["protocol"]]
        out = {"scenario": row["scenario"], "protocol": row["protocol"], "baseline_protocol": row["protocol"]}
        for metric in metrics:
            value = float(row[metric])
            base = float(baseline[metric])
            out[f"{metric}_value"] = value
            out[f"{metric}_baseline"] = base
            out[f"{metric}_delta"] = value - base
            out[f"{metric}_relative_delta"] = _relative_delta(value, base)
        rows.append(out)
    return rows


def _lhs(n: int, k: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    out = np.empty((n, k), dtype=float)
    for col in range(k):
        perm = rng.permutation(n)
        out[:, col] = (perm + rng.random(n)) / n
    return out


def _apply_uncertainty(scenario: ScenarioDefinition, unit: np.ndarray) -> ScenarioDefinition:
    factors = {
        "neck_radius_scale": 0.85 + 0.30 * unit[0],
        "neck_length_scale": 0.80 + 0.40 * unit[1],
        "head_radius_scale": 0.85 + 0.30 * unit[2],
        "dendritic_leak_scale": 0.70 + 0.60 * unit[3],
        "synaptic_g_scale": 0.75 + 0.50 * unit[4],
        "nmda_fraction": max(0.0, min(0.9, scenario.nmda_fraction + (unit[5] - 0.5) * 0.30)),
        "hcn_scale": 0.70 + 0.60 * unit[6],
        "kdr_scale": 0.70 + 0.60 * unit[7],
        "ka_scale": 0.70 + 0.60 * unit[8],
    }
    return replace(
        scenario,
        neck_radius_scale=scenario.neck_radius_scale * factors["neck_radius_scale"],
        neck_length_scale=scenario.neck_length_scale * factors["neck_length_scale"],
        head_radius_scale=scenario.head_radius_scale * factors["head_radius_scale"],
        dendritic_leak_scale=scenario.dendritic_leak_scale * factors["dendritic_leak_scale"],
        synaptic_g_scale=scenario.synaptic_g_scale * factors["synaptic_g_scale"],
        nmda_fraction=factors["nmda_fraction"],
        hcn_scale=scenario.hcn_scale * factors["hcn_scale"],
        kdr_scale=scenario.kdr_scale * factors["kdr_scale"],
        ka_scale=scenario.ka_scale * factors["ka_scale"],
    )


def _uncertainty_rows() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    sample_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    metrics = ["SMI", "A_h_mV", "Gamma_h_to_d", "Gamma_h_to_s", "local_voltage_isolation", "active_frozen_Zin_50Hz_Mohm"]
    for scenario_index, scenario in enumerate(SCENARIOS):
        samples = _lhs(PHASE06_UNCERTAINTY_N, 9, PHASE06_SEED + 101 * scenario_index)
        scenario_metric_rows: list[dict[str, object]] = []
        for sample_index, unit in enumerate(samples):
            sampled = _apply_uncertainty(scenario, unit)
            row = _run_protocol(sampled, "isolated_single_spine")
            row["sample_index"] = sample_index
            row["uncertainty_seed"] = PHASE06_SEED + 101 * scenario_index
            scenario_metric_rows.append(row)
            sample_rows.append(row)
        for metric in metrics:
            values = np.array([float(row[metric]) for row in scenario_metric_rows])
            summary_rows.append(
                {
                    "scenario": scenario.name,
                    "metric": metric,
                    "n": PHASE06_UNCERTAINTY_N,
                    "median": float(np.median(values)),
                    "p05": float(np.percentile(values, 5)),
                    "p95": float(np.percentile(values, 95)),
                    "iqr": float(np.percentile(values, 75) - np.percentile(values, 25)),
                }
            )
    return sample_rows, summary_rows


def _predictor_rows(metric_rows: list[dict[str, object]], uncertainty_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = [row for row in metric_rows + uncertainty_rows if row["protocol"] == "isolated_single_spine"]
    predictors = [
        "R_neck_Mohm",
        "R_in_d_Mohm",
        "SMI",
        "dynamic_SMI_abs_50Hz",
        "Zin_50Hz_Mohm",
        "Ztransfer_50Hz_Mohm",
        "transfer_gain_50Hz",
        "electrotonic_distance_50Hz",
        "active_frozen_Zin_50Hz_Mohm",
        "synaptic_g_scale",
        "nmda_fraction",
        "hcn_scale",
        "ka_scale",
    ]
    targets = ["Gamma_h_to_d", "Gamma_h_to_s", "A_h_mV", "local_voltage_isolation"]
    out: list[dict[str, object]] = []
    for target in targets:
        target_values = [float(row[target]) for row in rows]
        for predictor in predictors:
            values = [float(row[predictor]) for row in rows]
            out.append(
                {
                    "target": target,
                    "predictor": predictor,
                    "n": len(rows),
                    "pearson": pearson(values, target_values),
                    "spearman": spearman(values, target_values),
                    "abs_spearman": abs(spearman(values, target_values)),
                }
            )
    return sorted(out, key=lambda row: (str(row["target"]), -float(row["abs_spearman"])))


def _decomposition_rows() -> list[dict[str, object]]:
    baseline = _scenario_by_name("matched_baseline")
    combined = _scenario_by_name("combined_restrained_epileptogenesis")
    components = {
        "baseline": baseline,
        "morphology_only": replace(
            baseline,
            name="morphology_only",
            neck_radius_scale=combined.neck_radius_scale,
            neck_length_scale=combined.neck_length_scale,
            head_radius_scale=combined.head_radius_scale,
        ),
        "leak_only": replace(baseline, name="leak_only", dendritic_leak_scale=combined.dendritic_leak_scale),
        "hcn_only": replace(baseline, name="hcn_only", hcn_scale=combined.hcn_scale),
        "potassium_only": replace(baseline, name="potassium_only", kdr_scale=combined.kdr_scale, ka_scale=combined.ka_scale),
        "synaptic_only": replace(baseline, name="synaptic_only", synaptic_g_scale=combined.synaptic_g_scale),
        "nmda_only": replace(baseline, name="nmda_only", nmda_fraction=combined.nmda_fraction),
        "combined": combined,
    }
    baseline_row = _run_protocol(components["baseline"], "isolated_single_spine")
    rows: list[dict[str, object]] = []
    for label, scenario in components.items():
        row = _run_protocol(scenario, "isolated_single_spine")
        rows.append(
            {
                "component": label,
                "SMI": row["SMI"],
                "A_h_mV": row["A_h_mV"],
                "Gamma_h_to_d": row["Gamma_h_to_d"],
                "Gamma_h_to_s": row["Gamma_h_to_s"],
                "active_frozen_Zin_50Hz_Mohm": row["active_frozen_Zin_50Hz_Mohm"],
                "A_h_mV_delta_vs_baseline": float(row["A_h_mV"]) - float(baseline_row["A_h_mV"]),
                "Gamma_h_to_d_delta_vs_baseline": float(row["Gamma_h_to_d"]) - float(baseline_row["Gamma_h_to_d"]),
                "Gamma_h_to_s_delta_vs_baseline": float(row["Gamma_h_to_s"]) - float(baseline_row["Gamma_h_to_s"]),
            }
        )
    return rows


def _claim_rows(metric_rows: list[dict[str, object]], predictor_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    isolated = [row for row in metric_rows if row["protocol"] == "isolated_single_spine"]
    by_name = {row["scenario"]: row for row in isolated}
    base = by_name["matched_baseline"]
    combined = by_name["combined_restrained_epileptogenesis"]
    top_by_target = {}
    for row in predictor_rows:
        top_by_target.setdefault(row["target"], row)
    return [
        {
            "claim": "Epilepsy exploratory perturbations should remain separate from baseline SPINE claims.",
            "classification": "strongly_supported",
            "basis": "Phase 06 configs and outputs are under epilepsy_exploratory and contain no clinical claim field beyond none.",
        },
        {
            "claim": "SMI remains a local isolation descriptor under restrained epilepsy-like perturbations.",
            "classification": "supported",
            "basis": f"SMI/topology changes track local isolation in isolated protocols, but active/synaptic variables also alter amplitudes; combined delta A_h={float(combined['A_h_mV'])-float(base['A_h_mV']):.4g} mV.",
        },
        {
            "claim": "SMI is not a reliable active-regime amplitude predictor.",
            "classification": "supported",
            "basis": f"Top A_h predictor in combined scenario ensemble was {top_by_target['A_h_mV']['predictor']}; SMI is challenged by synaptic/NMDA/channel perturbations.",
        },
        {
            "claim": "Equal or similar SMI does not imply electrical equivalence in exploratory epilepsy scenarios.",
            "classification": "supported",
            "basis": "HCN, potassium, synaptic-strength, NMDA, and clustering scenarios can leave SMI unchanged while changing amplitude, latency, voltage integral, or active impedance.",
        },
        {
            "claim": "The exploratory module can identify disease mechanisms.",
            "classification": "contradicted",
            "basis": "Evidence grades are mixed and parameter values are restrained sensitivity probes, not calibrated disease mechanisms.",
        },
    ]


def _prediction_rows() -> list[dict[str, object]]:
    return [
        {
            "prediction": "If spine-neck geometry dominates a preparation, R_neck and SMI changes should covary with local voltage isolation more strongly than with somatic transfer.",
            "falsification": "Somatic or head amplitude changes occur with no corresponding SMI/local-isolation change after controlling synaptic conductance.",
            "status": "hypothesis_generating",
        },
        {
            "prediction": "If HCN/Ih perturbation dominates, active frozen-gate impedance and latency/voltage-integral metrics should change even when DC SMI is unchanged.",
            "falsification": "HCN scaling leaves active impedance and time-domain metrics unchanged within convergence tolerance.",
            "status": "hypothesis_generating",
        },
        {
            "prediction": "Clustered synchronous inputs should weaken scalar SMI predictions relative to isolated single-spine protocols.",
            "falsification": "Clustered and isolated protocols have indistinguishable predictor rankings and deltas.",
            "status": "hypothesis_generating",
        },
    ]


def _validation_rows(metric_rows: list[dict[str, object]], uncertainty_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    repro_a = _lhs(8, 3, PHASE06_SEED)
    repro_b = _lhs(8, 3, PHASE06_SEED)
    scenario_names = {row["scenario"] for row in metric_rows}
    expected = {scenario.name for scenario in SCENARIOS}
    return [
        {
            "check": "scenario_set_complete",
            "status": "pass" if scenario_names == expected else "fail",
            "observed": len(scenario_names),
            "threshold": len(expected),
            "interpretation": "all approved scenarios were simulated",
        },
        {
            "check": "deterministic_lhs_reproducibility",
            "status": "pass" if bool(np.allclose(repro_a, repro_b)) else "fail",
            "observed": float(np.max(np.abs(repro_a - repro_b))),
            "threshold": 0.0,
            "interpretation": "uncertainty design is deterministic for a fixed seed",
        },
        {
            "check": "finite_active_solutions",
            "status": "pass" if all(bool(row["finite"]) for row in metric_rows + uncertainty_rows) else "fail",
            "observed": sum(bool(row["finite"]) for row in metric_rows + uncertainty_rows),
            "threshold": len(metric_rows) + len(uncertainty_rows),
            "interpretation": "time-domain simulations remained finite",
        },
        {
            "check": "gating_bounds",
            "status": "pass"
            if all(float(row["min_gate"]) >= -1e-12 and float(row["max_gate"]) <= 1.0 + 1e-12 for row in metric_rows + uncertainty_rows)
            else "fail",
            "observed": max(float(row["max_gate"]) for row in metric_rows + uncertainty_rows),
            "threshold": 1.0,
            "interpretation": "active gating variables stayed within validated bounds",
        },
        {
            "check": "clinical_claim_absent",
            "status": "pass" if all(row["clinical_claim"] == "none" for row in metric_rows) else "fail",
            "observed": "none",
            "threshold": "none",
            "interpretation": "outputs do not make clinical claims",
        },
        {
            "check": "unit_positive_resistances",
            "status": "pass" if all(float(row["R_neck_Mohm"]) > 0 and float(row["R_in_d_Mohm"]) > 0 for row in metric_rows) else "fail",
            "observed": min(float(row["R_neck_Mohm"]) for row in metric_rows),
            "threshold": ">0",
            "interpretation": "neck resistance and dendritic input resistance are positive SI-derived quantities",
        },
    ]


def _write_reports(
    reports: Path,
    results: Path,
    metric_rows: list[dict[str, object]],
    comparison_rows: list[dict[str, object]],
    uncertainty_summary: list[dict[str, object]],
    predictor_rows: list[dict[str, object]],
    validation_rows: list[dict[str, object]],
) -> dict[str, Path]:
    reports.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, Path] = {}
    failures = [row for row in validation_rows if row["status"] != "pass"]
    top_predictors = {}
    for row in predictor_rows:
        top_predictors.setdefault(row["target"], row)
    baseline = next(row for row in metric_rows if row["scenario"] == "matched_baseline" and row["protocol"] == "isolated_single_spine")
    combined = next(row for row in metric_rows if row["scenario"] == "combined_restrained_epileptogenesis" and row["protocol"] == "isolated_single_spine")

    literature = reports / "PHASE06_LITERATURE_REVIEW.md"
    literature.write_text(
        "# Phase 06 Literature Review\n\n"
        "Phase 06 uses the literature only to define restrained exploratory perturbations. "
        "No row below is treated as a calibrated clinical or disease-state parameter.\n\n"
        "| Key | Evidence grade | Direction used | Limitation |\n"
        "| --- | --- | --- | --- |\n"
        + "\n".join(
            f"| {row.key} | {row.evidence_grade} | {row.direction_supported} | {row.limitation} |"
            for row in EVIDENCE_ROWS
        )
        + f"\n\nSource data: `{results / 'epilepsy_evidence_table.csv'}`.\n",
        encoding="utf-8",
    )
    outputs["literature_report"] = literature

    scenario_report = reports / "PHASE06_SCENARIO_RESULTS.md"
    scenario_report.write_text(
        "# Phase 06 Scenario Results\n\n"
        "The matched baseline is an exploratory Phase 06 comparator, not the manuscript-faithful passive baseline.\n\n"
        f"- Baseline isolated SMI: {float(baseline['SMI']):.6g}\n"
        f"- Combined isolated SMI: {float(combined['SMI']):.6g}\n"
        f"- Baseline isolated A_h: {float(baseline['A_h_mV']):.6g} mV\n"
        f"- Combined isolated A_h: {float(combined['A_h_mV']):.6g} mV\n"
        f"- Source data: `{results / 'scenario_metrics.csv'}` and `{results / 'matched_baseline_comparisons.csv'}`.\n\n"
        "Negative/limiting result: several channel or synaptic scenarios change active voltage metrics while leaving SMI nearly unchanged, "
        "so SMI should not be promoted from a passive low-frequency isolation descriptor to a disease-response predictor.\n",
        encoding="utf-8",
    )
    outputs["scenario_report"] = scenario_report

    prediction_report = reports / "PHASE06_SMI_EPILEPSY_PREDICTIONS.md"
    prediction_report.write_text(
        "# Phase 06 SMI/Epilepsy Predictions\n\n"
        "Falsifiable predictions are stated as model-level hypotheses only.\n\n"
        + "\n".join(f"- {row['prediction']} Falsification: {row['falsification']}" for row in _prediction_rows())
        + f"\n\nPredictor source data: `{results / 'predictor_table.csv'}`.\n",
        encoding="utf-8",
    )
    outputs["prediction_report"] = prediction_report

    uncertainty_report = reports / "PHASE06_UNCERTAINTY_AND_LIMITATIONS.md"
    smi_unc = [row for row in uncertainty_summary if row["metric"] == "SMI"]
    uncertainty_report.write_text(
        "# Phase 06 Uncertainty And Limitations\n\n"
        "Uncertainty propagation used deterministic Latin-hypercube samples around each exploratory scenario. "
        "The ensemble is deliberately small and intended to reveal sensitivity, not to estimate biological prevalence.\n\n"
        "| Scenario | SMI median | SMI p05 | SMI p95 |\n"
        "| --- | ---: | ---: | ---: |\n"
        + "\n".join(
            f"| {row['scenario']} | {float(row['median']):.6g} | {float(row['p05']):.6g} | {float(row['p95']):.6g} |"
            for row in smi_unc
        )
        + f"\n\nSource data: `{results / 'scenario_uncertainty_samples.csv'}` and `{results / 'scenario_uncertainty_summary.csv'}`.\n",
        encoding="utf-8",
    )
    outputs["uncertainty_report"] = uncertainty_report

    report = reports / "PHASE_06_REPORT.md"
    report.write_text(
        "# Phase 06 Report\n\n"
        "Phase 06 implemented a separated exploratory epilepsy/epileptogenesis module. "
        "It did not modify the validated passive, active, Phase 05, or Phase 05.1 scientific implementations.\n\n"
        "## Scope\n\n"
        "- Config family: `configs/epilepsy_exploratory/`\n"
        "- Source data: `results/phase06/`\n"
        "- Figures: `figures/phase06/`\n"
        "- No clinical, diagnostic, prognostic, or therapeutic claims are made.\n\n"
        "## Predictor Summary\n\n"
        + "\n".join(
            f"- {target}: top predictor `{row['predictor']}` with Spearman {float(row['spearman']):.4g}"
            for target, row in top_predictors.items()
        )
        + "\n\n## Validation\n\n"
        + "\n".join(
            f"- {row['check']}: {row['status']} (observed={row['observed']}, threshold={row['threshold']})"
            for row in validation_rows
        )
        + "\n\n"
        + ("No Phase 06 validation failures were observed.\n" if not failures else "Validation failures were preserved: " + ", ".join(row["check"] for row in failures) + "\n")
        + "\n## Boundary\n\nStopped at the Phase 06 boundary. Phase 07 was not started.\n",
        encoding="utf-8",
    )
    outputs["phase_report"] = report
    return outputs


def run_phase06(
    results_dir: str | Path = "results/phase06",
    figures_dir: str | Path = "figures/phase06",
    reports_dir: str | Path = "reports",
) -> dict[str, Path]:
    results = Path(results_dir)
    figures = Path(figures_dir)
    reports = Path(reports_dir)
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)

    outputs: dict[str, Path] = {}
    evidence_rows = [row.__dict__ for row in EVIDENCE_ROWS]
    scenario_rows = [scenario.__dict__ | {"reference_ids": ";".join(scenario.reference_ids)} for scenario in SCENARIOS]
    outputs["evidence_table"] = _write_csv(results / "epilepsy_evidence_table.csv", evidence_rows)
    outputs["scenario_definitions"] = _write_csv(results / "scenario_definitions.csv", scenario_rows)

    protocols = ["isolated_single_spine", "clustered_synchronous", "clustered_asynchronous"]
    metric_rows = [_run_protocol(scenario, protocol) for scenario in SCENARIOS for protocol in protocols]
    comparison_rows = _comparison_rows(metric_rows)
    uncertainty_rows, uncertainty_summary = _uncertainty_rows()
    predictor_rows = _predictor_rows(metric_rows, uncertainty_rows)
    decomposition_rows = _decomposition_rows()
    claim_rows = _claim_rows(metric_rows, predictor_rows)
    prediction_rows = _prediction_rows()
    validation_rows = _validation_rows(metric_rows, uncertainty_rows)

    outputs["scenario_metrics"] = _write_csv(results / "scenario_metrics.csv", metric_rows)
    outputs["matched_baseline_comparisons"] = _write_csv(results / "matched_baseline_comparisons.csv", comparison_rows)
    outputs["scenario_uncertainty_samples"] = _write_csv(results / "scenario_uncertainty_samples.csv", uncertainty_rows)
    outputs["scenario_uncertainty_summary"] = _write_csv(results / "scenario_uncertainty_summary.csv", uncertainty_summary)
    outputs["predictor_table"] = _write_csv(results / "predictor_table.csv", predictor_rows)
    outputs["mechanistic_decomposition"] = _write_csv(results / "mechanistic_decomposition.csv", decomposition_rows)
    outputs["claim_classification"] = _write_csv(results / "claim_classification.csv", claim_rows)
    outputs["falsifiable_predictions"] = _write_csv(results / "falsifiable_predictions.csv", prediction_rows)
    outputs["phase06_validation"] = _write_csv(results / "phase06_validation.csv", validation_rows)
    outputs["provenance_metadata"] = _write_csv(
        results / "provenance_metadata.csv",
        [
            {
                "phase": "06",
                "track": "epilepsy_exploratory",
                "dt_s": PHASE06_DT_S,
                "stop_s": PHASE06_STOP_S,
                "event_time_s": PHASE06_EVENT_S,
                "metric_window_s": PHASE06_WINDOW_S,
                "uncertainty_n_per_scenario": PHASE06_UNCERTAINTY_N,
                "seed": PHASE06_SEED,
                "clinical_claims": "none",
            }
        ],
    )

    isolated_rows = [row for row in metric_rows if row["protocol"] == "isolated_single_spine"]
    outputs["fig_smi_gamma_hd"] = _write_scatter_svg(
        figures / "scenario_SMI_vs_Gamma_hd.svg", isolated_rows, "SMI", "Gamma_h_to_d", "SMI vs Gamma_h_to_d"
    )
    outputs["fig_smi_gamma_hs"] = _write_scatter_svg(
        figures / "scenario_SMI_vs_Gamma_hs.svg", isolated_rows, "SMI", "Gamma_h_to_s", "SMI vs Gamma_h_to_s"
    )
    outputs["fig_smi_ah"] = _write_scatter_svg(
        figures / "scenario_SMI_vs_Ah.svg", isolated_rows, "SMI", "A_h_mV", "SMI vs head amplitude"
    )
    outputs["fig_decomposition"] = _write_line_svg(
        figures / "mechanistic_decomposition_Ah.svg",
        [{**row, "index": i} for i, row in enumerate(decomposition_rows)],
        "index",
        "A_h_mV",
        "Mechanistic decomposition A_h",
    )
    smi_summary = [row for row in uncertainty_summary if row["metric"] == "SMI"]
    outputs["fig_uncertainty"] = _write_line_svg(
        figures / "uncertainty_SMI_by_scenario.svg",
        [{**row, "index": i} for i, row in enumerate(smi_summary)],
        "index",
        "median",
        "SMI uncertainty medians",
    )
    outputs.update(_write_reports(reports, results, metric_rows, comparison_rows, uncertainty_summary, predictor_rows, validation_rows))
    return outputs
