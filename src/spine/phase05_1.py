"""Phase 05.1 convergence and robustness audit for Phase 05 conclusions."""

from __future__ import annotations

from pathlib import Path
import csv
import math

import numpy as np

from spine.geometry import cylindrical_neck_resistance_ohm
from spine.phase03 import _write_csv, _write_line_svg, spearman
from spine.phase05 import (
    BOOTSTRAP_SEED,
    CV_SEED,
    LHS_SEED,
    PARAMETERS,
    bootstrap_abs_spearman_ci,
    claim_row,
    counterexample_prevalence_rows,
    cv_rmse_univariate,
    evaluate_sample,
    lhs_samples,
    multivariable_predictor_rows,
    predictor_rows,
    radius_uncertainty_rows,
    smi_class,
    uncertainty_summary_rows,
)


SAMPLE_SIZES = (96, 192, 384, 768)
CONVERGENCE_THRESHOLD = 0.10
STABILITY_THRESHOLD = 0.05
RADIUS_SD_UM = 0.018
RADIUS_OFFSETS = np.linspace(-2.0, 2.0, 25)
AUDIT_SEED_OFFSET = 5100


def read_csv_rows(path: Path) -> list[dict[str, object]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def progressive_seed(n: int) -> int:
    return LHS_SEED + AUDIT_SEED_OFFSET + n


def evaluated_samples_for_n(n: int, results: Path) -> list[dict[str, object]]:
    path = results / f"global_uncertainty_samples_N{n}.csv"
    if path.exists():
        return read_csv_rows(path)
    seed = progressive_seed(n)
    samples = lhs_samples(n, seed)
    evaluated = [evaluate_sample(sample, include_active=True) for sample in samples]
    _write_csv(path, evaluated)
    return evaluated


def summary_rows_by_n(evaluated_by_n: dict[int, list[dict[str, object]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for n, samples in evaluated_by_n.items():
        for row in uncertainty_summary_rows(samples):
            rows.append({"n": n, **row})
    return rows


def convergence_delta_rows(summary: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    by_n_output = {(int(row["n"]), row["output"]): row for row in summary}
    sizes = sorted({int(row["n"]) for row in summary})
    outputs = sorted({str(row["output"]) for row in summary})
    for prev, current in zip(sizes, sizes[1:]):
        for output in outputs:
            a = by_n_output[(prev, output)]
            b = by_n_output[(current, output)]
            for metric in ("median", "p2_5", "p97_5"):
                av = float(a[metric])
                bv = float(b[metric])
                rows.append(
                    {
                        "n_previous": prev,
                        "n_current": current,
                        "output": output,
                        "metric": metric,
                        "previous_value": av,
                        "current_value": bv,
                        "relative_change": relative_change(av, bv),
                        "passed_10_percent": relative_change(av, bv) < CONVERGENCE_THRESHOLD,
                    }
                )
    return rows


def relative_change(a: float, b: float) -> float:
    return abs(b - a) / max(abs(b), 1e-12)


def convergence_cause_rows(evaluated_by_n: dict[int, list[dict[str, object]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for n, samples in evaluated_by_n.items():
        smi = np.array([float(row["SMI"]) for row in samples])
        radius = np.array([float(row["neck_radius_um"]) for row in samples])
        length = np.array([float(row["neck_length_um"]) for row in samples])
        resistivity = np.array([float(row["intracellular_resistivity_ohm_cm"]) for row in samples])
        rin = np.array([float(row["R_in_d_Mohm"]) for row in samples])
        rows.append(
            {
                "n": n,
                "smi_mean": float(np.mean(smi)),
                "smi_median": float(np.median(smi)),
                "smi_sd": float(np.std(smi, ddof=1)),
                "smi_coefficient_of_variation": float(np.std(smi, ddof=1) / np.mean(smi)),
                "smi_skewness": skewness(smi),
                "smi_p95_over_median": float(np.percentile(smi, 95) / np.median(smi)),
                "radius_smi_spearman": spearman(radius, smi),
                "length_smi_spearman": spearman(length, smi),
                "resistivity_smi_spearman": spearman(resistivity, smi),
                "rin_smi_spearman": spearman(rin, smi),
                "low_class_fraction": class_fraction(samples, "low"),
                "intermediate_class_fraction": class_fraction(samples, "intermediate"),
                "high_class_fraction": class_fraction(samples, "high"),
            }
        )
    return rows


def skewness(values: np.ndarray) -> float:
    centered = values - np.mean(values)
    sd = np.std(values, ddof=1)
    if sd == 0:
        return 0.0
    return float(np.mean(centered**3) / (sd**3))


def class_fraction(samples: list[dict[str, object]], label: str) -> float:
    return sum(1 for row in samples if str(row["SMI_class"]) == label) / len(samples)


def predictor_stability_rows(evaluated_by_n: dict[int, list[dict[str, object]]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    ranking_rows: list[dict[str, object]] = []
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
    for n, samples in evaluated_by_n.items():
        predictors = predictor_rows(samples)
        for group, target in targets:
            univariate = [
                row
                for row in predictors
                if row["group"] == group and row["target"] == target and row["model"] == "univariate_linear"
            ]
            sorted_uni = sorted(univariate, key=lambda row: float(row["abs_spearman"]), reverse=True)
            smi = [row for row in sorted_uni if row["predictor"] == "SMI"][0]
            for rank, row in enumerate(sorted_uni[:8], start=1):
                ranking_rows.append(
                    {
                        "n": n,
                        "group": group,
                        "target": target,
                        "rank": rank,
                        "predictor": row["predictor"],
                        "pearson": row["pearson"],
                        "spearman": row["spearman"],
                        "abs_spearman": row["abs_spearman"],
                        "bootstrap_abs_spearman_p05": row["bootstrap_abs_spearman_p05"],
                        "bootstrap_abs_spearman_p95": row["bootstrap_abs_spearman_p95"],
                        "cv_rmse": row["cv_rmse"],
                        "model": row["model"],
                    }
                )
            best = sorted_uni[0]
            rows.append(
                {
                    "n": n,
                    "group": group,
                    "target": target,
                    "best_univariate_predictor": best["predictor"],
                    "best_abs_spearman": best["abs_spearman"],
                    "best_cv_rmse": best["cv_rmse"],
                    "smi_abs_spearman": smi["abs_spearman"],
                    "smi_bootstrap_p05": smi["bootstrap_abs_spearman_p05"],
                    "smi_bootstrap_p95": smi["bootstrap_abs_spearman_p95"],
                    "smi_cv_rmse": smi["cv_rmse"],
                    "smi_rank": predictor_rank(sorted_uni, "SMI"),
                }
            )
        for row in multivariable_predictor_rows(samples):
            ranking_rows.append({"n": n, "rank": "", **row})
    rows.extend(predictor_delta_rows(rows))
    return rows, ranking_rows


def predictor_rank(rows: list[dict[str, object]], predictor: str) -> int:
    for i, row in enumerate(rows, start=1):
        if row["predictor"] == predictor:
            return i
    return -1


def predictor_delta_rows(summary_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    deltas: list[dict[str, object]] = []
    rows = [row for row in summary_rows if "best_univariate_predictor" in row]
    keys = sorted({(row["group"], row["target"]) for row in rows})
    sizes = sorted({int(row["n"]) for row in rows})
    lookup = {(row["group"], row["target"], int(row["n"])): row for row in rows}
    for group, target in keys:
        for prev, current in zip(sizes, sizes[1:]):
            a = lookup[(group, target, prev)]
            b = lookup[(group, target, current)]
            deltas.append(
                {
                    "n": current,
                    "group": group,
                    "target": target,
                    "best_univariate_predictor": b["best_univariate_predictor"],
                    "best_abs_spearman": b["best_abs_spearman"],
                    "best_cv_rmse": b["best_cv_rmse"],
                    "smi_abs_spearman": b["smi_abs_spearman"],
                    "smi_bootstrap_p05": b["smi_bootstrap_p05"],
                    "smi_bootstrap_p95": b["smi_bootstrap_p95"],
                    "smi_cv_rmse": b["smi_cv_rmse"],
                    "smi_rank": b["smi_rank"],
                    "delta_from_previous_n": abs(float(b["smi_abs_spearman"]) - float(a["smi_abs_spearman"])),
                    "best_predictor_changed_from_previous_n": a["best_univariate_predictor"] != b["best_univariate_predictor"],
                    "row_type": "delta",
                }
            )
    for row in rows:
        row["delta_from_previous_n"] = ""
        row["best_predictor_changed_from_previous_n"] = ""
        row["row_type"] = "summary"
    return deltas


def counterexample_convergence_rows(evaluated_by_n: dict[int, list[dict[str, object]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    previous: dict[str, float] = {}
    for n, samples in evaluated_by_n.items():
        for row in counterexample_prevalence_rows(samples):
            prevalence = float(row["prevalence"])
            rows.append(
                {
                    "n": n,
                    **row,
                    "delta_from_previous_n": "" if row["counterexample_type"] not in previous else abs(prevalence - previous[row["counterexample_type"]]),
                    "stable_vs_previous": "" if row["counterexample_type"] not in previous else abs(prevalence - previous[row["counterexample_type"]]) < STABILITY_THRESHOLD,
                }
            )
            previous[row["counterexample_type"]] = prevalence
    return rows


def radius_audit_rows(evaluated_by_n: dict[int, list[dict[str, object]]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    summary: list[dict[str, object]] = []
    examples: list[dict[str, object]] = []
    for n, samples in evaluated_by_n.items():
        radius_rows = radius_uncertainty_rows(samples)
        flips = [row for row in radius_rows if str(row["class_flips"]) == "True" or row["class_flips"] is True]
        by_class = {label: [row for row in radius_rows if row["true_class"] == label] for label in ("low", "intermediate", "high")}
        summary.append(
            {
                "n": n,
                "flip_count": len(flips),
                "flip_fraction": len(flips) / len(radius_rows),
                "mean_class_stable_fraction": float(np.mean([float(row["class_stable_fraction"]) for row in radius_rows])),
                "min_class_stable_fraction": min(float(row["class_stable_fraction"]) for row in radius_rows),
                "low_flip_fraction": class_flip_fraction(by_class["low"]),
                "intermediate_flip_fraction": class_flip_fraction(by_class["intermediate"]),
                "high_flip_fraction": class_flip_fraction(by_class["high"]),
                "median_distance_to_boundary_all": median_distance_to_boundary(radius_rows),
                "median_distance_to_boundary_flipped": median_distance_to_boundary(flips),
                "median_radius_induced_SMI_fold_range": float(np.median([float(row["measured_SMI_max"]) / max(float(row["measured_SMI_min"]), 1e-12) for row in radius_rows])),
            }
        )
        for row in sorted(radius_rows, key=lambda item: float(item["class_stable_fraction"]))[:12]:
            examples.append(
                {
                    "n": n,
                    **row,
                    "distance_to_nearest_boundary": distance_to_boundary(float(row["true_SMI"])),
                    "SMI_fold_range": float(row["measured_SMI_max"]) / max(float(row["measured_SMI_min"]), 1e-12),
                }
            )
    return summary, examples


def class_flip_fraction(rows: list[dict[str, object]]) -> object:
    if not rows:
        return ""
    return sum(1 for row in rows if str(row["class_flips"]) == "True" or row["class_flips"] is True) / len(rows)


def distance_to_boundary(smi: float) -> float:
    return min(abs(smi - 0.25), abs(smi - 0.75))


def median_distance_to_boundary(rows: list[dict[str, object]]) -> object:
    if not rows:
        return ""
    return float(np.median([distance_to_boundary(float(row["true_SMI"])) for row in rows]))


def radius_only_rows(evaluated_by_n: dict[int, list[dict[str, object]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for n, samples in evaluated_by_n.items():
        for sample in samples:
            true_radius = float(sample["neck_radius_um"])
            rin_ohm = float(sample["R_in_d_Mohm"]) * 1e6
            rneck_values = []
            smi_values = []
            for offset in RADIUS_OFFSETS:
                measured_radius = min(0.22, max(0.06, true_radius + offset * RADIUS_SD_UM))
                rneck = cylindrical_neck_resistance_ohm(
                    float(sample["intracellular_resistivity_ohm_cm"]),
                    float(sample["neck_length_um"]),
                    measured_radius,
                )
                rneck_values.append(rneck / 1e6)
                smi_values.append(rneck / rin_ohm)
            rows.append(
                {
                    "n": n,
                    "sample_id": int(float(sample["sample_id"])),
                    "true_radius_um": true_radius,
                    "true_SMI": sample["SMI"],
                    "true_R_neck_Mohm": sample["R_neck_Mohm"],
                    "R_neck_min_Mohm": min(rneck_values),
                    "R_neck_max_Mohm": max(rneck_values),
                    "R_neck_relative_range": (max(rneck_values) - min(rneck_values)) / max(float(sample["R_neck_Mohm"]), 1e-12),
                    "SMI_min": min(smi_values),
                    "SMI_max": max(smi_values),
                    "SMI_relative_range": (max(smi_values) - min(smi_values)) / max(float(sample["SMI"]), 1e-12),
                }
            )
    return rows


def claim_reassessment_rows(
    predictor_stability: list[dict[str, object]],
    counterexamples: list[dict[str, object]],
    radius_summary: list[dict[str, object]],
    convergence_deltas: list[dict[str, object]],
) -> list[dict[str, object]]:
    final_n = max(int(row["n"]) for row in predictor_stability if row.get("row_type") == "summary")

    def pred(group: str, target: str) -> dict[str, object]:
        return [
            row
            for row in predictor_stability
            if row.get("row_type") == "summary" and int(row["n"]) == final_n and row["group"] == group and row["target"] == target
        ][0]

    ce_final = {row["counterexample_type"]: row for row in counterexamples if int(row["n"]) == final_n}
    radius_final = [row for row in radius_summary if int(row["n"]) == final_n][0]
    local = pred("passive", "Gamma_h_to_d")
    active_local = pred("active", "active_Gamma_h_to_d")
    amp = pred("passive", "A_h_mV")
    active_amp = pred("active", "active_A_h_mV")
    soma = pred("passive", "Gamma_h_to_s")
    active_soma = pred("active", "active_Gamma_h_to_s")
    smi_convergence = [
        row
        for row in convergence_deltas
        if row["output"] == "SMI" and row["metric"] == "median" and int(row["n_current"]) == final_n
    ][0]
    rows = [
        claim_row(
            "SMI is a local isolation descriptor",
            "supported" if float(local["smi_bootstrap_p05"]) > 0.70 and float(active_local["smi_bootstrap_p05"]) > 0.70 else "uncertain",
            f"N={final_n}; passive SMI abs_spearman={local['smi_abs_spearman']} rank={local['smi_rank']}; active SMI abs_spearman={active_local['smi_abs_spearman']} rank={active_local['smi_rank']}",
        ),
        claim_row(
            "SMI is not a reliable amplitude predictor",
            "strongly supported" if float(amp["smi_abs_spearman"]) < 0.30 and float(active_amp["smi_abs_spearman"]) < 0.30 else "supported",
            f"N={final_n}; passive amplitude SMI abs_spearman={amp['smi_abs_spearman']}; active amplitude SMI abs_spearman={active_amp['smi_abs_spearman']}; passive amplitude failures={ce_final['passive_iso_SMI_amplitude_failure']['prevalence']}",
        ),
        claim_row(
            "SMI is not a universal transfer predictor",
            "supported" if int(soma["smi_rank"]) > 1 or int(active_soma["smi_rank"]) > 1 else "uncertain",
            f"N={final_n}; passive somatic SMI rank={soma['smi_rank']} abs_spearman={soma['smi_abs_spearman']}; active somatic SMI rank={active_soma['smi_rank']} abs_spearman={active_soma['smi_abs_spearman']}",
        ),
        claim_row(
            "Active mechanisms sharpen SMI limitations",
            "uncertain"
            if float(ce_final["active_amplitude_failure"]["prevalence"]) < float(ce_final["passive_iso_SMI_amplitude_failure"]["prevalence"])
            else "supported",
            f"N={final_n}; active amplitude failure prevalence={ce_final['active_amplitude_failure']['prevalence']}; passive amplitude failure prevalence={ce_final['passive_iso_SMI_amplitude_failure']['prevalence']}",
        ),
        claim_row(
            "Equal SMI does not imply electrical equivalence",
            "strongly supported" if float(ce_final["passive_iso_SMI_amplitude_failure"]["prevalence"]) >= 0.30 else "supported",
            f"N={final_n}; passive iso-SMI amplitude failure prevalence={ce_final['passive_iso_SMI_amplitude_failure']['prevalence']}; active amplitude failure prevalence={ce_final['active_amplitude_failure']['prevalence']}",
        ),
        claim_row(
            "SMI class assignments are stable under radius uncertainty",
            "contradicted" if float(radius_final["flip_fraction"]) > 0.10 else "weak",
            f"N={final_n}; radius-induced class flip fraction={radius_final['flip_fraction']}; SMI median convergence delta from previous N={smi_convergence['relative_change']}",
        ),
    ]
    return rows


def validation_rows(
    evaluated_by_n: dict[int, list[dict[str, object]]],
    convergence_deltas: list[dict[str, object]],
    predictor_stability: list[dict[str, object]],
    counterexamples: list[dict[str, object]],
) -> list[dict[str, object]]:
    final_n = max(evaluated_by_n)
    repeat = lhs_samples(final_n, progressive_seed(final_n))
    reproducible = all(
        abs(repeat[i][spec.name] - float(evaluated_by_n[final_n][i][spec.name])) < 1e-15
        for i in range(final_n)
        for spec in PARAMETERS
    )
    final_deltas = [
        float(row["relative_change"])
        for row in convergence_deltas
        if int(row["n_current"]) == final_n and row["metric"] == "median"
    ]
    smi_delta = [
        float(row["relative_change"])
        for row in convergence_deltas
        if int(row["n_current"]) == final_n and row["metric"] == "median" and row["output"] == "SMI"
    ][0]
    ranking_rows = [
        row
        for row in predictor_stability
        if row.get("row_type") == "delta" and int(row["n"]) == final_n
    ]
    ranking_stable = all(not (str(row["best_predictor_changed_from_previous_n"]) == "True" or row["best_predictor_changed_from_previous_n"] is True) for row in ranking_rows)
    counter_rows = [
        row
        for row in counterexamples
        if int(row["n"]) == final_n and row["stable_vs_previous"] != ""
    ]
    counter_stable = all(str(row["stable_vs_previous"]) == "True" or row["stable_vs_previous"] is True for row in counter_rows)
    x = np.linspace(0.0, 1.0, 30)
    y = x**2 + 0.1 * x
    boot_a = bootstrap_abs_spearman_ci(x, y, seed=BOOTSTRAP_SEED, n_boot=40)
    boot_b = bootstrap_abs_spearman_ci(x, y, seed=BOOTSTRAP_SEED, n_boot=40)
    cv_a = cv_rmse_univariate(x, y, seed=CV_SEED)
    cv_b = cv_rmse_univariate(x, y, seed=CV_SEED)
    return [
        {"validation": "progressive_lhs_reproducibility", "value": reproducible, "threshold": True, "passed": reproducible},
        {"validation": "final_smi_median_convergence", "value": smi_delta, "threshold": CONVERGENCE_THRESHOLD, "passed": smi_delta < CONVERGENCE_THRESHOLD},
        {"validation": "final_all_median_convergence", "value": max(final_deltas), "threshold": CONVERGENCE_THRESHOLD, "passed": max(final_deltas) < CONVERGENCE_THRESHOLD},
        {"validation": "bootstrap_reproducibility", "value": boot_a == boot_b, "threshold": True, "passed": boot_a == boot_b},
        {"validation": "cross_validation_reproducibility", "value": cv_a == cv_b, "threshold": True, "passed": cv_a == cv_b},
        {"validation": "final_ranking_stability_vs_previous_n", "value": ranking_stable, "threshold": True, "passed": ranking_stable},
        {"validation": "counterexample_prevalence_stability_vs_previous_n", "value": counter_stable, "threshold": True, "passed": counter_stable},
    ]


def run_phase05_1(results_dir: str | Path = "results/phase05_1", figures_dir: str | Path = "figures/phase05_1") -> dict[str, Path]:
    results = Path(results_dir)
    figures = Path(figures_dir)
    results.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, Path] = {}

    evaluated_by_n = {n: evaluated_samples_for_n(n, results) for n in SAMPLE_SIZES}
    summary = summary_rows_by_n(evaluated_by_n)
    outputs["summary"] = _write_csv(results / "progressive_uncertainty_summary.csv", summary)
    convergence = convergence_delta_rows(summary)
    outputs["convergence"] = _write_csv(results / "progressive_convergence_deltas.csv", convergence)
    causes = convergence_cause_rows(evaluated_by_n)
    outputs["causes"] = _write_csv(results / "convergence_cause_diagnostics.csv", causes)
    predictor_stability, predictor_rankings = predictor_stability_rows(evaluated_by_n)
    outputs["predictor_stability"] = _write_csv(results / "predictor_stability_summary.csv", predictor_stability)
    outputs["predictor_rankings"] = _write_csv(results / "predictor_rankings_by_n.csv", predictor_rankings)
    counterexamples = counterexample_convergence_rows(evaluated_by_n)
    outputs["counterexamples"] = _write_csv(results / "counterexample_prevalence_by_n.csv", counterexamples)
    radius_summary, radius_examples = radius_audit_rows(evaluated_by_n)
    outputs["radius_summary"] = _write_csv(results / "radius_uncertainty_by_n.csv", radius_summary)
    outputs["radius_examples"] = _write_csv(results / "radius_boundary_examples.csv", radius_examples)
    outputs["radius_only"] = _write_csv(results / "radius_only_uncertainty.csv", radius_only_rows(evaluated_by_n))
    claims = claim_reassessment_rows(predictor_stability, counterexamples, radius_summary, convergence)
    outputs["claims"] = _write_csv(results / "claim_reassessment.csv", claims)
    validation = validation_rows(evaluated_by_n, convergence, predictor_stability, counterexamples)
    outputs["validation"] = _write_csv(results / "phase05_1_validation.csv", validation)

    smi_rows = [row for row in summary if row["output"] == "SMI"]
    _write_line_svg(figures / "convergence_SMI_median.svg", smi_rows, "n", "median", "SMI median convergence")
    interval_rows = [{**row, "interval_width": float(row["p97_5"]) - float(row["p2_5"])} for row in smi_rows]
    _write_line_svg(figures / "convergence_SMI_interval_width.svg", interval_rows, "n", "interval_width", "SMI percentile width convergence")
    gamma_rows = [row for row in summary if row["output"] == "Gamma_h_to_d"]
    _write_line_svg(figures / "convergence_Gamma_hd_median.svg", gamma_rows, "n", "median", "Gamma_h_to_d median convergence")
    gamma_s_rows = [row for row in summary if row["output"] == "Gamma_h_to_s"]
    _write_line_svg(figures / "convergence_Gamma_hs_median.svg", gamma_s_rows, "n", "median", "Gamma_h_to_s median convergence")
    local_predictor_rows = [
        row
        for row in predictor_stability
        if row.get("row_type") == "summary" and row["group"] == "passive" and row["target"] == "Gamma_h_to_d"
    ]
    _write_line_svg(figures / "predictor_stability_local_SMI.svg", local_predictor_rows, "n", "smi_abs_spearman", "Local SMI predictor stability")
    soma_predictor_rows = [
        row
        for row in predictor_stability
        if row.get("row_type") == "summary" and row["group"] == "passive" and row["target"] == "Gamma_h_to_s"
    ]
    _write_line_svg(figures / "predictor_stability_somatic_SMI.svg", soma_predictor_rows, "n", "smi_abs_spearman", "Somatic SMI predictor stability")
    passive_amp_counter = [row for row in counterexamples if row["counterexample_type"] == "passive_iso_SMI_amplitude_failure"]
    _write_line_svg(figures / "counterexample_prevalence_amplitude.svg", passive_amp_counter, "n", "prevalence", "Passive iso-SMI amplitude failure prevalence")
    _write_line_svg(figures / "radius_flip_prevalence.svg", radius_summary, "n", "flip_fraction", "Radius-induced SMI class flip prevalence")
    return outputs

