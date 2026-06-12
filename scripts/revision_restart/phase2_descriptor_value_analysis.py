"""Restart Phase 2 ratio-versus-components descriptor analysis.

This deterministic post-processing script reads existing SPINE CSV outputs,
especially the Restart Phase 1 divider-residual table, and writes derived
descriptor-comparison artifacts. It does not modify raw source data, validated
model code, manuscript TeX source, or publication figures.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PHASE1 = ROOT / "results" / "revision_restart" / "phase1"
OUT = ROOT / "results" / "revision_restart" / "phase2"
FIG_DIR = OUT / "diagnostic_figures"
CV_SEED = 202608
FOLDS = 5
HEAD_SPECIFIC_LEAK_NS_PER_UM2 = 3e-6
DEFAULT_HEAD_RADIUS_UM = 0.35


@dataclass(frozen=True)
class Predictor:
    name: str
    family: str
    column: str


PREDICTORS: tuple[Predictor, ...] = (
    Predictor("SMI", "ratio", "SMI"),
    Predictor("Gamma_divider", "analytic_divider", "Gamma_divider"),
    Predictor("R_neck_Mohm", "component", "R_neck_Mohm"),
    Predictor("R_in_d_Mohm", "component", "R_in_d_Mohm"),
    Predictor("log10_R_neck_Mohm", "component_log", "log10_R_neck_Mohm"),
    Predictor("log10_R_in_d_Mohm", "component_log", "log10_R_in_d_Mohm"),
    Predictor("Zin_Mohm", "impedance", "Zin_Mohm"),
    Predictor("Ztransfer_Mohm", "impedance", "Ztransfer_Mohm"),
    Predictor("transfer_gain", "impedance", "transfer_gain"),
    Predictor("dynamic_SMI_abs", "dynamic_ratio", "dynamic_SMI_abs"),
    Predictor("synaptic_conductance_scale", "synaptic", "synaptic_conductance_scale"),
)

TARGETS: tuple[tuple[str, str], ...] = (
    ("observed_Gamma_h_to_d", "local_transfer"),
    ("residual", "divider_residual"),
    ("absolute_residual", "absolute_divider_residual"),
    ("Gamma_h_to_s", "somatic_transfer"),
    ("A_h_mV", "head_amplitude"),
)


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("/", "\\")


def safe_numeric(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame.columns:
        return pd.Series(np.nan, index=frame.index, dtype=float)
    return pd.to_numeric(frame[column], errors="coerce")


def finite_xy(frame: pd.DataFrame, x_col: str, y_col: str) -> pd.DataFrame:
    if x_col not in frame.columns or y_col not in frame.columns:
        return frame.iloc[0:0].copy()
    sub = frame[[x_col, y_col, "dataset", "regime", "active_or_passive"]].copy()
    sub[x_col] = pd.to_numeric(sub[x_col], errors="coerce")
    sub[y_col] = pd.to_numeric(sub[y_col], errors="coerce")
    sub = sub.replace([np.inf, -np.inf], np.nan).dropna(subset=[x_col, y_col])
    return sub


def pearson(x: Iterable[float], y: Iterable[float]) -> float:
    xs = np.asarray(list(x), dtype=float)
    ys = np.asarray(list(y), dtype=float)
    if xs.size < 2 or np.nanstd(xs) == 0 or np.nanstd(ys) == 0:
        return math.nan
    return float(np.corrcoef(xs, ys)[0, 1])


def spearman(x: Iterable[float], y: Iterable[float]) -> float:
    xs = pd.Series(list(x), dtype=float)
    ys = pd.Series(list(y), dtype=float)
    if len(xs) < 2 or xs.nunique() < 2 or ys.nunique() < 2:
        return math.nan
    return float(xs.rank(method="average").corr(ys.rank(method="average")))


def smi_class(value: float) -> str:
    if value < 0.25:
        return "low"
    if value < 0.75:
        return "intermediate"
    return "high"


def load_phase1_rows() -> pd.DataFrame:
    path = PHASE1 / "phase1_divider_residual_rows.csv"
    if not path.exists():
        raise FileNotFoundError(f"Phase 1 residual table missing: {path}")
    rows = pd.read_csv(path)
    rows["phase2_row_id"] = np.arange(len(rows), dtype=int)
    return rows


def source_row_lookup(rows: pd.DataFrame) -> dict[tuple[str, int], pd.Series]:
    cache: dict[str, pd.DataFrame] = {}
    lookup: dict[tuple[str, int], pd.Series] = {}
    for source in sorted(rows["source_file"].dropna().astype(str).unique()):
        path = ROOT / source
        if not path.exists():
            continue
        try:
            cache[source] = pd.read_csv(path)
        except Exception:
            continue
    for idx, row in rows.iterrows():
        source = str(row.get("source_file", ""))
        row_id = row.get("row_id", np.nan)
        if source not in cache or pd.isna(row_id):
            continue
        source_frame = cache[source]
        rid = int(row_id)
        if 0 <= rid < len(source_frame):
            lookup[(source, rid)] = source_frame.iloc[rid]
    return lookup


def extract_source_value(row: pd.Series, lookup: dict[tuple[str, int], pd.Series], candidates: list[str]) -> object:
    source = str(row.get("source_file", ""))
    row_id = row.get("row_id", np.nan)
    if pd.isna(row_id):
        return np.nan
    source_row = lookup.get((source, int(row_id)))
    if source_row is None:
        return np.nan
    lower = {str(c).lower(): c for c in source_row.index}
    for candidate in candidates:
        real = lower.get(candidate.lower())
        if real is not None:
            return source_row[real]
    return np.nan


def add_standardized_columns(rows: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    lookup = source_row_lookup(out)
    out["head_radius_um"] = [
        extract_source_value(row, lookup, ["head_radius_um"]) for _, row in out.iterrows()
    ]
    head_diameter = [
        extract_source_value(row, lookup, ["head_diameter_um"]) for _, row in out.iterrows()
    ]
    head_radius = pd.to_numeric(out["head_radius_um"], errors="coerce")
    head_diameter = pd.to_numeric(pd.Series(head_diameter, index=out.index), errors="coerce")
    out["head_radius_um"] = head_radius.where(head_radius.notna(), head_diameter / 2.0)
    out["head_radius_um"] = out["head_radius_um"].fillna(DEFAULT_HEAD_RADIUS_UM)
    out["SMI_class"] = [smi_class(float(v)) if pd.notna(v) else "" for v in safe_numeric(out, "SMI")]
    for col in ("SMI", "R_neck_Mohm", "R_in_d_Mohm", "Zin_Mohm", "Ztransfer_Mohm", "transfer_gain", "dynamic_SMI_abs"):
        vals = safe_numeric(out, col)
        out[f"log10_{col}"] = np.where(vals > 0, np.log10(vals), np.nan)
    out["source_head_radius_note"] = np.where(
        out["head_radius_um"].eq(DEFAULT_HEAD_RADIUS_UM),
        "default 0.35 um used when source row did not carry head size",
        "head size recovered from source row",
    )
    return out


def correlation_rows(table: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    groups: list[tuple[str, pd.DataFrame]] = [("all_nonexploratory", table[~table["exploratory_only"].astype(bool)])]
    groups.extend((str(regime), grp) for regime, grp in table.groupby("regime", dropna=False, sort=True))
    for target, target_family in TARGETS:
        for regime, group in groups:
            for predictor in PREDICTORS:
                sub = finite_xy(group, predictor.column, target)
                if len(sub) < 3:
                    continue
                x = sub[predictor.column].to_numpy(dtype=float)
                y = sub[target].to_numpy(dtype=float)
                rho = spearman(x, y)
                r = pearson(x, y)
                rows.append(
                    {
                        "target": target,
                        "target_family": target_family,
                        "regime": regime,
                        "predictor": predictor.name,
                        "predictor_family": predictor.family,
                        "n_rows": len(sub),
                        "spearman": rho,
                        "abs_spearman": abs(rho) if math.isfinite(rho) else math.nan,
                        "pearson": r,
                        "monotonic_direction": "positive" if math.isfinite(rho) and rho > 0 else "negative" if math.isfinite(rho) and rho < 0 else "undefined",
                    }
                )
    return pd.DataFrame(rows)


def ols_fit(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    design = np.column_stack([np.ones(len(y)), x])
    coeffs, *_ = np.linalg.lstsq(design, y, rcond=None)
    return coeffs, design @ coeffs


def metrics(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    resid = y - pred
    ss_res = float(np.sum(resid**2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    return {
        "r2": 1.0 - ss_res / ss_tot if ss_tot > 0 else math.nan,
        "mae": float(np.mean(np.abs(resid))),
        "rmse": float(np.sqrt(np.mean(resid**2))),
    }


def cv_predictions(x: np.ndarray, y: np.ndarray, seed: int = CV_SEED) -> tuple[np.ndarray, str]:
    n = len(y)
    if n < 3:
        return np.full_like(y, np.nan, dtype=float), "not_run_n_lt_3"
    if n < 30:
        folds = [np.array([i]) for i in range(n)]
        note = "leave_one_out_descriptive"
    else:
        rng = np.random.default_rng(seed)
        indices = np.arange(n)
        rng.shuffle(indices)
        folds = [fold for fold in np.array_split(indices, min(FOLDS, n)) if len(fold)]
        note = f"{len(folds)}_fold_seed_{seed}_descriptive"
    pred = np.empty(n, dtype=float)
    all_idx = np.arange(n)
    for fold in folds:
        train = np.setdiff1d(all_idx, fold)
        if len(train) <= x.shape[1]:
            pred[fold] = np.nan
            continue
        coeffs, _ = ols_fit(x[train, :], y[train])
        pred[fold] = np.column_stack([np.ones(len(fold)), x[fold, :]]) @ coeffs
    return pred, note


def model_comparison_rows(table: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    groups: list[tuple[str, pd.DataFrame]] = [("all_nonexploratory", table[~table["exploratory_only"].astype(bool)])]
    groups.extend((str(regime), grp) for regime, grp in table.groupby("regime", dropna=False, sort=True))
    scalar_models = {
        "SMI_linear": ["SMI"],
        "Gamma_divider_linear": ["Gamma_divider"],
        "log10_R_neck_linear": ["log10_R_neck_Mohm"],
        "log10_R_in_d_linear": ["log10_R_in_d_Mohm"],
        "component_pair_log10_OLS": ["log10_R_neck_Mohm", "log10_R_in_d_Mohm"],
        "component_pair_raw_OLS": ["R_neck_Mohm", "R_in_d_Mohm"],
        "impedance_pair_OLS": ["log10_Zin_Mohm", "transfer_gain"],
        "dynamic_plus_transfer_gain_OLS": ["dynamic_SMI_abs", "transfer_gain"],
        "synaptic_plus_components_OLS": ["log10_R_neck_Mohm", "log10_R_in_d_Mohm", "synaptic_conductance_scale"],
    }
    for target, target_family in TARGETS:
        for regime, group in groups:
            for model_name, columns in scalar_models.items():
                needed = columns + [target]
                missing = [c for c in needed if c not in group.columns]
                if missing:
                    continue
                sub = group[needed].replace([np.inf, -np.inf], np.nan).apply(pd.to_numeric, errors="coerce").dropna()
                if len(sub) < max(3, len(columns) + 2):
                    continue
                x = sub[columns].to_numpy(dtype=float)
                y = sub[target].to_numpy(dtype=float)
                coeffs, pred = ols_fit(x, y)
                fit_metrics = metrics(y, pred)
                cv_pred, cv_note = cv_predictions(x, y)
                cv_metric = metrics(y[~np.isnan(cv_pred)], cv_pred[~np.isnan(cv_pred)]) if np.isfinite(cv_pred).any() else {"r2": math.nan, "mae": math.nan, "rmse": math.nan}
                coef_text = "; ".join([f"intercept={coeffs[0]:.9g}"] + [f"{col}={coeffs[i+1]:.9g}" for i, col in enumerate(columns)])
                sign_text = "; ".join([f"{col}:{'positive' if coeffs[i+1] > 0 else 'negative' if coeffs[i+1] < 0 else 'zero'}" for i, col in enumerate(columns)])
                rows.append(
                    {
                        "target": target,
                        "target_family": target_family,
                        "regime": regime,
                        "model": model_name,
                        "predictors": ";".join(columns),
                        "n_rows": len(sub),
                        "in_sample_r2": fit_metrics["r2"],
                        "in_sample_mae": fit_metrics["mae"],
                        "in_sample_rmse": fit_metrics["rmse"],
                        "cv_r2": cv_metric["r2"],
                        "cv_mae": cv_metric["mae"],
                        "cv_rmse": cv_metric["rmse"],
                        "cv_note": cv_note,
                        "coefficients": coef_text,
                        "coefficient_signs": sign_text,
                        "method": "ordinary_least_squares_descriptive",
                    }
                )
    return pd.DataFrame(rows)


def target_summary(corr: pd.DataFrame, comps: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    keys = sorted(set(zip(corr["target"], corr["regime"])) | set(zip(comps["target"], comps["regime"])))
    for target, regime in keys:
        csub = corr[(corr["target"] == target) & (corr["regime"] == regime)].copy()
        msub = comps[(comps["target"] == target) & (comps["regime"] == regime)].copy()
        best_scalar = csub.sort_values("abs_spearman", ascending=False).head(1)
        smi = csub[csub["predictor"] == "SMI"].head(1)
        gamma = csub[csub["predictor"] == "Gamma_divider"].head(1)
        comp = msub[msub["model"] == "component_pair_log10_OLS"].head(1)
        best_model = msub.sort_values("cv_rmse", ascending=True).head(1)
        rows.append(
            {
                "target": target,
                "regime": regime,
                "best_scalar_descriptor": "" if best_scalar.empty else best_scalar.iloc[0]["predictor"],
                "best_scalar_abs_spearman": "" if best_scalar.empty else best_scalar.iloc[0]["abs_spearman"],
                "SMI_abs_spearman": "" if smi.empty else smi.iloc[0]["abs_spearman"],
                "Gamma_divider_abs_spearman": "" if gamma.empty else gamma.iloc[0]["abs_spearman"],
                "component_pair_log10_cv_rmse": "" if comp.empty else comp.iloc[0]["cv_rmse"],
                "component_pair_log10_cv_r2": "" if comp.empty else comp.iloc[0]["cv_r2"],
                "best_descriptive_model": "" if best_model.empty else best_model.iloc[0]["model"],
                "best_descriptive_model_cv_rmse": "" if best_model.empty else best_model.iloc[0]["cv_rmse"],
                "interpretation": interpretation_for(target, best_scalar, smi, gamma, comp),
            }
        )
    return pd.DataFrame(rows)


def interpretation_for(target: str, best_scalar: pd.DataFrame, smi: pd.DataFrame, gamma: pd.DataFrame, comp: pd.DataFrame) -> str:
    if target == "observed_Gamma_h_to_d":
        if not gamma.empty and not smi.empty and float(gamma.iloc[0]["abs_spearman"]) >= float(smi.iloc[0]["abs_spearman"]):
            return "Analytic divider transform is the appropriate first-order local-transfer coordinate."
        return "Raw SMI retains local-transfer ordering, but interpretation should stay tied to the divider relation."
    if target in ("residual", "absolute_residual"):
        return "Residual departures are not a raw-ratio discovery target; compare components, conductance, and impedance descriptors."
    if target == "Gamma_h_to_s":
        return "Somatic transfer depends on downstream filtering; local ratio alone is not sufficient."
    if target == "A_h_mV":
        return "Head amplitude requires conductance/load descriptors beyond the local ratio."
    return "Descriptor value is target and regime dependent."


def residual_predictor_summary(corr: pd.DataFrame, comps: pd.DataFrame) -> pd.DataFrame:
    csub = corr[corr["target"].isin(["residual", "absolute_residual"])].copy()
    msub = comps[comps["target"].isin(["residual", "absolute_residual"])].copy()
    rows: list[dict[str, object]] = []
    for target, regime in sorted(set(zip(csub["target"], csub["regime"]))):
        cc = csub[(csub["target"] == target) & (csub["regime"] == regime)].sort_values("abs_spearman", ascending=False)
        mm = msub[(msub["target"] == target) & (msub["regime"] == regime)].sort_values("cv_rmse", ascending=True)
        rows.append(
            {
                "target": target,
                "regime": regime,
                "best_scalar_predictor": "" if cc.empty else cc.iloc[0]["predictor"],
                "best_scalar_abs_spearman": "" if cc.empty else cc.iloc[0]["abs_spearman"],
                "SMI_abs_spearman": "" if cc[cc["predictor"] == "SMI"].empty else cc[cc["predictor"] == "SMI"].iloc[0]["abs_spearman"],
                "best_model": "" if mm.empty else mm.iloc[0]["model"],
                "best_model_cv_rmse": "" if mm.empty else mm.iloc[0]["cv_rmse"],
                "residual_interpretation": "Residual prediction is descriptive and design-dependent; strong residual associations mark departures from the DC divider limit rather than independent validation of SMI.",
            }
        )
    return pd.DataFrame(rows)


def attached_vs_omitted(table: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in table.iterrows():
        rneck = row.get("R_neck_Mohm", np.nan)
        rin = row.get("R_in_d_Mohm", np.nan)
        head_radius = row.get("head_radius_um", DEFAULT_HEAD_RADIUS_UM)
        try:
            rneck = float(rneck)
            rin = float(rin)
            head_radius = float(head_radius)
        except (TypeError, ValueError):
            continue
        if not all(math.isfinite(v) and v > 0 for v in (rneck, rin, head_radius)):
            continue
        head_area_um2 = 4.0 * math.pi * head_radius**2
        g_head_nS = HEAD_SPECIFIC_LEAK_NS_PER_UM2 * head_area_um2
        if g_head_nS <= 0:
            continue
        r_head_mohm = 1000.0 / g_head_nS
        attached_branch_mohm = rneck + r_head_mohm
        rin_attached = 1.0 / (1.0 / rin + 1.0 / attached_branch_mohm)
        smi_omitted = rneck / rin
        smi_attached = rneck / rin_attached
        divider_omitted = 1.0 / (1.0 + smi_omitted)
        divider_attached = 1.0 / (1.0 + smi_attached)
        rows.append(
            {
                "phase2_row_id": row["phase2_row_id"],
                "dataset": row["dataset"],
                "regime": row["regime"],
                "condition": row["condition"],
                "source_file": row["source_file"],
                "row_id": row["row_id"],
                "R_neck_Mohm": rneck,
                "R_in_d_omitted_Mohm": rin,
                "R_in_d_attached_Mohm": rin_attached,
                "absolute_difference_Mohm": rin_attached - rin,
                "relative_difference": (rin_attached - rin) / rin,
                "head_radius_um": head_radius,
                "head_leak_nS": g_head_nS,
                "head_leak_resistance_Mohm": r_head_mohm,
                "SMI_omitted": smi_omitted,
                "SMI_attached": smi_attached,
                "SMI_relative_change": (smi_attached - smi_omitted) / smi_omitted,
                "Gamma_divider_omitted": divider_omitted,
                "Gamma_divider_attached": divider_attached,
                "Gamma_divider_difference": divider_attached - divider_omitted,
                "SMI_class_omitted": smi_class(smi_omitted),
                "SMI_class_attached": smi_class(smi_attached),
                "class_assignment_changed": smi_class(smi_omitted) != smi_class(smi_attached),
                "method": "DC one-port reconstruction from omitted R_in,d plus passive head leak through neck",
                "caveat": "Uses existing row descriptors only; not a primary simulation rerun.",
            }
        )
    return pd.DataFrame(rows)


def recommendation_table(summary: pd.DataFrame, corr: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, row in summary.iterrows():
        target = row["target"]
        regime = row["regime"]
        csub = corr[(corr["target"] == target) & (corr["regime"] == regime)]
        dyn = csub[csub["predictor_family"].isin(["impedance", "dynamic_ratio"])].sort_values("abs_spearman", ascending=False).head(1)
        if target == "observed_Gamma_h_to_d":
            language = "Use analytic divider prediction for first-order local transfer."
            interp = "SMI is best read through the voltage-divider transform, not as a standalone empirical discovery."
        elif target in ("residual", "absolute_residual"):
            language = "Use component pair or impedance descriptors when residual precision matters."
            interp = "SMI is insufficient for explaining departures from the divider limit."
        elif target == "Gamma_h_to_s":
            language = "SMI is insufficient for somatic transfer outside constrained regimes."
            interp = "Downstream dendrite-to-soma filtering dominates this target."
        elif target == "A_h_mV":
            language = "SMI is insufficient for amplitude prediction."
            interp = "Conductance scale and input impedance are needed for amplitude."
        else:
            language = "SMI is appropriate as a compact local ordering coordinate."
            interp = "Use target-specific qualifiers."
        rows.append(
            {
                "target": target,
                "regime": regime,
                "best_scalar_descriptor": row.get("best_scalar_descriptor", ""),
                "best_scalar_metric": row.get("best_scalar_abs_spearman", ""),
                "two_variable_model_metric": row.get("component_pair_log10_cv_rmse", ""),
                "smi_metric": row.get("SMI_abs_spearman", ""),
                "gamma_divider_metric": row.get("Gamma_divider_abs_spearman", ""),
                "dynamic_or_impedance_metric_if_available": "" if dyn.empty else f"{dyn.iloc[0]['predictor']} abs_spearman={dyn.iloc[0]['abs_spearman']}",
                "recommended_descriptor_language": language,
                "interpretation": interp,
                "caveats": "Descriptive comparison across designed/sensitivity rows; not population inference.",
            }
        )
    return pd.DataFrame(rows)


def source_manifest(outputs: list[str], sources: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for output in outputs:
        for source in sources:
            rows.append(
                {
                    "derived_file": output,
                    "source_file": source,
                    "transformation": "deterministic Restart Phase 2 descriptor post-processing",
                    "notes": "Raw source CSV was read only and not modified.",
                }
            )
    return pd.DataFrame(rows)


def scaled(value: float, vmin: float, vmax: float, out_min: float, out_max: float) -> float:
    if not math.isfinite(value) or not math.isfinite(vmin) or not math.isfinite(vmax) or vmax == vmin:
        return 0.5 * (out_min + out_max)
    return out_min + (value - vmin) * (out_max - out_min) / (vmax - vmin)


def write_scatter_svg(frame: pd.DataFrame, x_col: str, y_col: str, path: Path, title: str) -> None:
    sub = frame[[x_col, y_col]].replace([np.inf, -np.inf], np.nan).apply(pd.to_numeric, errors="coerce").dropna()
    if sub.empty:
        return
    width, height = 720, 470
    left, right, top, bottom = 78, 28, 52, 68
    xs = sub[x_col].to_numpy(dtype=float)
    ys = sub[y_col].to_numpy(dtype=float)
    xmin, xmax = float(np.min(xs)), float(np.max(xs))
    ymin, ymax = float(np.min(ys)), float(np.max(ys))
    if ymin == ymax:
        ymin -= 0.1
        ymax += 0.1
    ypad = 0.05 * (ymax - ymin)
    ymin -= ypad
    ymax += ypad
    elements = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<desc>Restart Phase 2 diagnostic-only figure; not a publication figure.</desc>",
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="28" text-anchor="middle" font-family="Arial" font-size="16" font-weight="700">{title}</text>',
        f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#222"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#222"/>',
        f'<text x="{width/2}" y="{height-24}" text-anchor="middle" font-family="Arial" font-size="12">{x_col}</text>',
        f'<text x="18" y="{height/2}" text-anchor="middle" font-family="Arial" font-size="12" transform="rotate(-90 18 {height/2})">{y_col}</text>',
    ]
    for x, y in zip(xs, ys):
        sx = scaled(float(x), xmin, xmax, left, width - right)
        sy = scaled(float(y), ymin, ymax, height - bottom, top)
        elements.append(f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="2.3" fill="#2563EB" fill-opacity="0.26"/>')
    elements.append("</svg>")
    path.write_text("\n".join(elements), encoding="utf-8")


def write_diagnostic_figures(table: pd.DataFrame, attached: pd.DataFrame) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    write_scatter_svg(table, "Gamma_divider", "observed_Gamma_h_to_d", FIG_DIR / "phase2_observed_local_vs_gamma_divider.svg", "Observed local transfer vs divider")
    write_scatter_svg(table, "SMI", "residual", FIG_DIR / "phase2_residual_vs_smi.svg", "Divider residual vs SMI")
    write_scatter_svg(table, "R_neck_Mohm", "residual", FIG_DIR / "phase2_residual_vs_r_neck.svg", "Divider residual vs R_neck")
    write_scatter_svg(table, "R_in_d_Mohm", "residual", FIG_DIR / "phase2_residual_vs_r_in_d.svg", "Divider residual vs R_in,d")
    write_scatter_svg(table, "dynamic_SMI_abs", "residual", FIG_DIR / "phase2_residual_vs_dynamic_smi.svg", "Divider residual vs dynamic SMI")
    if not attached.empty:
        write_scatter_svg(attached, "R_in_d_omitted_Mohm", "R_in_d_attached_Mohm", FIG_DIR / "phase2_attached_vs_omitted_rind.svg", "Attached vs omitted R_in,d")
        write_scatter_svg(attached, "SMI_omitted", "SMI_attached", FIG_DIR / "phase2_attached_vs_omitted_smi.svg", "Attached vs omitted SMI")


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, quoting=csv.QUOTE_MINIMAL)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = load_phase1_rows()
    table = add_standardized_columns(rows)
    corr = correlation_rows(table)
    comps = model_comparison_rows(table)
    summary = target_summary(corr, comps)
    residual_summary = residual_predictor_summary(corr, comps)
    attached = attached_vs_omitted(table)
    recommendations = recommendation_table(summary, corr)

    output_names = [
        "phase2_standardized_descriptor_table.csv",
        "phase2_scalar_descriptor_correlations.csv",
        "phase2_ratio_vs_components_model_comparison.csv",
        "phase2_target_specific_descriptor_summary.csv",
        "phase2_residual_predictor_summary.csv",
        "phase2_spine_omitted_vs_attached_rind.csv",
        "phase2_descriptor_recommendation_table.csv",
        "phase2_source_manifest.csv",
        "diagnostic_figures/*.svg",
    ]
    sources = sorted(set(["results\\revision_restart\\phase1\\phase1_divider_residual_rows.csv"] + table["source_file"].dropna().astype(str).unique().tolist()))
    manifest = source_manifest(output_names, sources)

    write_csv(OUT / "phase2_standardized_descriptor_table.csv", table)
    write_csv(OUT / "phase2_scalar_descriptor_correlations.csv", corr)
    write_csv(OUT / "phase2_ratio_vs_components_model_comparison.csv", comps)
    write_csv(OUT / "phase2_target_specific_descriptor_summary.csv", summary)
    write_csv(OUT / "phase2_residual_predictor_summary.csv", residual_summary)
    write_csv(OUT / "phase2_spine_omitted_vs_attached_rind.csv", attached)
    write_csv(OUT / "phase2_descriptor_recommendation_table.csv", recommendations)
    write_csv(OUT / "phase2_source_manifest.csv", manifest)
    write_diagnostic_figures(table, attached)

    print("phase2_descriptor_value_analysis")
    print(f"standardized_rows={len(table)}")
    print(f"correlation_rows={len(corr)}")
    print(f"model_comparison_rows={len(comps)}")
    print(f"attached_vs_omitted_rows={len(attached)}")
    print(f"diagnostic_figures={len(list(FIG_DIR.glob('*.svg')))}")
    local = summary[(summary["target"] == "observed_Gamma_h_to_d") & (summary["regime"] == "all_nonexploratory")]
    if not local.empty:
        print(f"local_all_best_scalar={local.iloc[0]['best_scalar_descriptor']}")
        print(f"local_all_component_pair_cv_rmse={local.iloc[0]['component_pair_log10_cv_rmse']}")
    residual = residual_summary[(residual_summary["target"] == "absolute_residual") & (residual_summary["regime"] == "all_nonexploratory")]
    if not residual.empty:
        print(f"absolute_residual_all_best_scalar={residual.iloc[0]['best_scalar_predictor']}")


if __name__ == "__main__":
    main()
