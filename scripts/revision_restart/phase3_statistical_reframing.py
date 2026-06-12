"""Restart Phase 3 statistical reframing and high-SMI coverage audit.

This script reads existing SPINE source and derived CSVs and writes Phase 3
statistical-reframing outputs. It does not modify raw source CSVs, validated
model code, manuscript TeX source, manuscript tables, or publication figures.
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "revision_restart" / "phase3"
MANUSCRIPT_OUT = ROOT / "manuscript" / "revision_restart"
PERMUTATION_SEED = 202610
PERMUTATIONS = 1000
LOW_THRESHOLD = 0.25
HIGH_THRESHOLD = 0.75
REFERENCE_HIGH_SMI = 1.3218236853


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("/", "\\")


def read_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(ROOT / path)


def safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan)


def percentile(values: pd.Series, q: float) -> float:
    clean = safe_numeric(values).dropna()
    return float(np.percentile(clean.to_numpy(dtype=float), q)) if len(clean) else math.nan


def spearman(x: Iterable[float], y: Iterable[float]) -> float:
    xs = pd.Series(list(x), dtype=float)
    ys = pd.Series(list(y), dtype=float)
    valid = xs.notna() & ys.notna()
    xs = xs[valid]
    ys = ys[valid]
    if len(xs) < 3 or xs.nunique() < 2 or ys.nunique() < 2:
        return math.nan
    return float(xs.rank(method="average").corr(ys.rank(method="average")))


def phase_artifacts_exist() -> None:
    required = [
        ROOT / "results/revision_restart/phase1/phase1_divider_residual_rows.csv",
        ROOT / "results/revision_restart/phase2/phase2_standardized_descriptor_table.csv",
        ROOT / "results/revision_restart/phase2/phase2_scalar_descriptor_correlations.csv",
        ROOT / "results/revision_restart/phase2/phase2_ratio_vs_components_model_comparison.csv",
        ROOT / "manuscript/revision_restart/PHASE2_NEXT_PHASE_HANDOFF.md",
    ]
    missing = [rel(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Required Phase 1/2 artifacts missing: " + "; ".join(missing))


def manuscript_and_report_files() -> list[Path]:
    patterns = [
        "manuscript/*.tex",
        "manuscript/sections/*.tex",
        "manuscript/tables/*.tex",
        "manuscript/supplement/*.tex",
        "manuscript/supplement/sections/*.tex",
        "manuscript/revision_v2/R3_*",
        "manuscript/revision_v2/R5_*",
        "manuscript/revision_restart/PHASE1_*",
        "manuscript/revision_restart/PHASE2_*",
        "reports/PHASE_05_REPORT.md",
        "reports/PHASE_05_1_REPORT.md",
        "reports/PHASE_R3_REPORT.md",
        "reports/PHASE_RESTART_1_REPORT.md",
        "reports/PHASE_RESTART_2_REPORT.md",
    ]
    files: list[Path] = []
    for pattern in patterns:
        files.extend(sorted(ROOT.glob(pattern)))
    return [path for path in files if path.is_file() and "PHASE3_" not in path.name]


LANGUAGE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("confidence interval", re.compile(r"confidence interval", re.I)),
    ("CI", re.compile(r"\bCI\b", re.I)),
    ("Wilson", re.compile(r"Wilson", re.I)),
    ("bootstrap", re.compile(r"bootstrap", re.I)),
    ("prevalence", re.compile(r"prevalence", re.I)),
    ("percent of samples", re.compile(r"percent of samples", re.I)),
    ("N=768", re.compile(r"N\s*=\s*768", re.I)),
    ("significant", re.compile(r"\bsignificant\b", re.I)),
    ("significance", re.compile(r"\bsignificance\b", re.I)),
    ("predictor", re.compile(r"\bpredictor", re.I)),
    ("best predictor", re.compile(r"best (tested )?predictor", re.I)),
    ("strongest predictor", re.compile(r"strongest predictor", re.I)),
    ("outperformed", re.compile(r"outperformed|outperform", re.I)),
    ("sample", re.compile(r"\bsamples?\b", re.I)),
    ("population", re.compile(r"\bpopulation\b", re.I)),
    ("estimate", re.compile(r"\bestimat", re.I)),
    ("uncertainty", re.compile(r"uncertainty", re.I)),
    ("class flip", re.compile(r"class[- ]flip|class flips|class assignments? changed", re.I)),
    ("failure prevalence", re.compile(r"failure prevalence", re.I)),
    ("deterministic", re.compile(r"deterministic", re.I)),
    ("Latin hypercube", re.compile(r"Latin[- ]hypercube", re.I)),
    ("sensitivity ensemble", re.compile(r"sensitivity ensemble", re.I)),
)


def context_from_line(line: str, current: str) -> str:
    stripped = line.strip()
    if stripped.startswith("#"):
        return stripped.lstrip("#").strip()
    tex_match = re.search(r"\\(?:section|subsection|subsubsection)\{([^}]*)\}", stripped)
    if tex_match:
        return tex_match.group(1)
    if "\\caption" in stripped:
        return "caption"
    return current


def classify_language(line: str, phrase: str) -> tuple[str, str, str, str, str]:
    low = line.lower()
    if phrase in {"confidence interval", "CI", "Wilson"} or "95\\%" in low or "95%" in low:
        return (
            "Inferential-looking interval language is attached to deterministic or designed rows.",
            "Use descriptive interval, deterministic sensitivity range, or remove interval language.",
            "high",
            "Phase 6",
            "Wilson/binomial confidence intervals are not appropriate for deterministic design fractions.",
        )
    if phrase in {"prevalence", "failure prevalence"}:
        return (
            "Prevalence implies population sampling or biological frequency.",
            "Use fraction of sampled parameter combinations with the denominator and design range.",
            "high",
            "Phase 6",
            "Keep the fraction but remove biological-prevalence implication.",
        )
    if phrase == "bootstrap":
        return (
            "Bootstrap intervals over designed rows can be mistaken for population uncertainty.",
            "Call these deterministic bootstrap stability intervals or move them to supplement.",
            "high",
            "Phase 6",
            "Retain only with explicit designed-row caveat.",
        )
    if phrase in {"best predictor", "strongest predictor", "outperformed"}:
        return (
            "Winner language overstates target- and row-subset-dependent descriptor comparisons.",
            "Use descriptor-family language and identify target-specific useful/weak families.",
            "high",
            "Phase 6",
            "Phase 2 showed component/dynamic/conductance descriptors can outperform raw SMI.",
        )
    if phrase in {"N=768", "Latin hypercube", "sensitivity ensemble", "deterministic"}:
        return (
            "Could imply sample-size support unless described as a deterministic design.",
            "State deterministic sensitivity ensemble and avoid population inference.",
            "medium",
            "Phase 6",
            "N stabilizes a design grid; it does not create biological sampling.",
        )
    if phrase == "class flip":
        return (
            "Class-flip percentages can read as biological prevalence.",
            "Use class changes within sampled parameter combinations under the assumed radius-error model.",
            "high",
            "Phase 6",
            "Thresholds are heuristic and measurement-model dependent.",
        )
    if phrase in {"sample", "population", "estimate", "uncertainty"}:
        if "sampled parameter" in low or "not a biological" in low or "not population" in low:
            return (
                "Mostly acceptable because the deterministic-design caveat is present.",
                "Retain or tighten wording to sampled parameter combinations.",
                "low",
                "Phase 6",
                "Check local context during rewrite.",
            )
        return (
            "May imply random sampling or inferential uncertainty.",
            "Use sampled parameter combinations, design rows, or deterministic sensitivity range.",
            "medium",
            "Phase 6",
            "Avoid standalone sample/population wording.",
        )
    if phrase in {"significant", "significance"}:
        return (
            "Significance language is not appropriate without a defined inferential model.",
            "Use larger/smaller descriptive effect, design check, or association strength.",
            "high",
            "Phase 6",
            "Remove significance framing unless a later phase adds a justified inferential model.",
        )
    return (
        "Potential statistical wording issue.",
        "Review and replace with deterministic descriptive language where needed.",
        "medium",
        "Phase 6",
        "Automated audit hit.",
    )


def statistical_language_audit() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for path in manuscript_and_report_files():
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception as exc:
            rows.append(
                {
                    "file": rel(path),
                    "section_or_context": "read_error",
                    "phrase": "",
                    "current_problem": f"Could not read file: {type(exc).__name__}: {exc}",
                    "recommended_replacement": "",
                    "priority": "medium",
                    "phase_for_edit": "Phase 6",
                    "notes": "",
                }
            )
            continue
        context = ""
        for line_number, line in enumerate(lines, start=1):
            context = context_from_line(line, context)
            for phrase, pattern in LANGUAGE_PATTERNS:
                if pattern.search(line):
                    problem, replacement, priority, phase, notes = classify_language(line, phrase)
                    rows.append(
                        {
                            "file": rel(path),
                            "section_or_context": context or f"line {line_number}",
                            "phrase": line.strip()[:260],
                            "current_problem": problem,
                            "recommended_replacement": replacement,
                            "priority": priority,
                            "phase_for_edit": phase,
                            "notes": f"matched term={phrase}; line={line_number}. {notes}",
                        }
                    )
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame = frame.drop_duplicates().sort_values(["priority", "file", "section_or_context", "phrase"])
    return frame


def interval_classification() -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    def add(**kwargs: object) -> None:
        base = {
            "interval_or_uncertainty_item": "",
            "source_file": "",
            "n_or_denominator": "",
            "current_interval_type": "",
            "phase3_classification": "",
            "recommended_action": "",
            "replacement_language": "",
            "notes": "",
        }
        base.update(kwargs)
        rows.append(base)

    pred_path = ROOT / "results/revision_v2/r3/r3_predictor_comparison_intervals.csv"
    if pred_path.exists():
        pred = pd.read_csv(pred_path)
        for (regime, target), group in pred.groupby(["regime", "target"], dropna=False):
            add(
                interval_or_uncertainty_item=f"{regime}:{target}:bootstrap predictor intervals",
                source_file=rel(pred_path),
                n_or_denominator="; ".join(str(int(n)) for n in sorted(group["n"].dropna().unique())),
                current_interval_type="bootstrap_abs_spearman_95_low/high plus CV RMSE",
                phase3_classification="bootstrap stability interval over designed rows",
                recommended_action="rename and heavily qualify; avoid confidence interval wording",
                replacement_language="deterministic bootstrap stability range over designed rows",
                notes="Useful as robustness check, not population inference.",
            )
    ce_path = ROOT / "results/revision_v2/r3/r3_counterexample_prevalence_intervals.csv"
    if ce_path.exists():
        ce = pd.read_csv(ce_path)
        for _, row in ce.iterrows():
            add(
                interval_or_uncertainty_item=f"{row.get('source')}:{row.get('counterexample_type')}",
                source_file=rel(ce_path),
                n_or_denominator=row.get("eligible_pairs", ""),
                current_interval_type=row.get("interval_method", "Wilson/binomial interval"),
                phase3_classification="inappropriate or misleading",
                recommended_action="remove Wilson interval; report design fraction and denominator",
                replacement_language="fraction of eligible sampled parameter-pairs in the deterministic design",
                notes="Eligible pairs are induced by a deterministic ensemble, not random binomial trials.",
            )
    for path_text in [
        "results/phase05/uncertainty_summary.csv",
        "results/phase05_1/progressive_uncertainty_summary.csv",
        "results/revision_v2/r3/r3_radius_uncertainty_summary.csv",
    ]:
        path = ROOT / path_text
        if path.exists():
            frame = pd.read_csv(path)
            add(
                interval_or_uncertainty_item=path.stem,
                source_file=rel(path),
                n_or_denominator="; ".join(str(v) for v in sorted(set(frame.filter(regex="^n$").stack().dropna().astype(str)))[:8])
                if "n" in frame.columns
                else "",
                current_interval_type="percentile/range summary",
                phase3_classification="deterministic sensitivity-design percentile range",
                recommended_action="retain as descriptive range; do not call confidence interval",
                replacement_language="descriptive percentile range within the deterministic sensitivity ensemble",
                notes="Range depends on selected parameter bounds.",
            )
    rad_path = ROOT / "results/phase05_1/radius_uncertainty_by_n.csv"
    if rad_path.exists():
        rad = pd.read_csv(rad_path)
        final = rad.sort_values("n").tail(1).iloc[0]
        add(
            interval_or_uncertainty_item="radius class-flip fraction",
            source_file=rel(rad_path),
            n_or_denominator=int(final["n"]),
            current_interval_type="fraction by deterministic radius-error offsets",
            phase3_classification="deterministic sensitivity-design fraction",
            recommended_action="retain as design fraction; remove prevalence/confidence language",
            replacement_language="class changes in sampled parameter combinations under the assumed radius-error model",
            notes=f"Final design fraction={final['flip_fraction']:.6g}.",
        )
    phase2_model = ROOT / "results/revision_restart/phase2/phase2_ratio_vs_components_model_comparison.csv"
    if phase2_model.exists():
        add(
            interval_or_uncertainty_item="Phase 2 CV model-comparison metrics",
            source_file=rel(phase2_model),
            n_or_denominator="varies by target/regime",
            current_interval_type="deterministic cross-validated RMSE/R2",
            phase3_classification="descriptive design-resampling check",
            recommended_action="retain as descriptive model-comparison metric",
            replacement_language="deterministic row-level cross-validation within designed/sensitivity rows",
            notes="Do not use as population generalization error.",
        )
    add(
        interval_or_uncertainty_item="N=768 uncertainty summaries",
        source_file="results\\phase05_1\\global_uncertainty_samples_N768.csv",
        n_or_denominator=768,
        current_interval_type="deterministic LHS sensitivity ensemble",
        phase3_classification="deterministic sensitivity-design summary",
        recommended_action="retain as convergence/stability evidence only",
        replacement_language="within the N=768 deterministic sensitivity design",
        notes="N stabilizes the design; it is not a biological sample size.",
    )
    return pd.DataFrame(rows)


SUMMARY_DATASETS: tuple[tuple[str, str, str], ...] = (
    ("phase05_global_uncertainty_N96", "results/phase05/global_uncertainty_samples.csv", "deterministic Latin-hypercube sensitivity design"),
    ("phase05_1_global_uncertainty_N96", "results/phase05_1/global_uncertainty_samples_N96.csv", "deterministic progressive Latin-hypercube sensitivity design"),
    ("phase05_1_global_uncertainty_N192", "results/phase05_1/global_uncertainty_samples_N192.csv", "deterministic progressive Latin-hypercube sensitivity design"),
    ("phase05_1_global_uncertainty_N384", "results/phase05_1/global_uncertainty_samples_N384.csv", "deterministic progressive Latin-hypercube sensitivity design"),
    ("phase05_1_global_uncertainty_N768", "results/phase05_1/global_uncertainty_samples_N768.csv", "deterministic progressive Latin-hypercube sensitivity design"),
    ("phase03_passive_morphology_challenge", "results/phase03/smi_challenge_suite.csv", "designed passive morphology challenge"),
    ("phase04_active_nonlinear_challenge", "results/phase04/active_smi_challenge_suite.csv", "designed active nonlinear challenge"),
    ("phase06_exploratory_scenario_uncertainty", "results/phase06/scenario_uncertainty_samples.csv", "exploratory deterministic stress-test sensitivity screen"),
    ("phase2_standardized_nonexploratory", "results/revision_restart/phase2/phase2_standardized_descriptor_table.csv", "Phase 2 derived non-exploratory descriptor rows"),
)


def descriptive_sensitivity_summaries() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    target_cols = [
        "SMI",
        "Gamma_h_to_d",
        "observed_Gamma_h_to_d",
        "Gamma_divider",
        "residual",
        "absolute_residual",
        "Gamma_h_to_s",
        "A_h_mV",
        "active_Gamma_h_to_d",
        "active_Gamma_h_to_s",
        "active_A_h_mV",
        "dynamic_SMI_abs",
        "dynamic_SMI_abs_50Hz",
        "synaptic_conductance_scale",
    ]
    for label, path_text, design in SUMMARY_DATASETS:
        path = ROOT / path_text
        if not path.exists():
            continue
        frame = pd.read_csv(path)
        if "exploratory_only" in frame.columns and "nonexploratory" in label:
            frame = frame[~frame["exploratory_only"].astype(bool)].copy()
        denominator = len(frame)
        for col in target_cols:
            if col not in frame.columns:
                continue
            values = safe_numeric(frame[col]).dropna()
            if len(values) < 1:
                continue
            rows.append(
                {
                    "dataset": label,
                    "source_file": path_text,
                    "quantity": col,
                    "summary_type": "descriptive_percentile_range",
                    "n": len(values),
                    "denominator": denominator,
                    "minimum": float(values.min()),
                    "p05": percentile(values, 5),
                    "q25": percentile(values, 25),
                    "median": percentile(values, 50),
                    "q75": percentile(values, 75),
                    "p95": percentile(values, 95),
                    "maximum": float(values.max()),
                    "fraction": "",
                    "numerator": "",
                    "design_description": design,
                    "interpretation": "descriptive range across sampled parameter combinations; not a confidence interval",
                }
            )
        if "SMI" in frame.columns:
            smi = safe_numeric(frame["SMI"]).dropna()
            for name, mask in [
                ("fraction_low_SMI", smi < LOW_THRESHOLD),
                ("fraction_intermediate_SMI", (smi >= LOW_THRESHOLD) & (smi < HIGH_THRESHOLD)),
                ("fraction_high_SMI", smi >= HIGH_THRESHOLD),
            ]:
                numerator = int(mask.sum())
                rows.append(
                    {
                        "dataset": label,
                        "source_file": path_text,
                        "quantity": name,
                        "summary_type": "design_fraction",
                        "n": len(smi),
                        "denominator": len(smi),
                        "minimum": "",
                        "p05": "",
                        "q25": "",
                        "median": "",
                        "q75": "",
                        "p95": "",
                        "maximum": "",
                        "fraction": numerator / len(smi) if len(smi) else math.nan,
                        "numerator": numerator,
                        "design_description": design,
                        "interpretation": "fraction of sampled parameter combinations; not biological prevalence",
                    }
                )
    rad_path = ROOT / "results/phase05_1/radius_uncertainty_by_n.csv"
    if rad_path.exists():
        rad = pd.read_csv(rad_path)
        for _, row in rad.iterrows():
            rows.append(
                {
                    "dataset": f"phase05_1_radius_uncertainty_N{int(row['n'])}",
                    "source_file": rel(rad_path),
                    "quantity": "class_flip_fraction",
                    "summary_type": "design_fraction",
                    "n": int(row["n"]),
                    "denominator": int(row["n"]),
                    "minimum": "",
                    "p05": "",
                    "q25": "",
                    "median": "",
                    "q75": "",
                    "p95": "",
                    "maximum": "",
                    "fraction": row["flip_fraction"],
                    "numerator": int(row["flip_count"]),
                    "design_description": "deterministic radius-error sensitivity offsets",
                    "interpretation": "class changes under assumed radius-error model; not biological prevalence",
                }
            )
    ce_path = ROOT / "results/phase05_1/counterexample_prevalence_by_n.csv"
    if ce_path.exists():
        ce = pd.read_csv(ce_path)
        for _, row in ce.iterrows():
            rows.append(
                {
                    "dataset": f"phase05_1_counterexample_N{int(row['n'])}",
                    "source_file": rel(ce_path),
                    "quantity": row["counterexample_type"],
                    "summary_type": "design_fraction",
                    "n": int(row["n"]),
                    "denominator": int(row["eligible_pairs"]),
                    "minimum": "",
                    "p05": "",
                    "q25": "",
                    "median": "",
                    "q75": "",
                    "p95": "",
                    "maximum": "",
                    "fraction": row["prevalence"],
                    "numerator": int(row["failure_pairs"]),
                    "design_description": "eligible pairs induced by deterministic uncertainty-design rows",
                    "interpretation": "fraction of eligible sampled parameter-pairs; not biological prevalence",
                }
            )
    return pd.DataFrame(rows)


def predictor_family(name: str) -> str:
    low = str(name).lower()
    if any(token in low for token in ("dynamic", "zin", "ztransfer", "transfer_gain", "impedance", "electrotonic")):
        return "dynamic/impedance family"
    if any(token in low for token in ("synaptic", "conductance", "nmda")):
        return "synaptic-drive family"
    if "gamma_divider" in low or low == "smi" or "smi_linear" in low or "divider" in low:
        return "DC neck/load ratio family"
    if any(token in low for token in ("r_neck", "r_in", "component", "neck_mohm")):
        return "component family"
    if any(token in low for token in ("path", "branch", "area", "capacitance", "location", "morph")):
        return "morphology/location family"
    return "other descriptor family"


def recommendation_for_target(target: str) -> str:
    if target == "observed_Gamma_h_to_d":
        return "Use the analytic divider as the first-order local expectation and report residual departures."
    if target in ("residual", "absolute_residual"):
        return "Use component, conductance, and dynamic/impedance families for residual-domain precision."
    if target == "Gamma_h_to_s":
        return "Use downstream transfer/impedance families for somatic transfer."
    if target == "A_h_mV":
        return "Use synaptic-drive and impedance/component context for amplitude."
    return "Report descriptor-family behavior with target-specific caveats."


def predictor_family_summary() -> pd.DataFrame:
    corr = read_csv("results/revision_restart/phase2/phase2_scalar_descriptor_correlations.csv")
    models = read_csv("results/revision_restart/phase2/phase2_ratio_vs_components_model_comparison.csv")
    rows: list[dict[str, object]] = []
    keys = sorted(set(zip(corr["target"], corr["regime"])))
    for target, regime in keys:
        csub = corr[(corr["target"] == target) & (corr["regime"] == regime)].copy()
        csub["family"] = csub["predictor"].map(predictor_family)
        fam = (
            csub.groupby("family", dropna=False)["abs_spearman"]
            .max()
            .reset_index()
            .sort_values("abs_spearman", ascending=False)
        )
        best_value = float(fam["abs_spearman"].max()) if not fam.empty else math.nan
        useful = fam[fam["abs_spearman"] >= 0.6]
        weak = fam[fam["abs_spearman"] < 0.3]
        near = fam[fam["abs_spearman"] >= best_value - 0.05] if math.isfinite(best_value) else fam.iloc[0:0]
        msub = models[(models["target"] == target) & (models["regime"] == regime)].copy()
        if not msub.empty:
            msub["family"] = msub["model"].map(predictor_family)
            model_summary = (
                msub.groupby("family", dropna=False)["cv_rmse"]
                .min()
                .reset_index()
                .sort_values("cv_rmse", ascending=True)
            )
            best_model_family = str(model_summary.iloc[0]["family"])
            best_model_cv_rmse = float(model_summary.iloc[0]["cv_rmse"])
        else:
            best_model_family = ""
            best_model_cv_rmse = math.nan
        rows.append(
            {
                "target": target,
                "regime": regime,
                "top_scalar_family": "" if fam.empty else fam.iloc[0]["family"],
                "top_scalar_family_abs_spearman": "" if fam.empty else fam.iloc[0]["abs_spearman"],
                "near_tied_families": "; ".join(near["family"].astype(str)),
                "useful_families": "; ".join(useful["family"].astype(str)),
                "weak_families": "; ".join(weak["family"].astype(str)),
                "best_model_family_by_cv_rmse": best_model_family,
                "best_model_family_cv_rmse": best_model_cv_rmse,
                "target_specific_recommendation": recommendation_for_target(str(target)),
                "smi_language": "Describe SMI as a compact coordinate for the divider family, not as a universal predictor.",
                "caveat": "Family rankings are descriptive over designed/sensitivity rows and depend on available columns.",
            }
        )
    return pd.DataFrame(rows)


def design_permutation_checks() -> pd.DataFrame:
    table = read_csv("results/revision_restart/phase2/phase2_standardized_descriptor_table.csv")
    if "exploratory_only" in table.columns:
        table = table[~table["exploratory_only"].astype(bool)].copy()
    checks = [
        ("Gamma_divider_vs_local_transfer", "Gamma_divider", "observed_Gamma_h_to_d", "dataset"),
        ("SMI_vs_local_transfer", "SMI", "observed_Gamma_h_to_d", "dataset"),
        ("synaptic_conductance_scale_vs_head_amplitude", "synaptic_conductance_scale", "A_h_mV", "dataset"),
        ("transfer_gain_vs_somatic_transfer", "transfer_gain", "Gamma_h_to_s", "dataset"),
        ("dynamic_SMI_vs_absolute_residual", "dynamic_SMI_abs", "absolute_residual", "dataset"),
        ("R_neck_vs_signed_residual", "R_neck_Mohm", "residual", "dataset"),
    ]
    rng = np.random.default_rng(PERMUTATION_SEED)
    rows: list[dict[str, object]] = []
    for name, x_col, y_col, group_col in checks:
        if x_col not in table.columns or y_col not in table.columns:
            rows.append(
                {
                    "check": name,
                    "predictor": x_col,
                    "target": y_col,
                    "n_rows": 0,
                    "observed_spearman": "",
                    "observed_abs_spearman": "",
                    "permutations": 0,
                    "permutation_abs_spearman_p05": "",
                    "permutation_abs_spearman_median": "",
                    "permutation_abs_spearman_p95": "",
                    "fraction_permutations_as_or_more_extreme": "",
                    "interpretation": "skipped_missing_columns",
                    "caveat": "Design-permutation check only; not a biological p-value.",
                }
            )
            continue
        sub = table[[x_col, y_col, group_col]].copy()
        sub[x_col] = safe_numeric(sub[x_col])
        sub[y_col] = safe_numeric(sub[y_col])
        sub = sub.dropna().reset_index(drop=True)
        if len(sub) < 20 or sub[x_col].nunique() < 3 or sub[y_col].nunique() < 3:
            rows.append(
                {
                    "check": name,
                    "predictor": x_col,
                    "target": y_col,
                    "n_rows": len(sub),
                    "observed_spearman": spearman(sub[x_col], sub[y_col]) if len(sub) >= 3 else "",
                    "observed_abs_spearman": abs(spearman(sub[x_col], sub[y_col])) if len(sub) >= 3 else "",
                    "permutations": 0,
                    "permutation_abs_spearman_p05": "",
                    "permutation_abs_spearman_median": "",
                    "permutation_abs_spearman_p95": "",
                    "fraction_permutations_as_or_more_extreme": "",
                    "interpretation": "skipped_small_or_low_variation",
                    "caveat": "Design-permutation check only; not a biological p-value.",
                }
            )
            continue
        observed = spearman(sub[x_col], sub[y_col])
        permuted_stats: list[float] = []
        groups = list(sub.groupby(group_col, sort=False).groups.values())
        y = sub[y_col].to_numpy(dtype=float)
        x = sub[x_col].to_numpy(dtype=float)
        for _ in range(PERMUTATIONS):
            y_perm = y.copy()
            for idx in groups:
                idx_arr = np.asarray(list(idx), dtype=int)
                if len(idx_arr) > 1:
                    y_perm[idx_arr] = rng.permutation(y_perm[idx_arr])
            permuted_stats.append(abs(spearman(x, y_perm)))
        perm = np.asarray(permuted_stats, dtype=float)
        more_extreme = float(np.mean(perm >= abs(observed)))
        rows.append(
            {
                "check": name,
                "predictor": x_col,
                "target": y_col,
                "n_rows": len(sub),
                "observed_spearman": observed,
                "observed_abs_spearman": abs(observed),
                "permutations": PERMUTATIONS,
                "permutation_abs_spearman_p05": float(np.percentile(perm, 5)),
                "permutation_abs_spearman_median": float(np.percentile(perm, 50)),
                "permutation_abs_spearman_p95": float(np.percentile(perm, 95)),
                "fraction_permutations_as_or_more_extreme": more_extreme,
                "interpretation": "observed design association exceeds random within-dataset label pairings"
                if more_extreme <= 0.05
                else "observed design association is not clearly separated from random within-dataset label pairings",
                "caveat": "Design-permutation check only; not a biological p-value or population inference.",
            }
        )
    return pd.DataFrame(rows)


HIGH_SMI_DATASETS: tuple[tuple[str, str, str], ...] = (
    ("phase02_baseline_targets", "results/phase02/Figure2_representative_summary.csv", "reference target cases"),
    ("phase02_fixed_load_geometry_sweep", "results/phase02/Figure3_geometry_sweep.csv", "designed fixed-load geometry sweep"),
    ("phase02_matched_neck_load_sweep", "results/phase02/Figure4_matched_neck_heterogeneous_load.csv", "designed matched-neck load sweep"),
    ("phase03_passive_morphology_challenge", "results/phase03/smi_challenge_suite.csv", "designed passive morphology challenge"),
    ("phase04_active_nonlinear_challenge", "results/phase04/active_smi_challenge_suite.csv", "designed active challenge"),
    ("phase05_global_uncertainty_N96", "results/phase05/global_uncertainty_samples.csv", "deterministic uncertainty ensemble"),
    ("phase05_1_global_uncertainty_N96", "results/phase05_1/global_uncertainty_samples_N96.csv", "deterministic uncertainty ensemble"),
    ("phase05_1_global_uncertainty_N192", "results/phase05_1/global_uncertainty_samples_N192.csv", "deterministic uncertainty ensemble"),
    ("phase05_1_global_uncertainty_N384", "results/phase05_1/global_uncertainty_samples_N384.csv", "deterministic uncertainty ensemble"),
    ("phase05_1_global_uncertainty_N768", "results/phase05_1/global_uncertainty_samples_N768.csv", "deterministic uncertainty ensemble"),
    ("phase06_exploratory_scenario_metrics", "results/phase06/scenario_metrics.csv", "exploratory stress-test scenarios"),
    ("phase06_exploratory_uncertainty_samples", "results/phase06/scenario_uncertainty_samples.csv", "exploratory stress-test sensitivity screen"),
    ("phase1_residual_rows", "results/revision_restart/phase1/phase1_divider_residual_rows.csv", "derived residual rows"),
    ("phase2_standardized_descriptor_rows", "results/revision_restart/phase2/phase2_standardized_descriptor_table.csv", "derived descriptor rows"),
)


def high_smi_coverage_audit() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for label, path_text, design in HIGH_SMI_DATASETS:
        path = ROOT / path_text
        if not path.exists():
            continue
        frame = pd.read_csv(path)
        if "SMI" not in frame.columns:
            continue
        smi = safe_numeric(frame["SMI"]).dropna()
        if smi.empty:
            continue
        low_count = int((smi < LOW_THRESHOLD).sum())
        intermediate_count = int(((smi >= LOW_THRESHOLD) & (smi < HIGH_THRESHOLD)).sum())
        high_count = int((smi >= HIGH_THRESHOLD).sum())
        max_smi = float(smi.max())
        is_uncertainty = "uncertainty ensemble" in design
        if is_uncertainty and high_count == 0:
            support = "does not support high-SMI uncertainty claims; scope to sampled low/intermediate range"
        elif high_count > 0:
            support = "contains high-SMI rows, but claims remain design-specific"
        else:
            support = "no high-SMI coverage"
        rows.append(
            {
                "dataset": label,
                "source_file": path_text,
                "design_type": design,
                "n_rows": len(smi),
                "min_SMI": float(smi.min()),
                "median_SMI": float(smi.median()),
                "max_SMI": max_smi,
                "low_threshold": LOW_THRESHOLD,
                "high_threshold": HIGH_THRESHOLD,
                "n_low": low_count,
                "n_intermediate": intermediate_count,
                "n_high": high_count,
                "fraction_low": low_count / len(smi),
                "fraction_intermediate": intermediate_count / len(smi),
                "fraction_high": high_count / len(smi),
                "reference_high_isolation_target_covered": bool(max_smi >= REFERENCE_HIGH_SMI),
                "claims_about_high_SMI_uncertainty_supported": "no" if is_uncertainty and high_count == 0 else "limited" if high_count > 0 else "no",
                "phase3_recommendation": support,
            }
        )
    return pd.DataFrame(rows)


def claim_reframing_table() -> pd.DataFrame:
    rows = [
        {
            "claim_id": "P3-C01",
            "old_or_current_wording": "SMI predicts or is the best predictor of local transfer.",
            "issue": "Raw SMI is being framed as an empirical winner rather than the coordinate for the analytic divider expectation.",
            "revised_wording": "SMI parameterizes the local divider expectation; use Gamma_divider as the first-order local-transfer prediction and analyze residual departures.",
            "statistical_basis": "Phase 1 divider derivation and Phase 2 model comparison.",
            "whether_uses_inferential_language": "no",
            "manuscript_target_section": "Abstract, Results, predictor table",
            "priority": "high",
            "notes": "Replace best-predictor wording with analytic expectation plus residual-domain language.",
        },
        {
            "claim_id": "P3-C02",
            "old_or_current_wording": "Bootstrap confidence intervals show SMI is the best predictor.",
            "issue": "Bootstrap intervals over designed rows can imply population inference.",
            "revised_wording": "Deterministic bootstrap stability ranges over designed rows support the descriptor-family pattern, not a population-level ranking.",
            "statistical_basis": "Phase 3 interval classification.",
            "whether_uses_inferential_language": "current yes; revised no",
            "manuscript_target_section": "Methods, Results, Table 3, supplement",
            "priority": "high",
            "notes": "Use only if strongly caveated or move details to supplement.",
        },
        {
            "claim_id": "P3-C03",
            "old_or_current_wording": "Class flips occurred in 24.0% of samples with Wilson 95% interval.",
            "issue": "Wilson CI treats deterministic sensitivity rows as random binomial trials.",
            "revised_wording": "Under the assumed radius-error model, class assignments changed in 184/768 sampled parameter combinations.",
            "statistical_basis": "Phase 05.1 radius uncertainty table and Phase 3 interval classification.",
            "whether_uses_inferential_language": "current yes; revised no",
            "manuscript_target_section": "Abstract, Results, claim table",
            "priority": "high",
            "notes": "Remove Wilson interval and biological-prevalence implication.",
        },
        {
            "claim_id": "P3-C04",
            "old_or_current_wording": "Amplitude failure prevalence was 64.5% passive and 57.8% active.",
            "issue": "Prevalence language implies biological population frequency.",
            "revised_wording": "Amplitude failures occurred in the corresponding fractions of eligible sampled parameter-pairs within the deterministic design.",
            "statistical_basis": "Phase 05.1 counterexample design fractions.",
            "whether_uses_inferential_language": "current yes; revised no",
            "manuscript_target_section": "Results, Discussion, claim table",
            "priority": "high",
            "notes": "Keep numerator/denominator and design qualifier.",
        },
        {
            "claim_id": "P3-C05",
            "old_or_current_wording": "N=768 uncertainty ensemble supports high-SMI class conclusions.",
            "issue": "N=768 LHS has no high-SMI rows.",
            "revised_wording": "The N=768 deterministic uncertainty ensemble stabilizes sampled low/intermediate SMI summaries but does not support high-SMI uncertainty claims.",
            "statistical_basis": "Phase 3 high-SMI coverage audit.",
            "whether_uses_inferential_language": "no",
            "manuscript_target_section": "Results uncertainty section, Discussion limitations",
            "priority": "high",
            "notes": "Scope high-isolation uncertainty claims to reference/design cases or future diagnostic extension.",
        },
        {
            "claim_id": "P3-C06",
            "old_or_current_wording": "SMI is preferable to the component pair.",
            "issue": "Phase 2 showed the component pair can improve raw-SMI precision for local transfer and residuals.",
            "revised_wording": "SMI is a compact interpretable compression; use the component pair or dynamic/impedance descriptors when precision matters.",
            "statistical_basis": "Phase 2 ratio-versus-components comparison.",
            "whether_uses_inferential_language": "no",
            "manuscript_target_section": "Introduction, Results, Discussion",
            "priority": "high",
            "notes": "Do not force a positive SMI narrative.",
        },
        {
            "claim_id": "P3-C07",
            "old_or_current_wording": "Active mechanisms preserve local usefulness.",
            "issue": "Can sound like a universal active-neuron claim.",
            "revised_wording": "In designed active stress tests, local divider-family ordering persisted, while active state and synaptic drive increased residual and amplitude determinants.",
            "statistical_basis": "Phase 2 target-specific summary and Phase 04 designed suite.",
            "whether_uses_inferential_language": "no",
            "manuscript_target_section": "Abstract, Results active section",
            "priority": "medium",
            "notes": "Keep generic active-extension caveat.",
        },
        {
            "claim_id": "P3-C08",
            "old_or_current_wording": "Deterministic ensembles estimate population uncertainty.",
            "issue": "LHS and designed suites are sensitivity designs, not random population samples.",
            "revised_wording": "The ensembles summarize outcomes across chosen parameter ranges and sampled parameter combinations.",
            "statistical_basis": "Phase 3 statistical reframing.",
            "whether_uses_inferential_language": "current yes if estimate/confidence wording remains; revised no",
            "manuscript_target_section": "Methods uncertainty section, supplement",
            "priority": "high",
            "notes": "Commit to sensitivity-analysis paradigm unless later probabilistic modeling is added.",
        },
    ]
    return pd.DataFrame(rows)


def write_outputs() -> dict[str, int]:
    OUT.mkdir(parents=True, exist_ok=True)
    MANUSCRIPT_OUT.mkdir(parents=True, exist_ok=True)
    outputs = {
        OUT / "phase3_interval_classification.csv": interval_classification(),
        OUT / "phase3_descriptive_sensitivity_summaries.csv": descriptive_sensitivity_summaries(),
        OUT / "phase3_predictor_family_summary.csv": predictor_family_summary(),
        OUT / "phase3_design_permutation_checks.csv": design_permutation_checks(),
        OUT / "phase3_high_smi_coverage_audit.csv": high_smi_coverage_audit(),
        MANUSCRIPT_OUT / "PHASE3_STATISTICAL_LANGUAGE_AUDIT.csv": statistical_language_audit(),
        MANUSCRIPT_OUT / "PHASE3_CLAIM_REFRAMING_TABLE.csv": claim_reframing_table(),
    }
    row_counts: dict[str, int] = {}
    for path, frame in outputs.items():
        frame.to_csv(path, index=False)
        row_counts[rel(path)] = len(frame)
    return row_counts


def main() -> None:
    phase_artifacts_exist()
    row_counts = write_outputs()
    print("phase3_statistical_reframing")
    for path, count in sorted(row_counts.items()):
        print(f"{path}: rows={count}")


if __name__ == "__main__":
    main()
