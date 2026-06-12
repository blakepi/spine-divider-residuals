"""Restart Phase 1 analytic-divider residual analysis.

Reads existing SPINE result CSVs, computes the DC voltage-divider prediction
Gamma_divider = 1 / (1 + SMI), and writes derived residual tables. This script
does not modify raw source data or validated model code.
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
OUT = ROOT / "results" / "revision_restart" / "phase1"
FIG_DIR = OUT / "diagnostic_figures"


@dataclass(frozen=True)
class DatasetSpec:
    dataset: str
    phase_source: str
    path: str
    regime: str
    active_or_passive: str
    include_active_target: bool = False
    exploratory: bool = False
    caveat: str = ""


DATASETS: tuple[DatasetSpec, ...] = (
    DatasetSpec(
        "phase02_baseline_target_cases",
        "phase02",
        "results/phase02/Figure2_representative_summary.csv",
        "baseline_reference_targets",
        "passive",
    ),
    DatasetSpec(
        "phase02_fixed_load_geometry_sweep",
        "phase02",
        "results/phase02/Figure3_geometry_sweep.csv",
        "fixed_load_geometry_sweep",
        "passive",
    ),
    DatasetSpec(
        "phase02_matched_neck_load_sweep",
        "phase02",
        "results/phase02/Figure4_matched_neck_heterogeneous_load.csv",
        "matched_neck_heterogeneous_load",
        "passive",
    ),
    DatasetSpec(
        "phase02_dt_convergence_intermediate",
        "phase02",
        "results/phase02/convergence_dt_intermediate.csv",
        "timestep_convergence_intermediate",
        "passive",
        caveat="Validation rows repeat the intermediate reference condition across dt.",
    ),
    DatasetSpec(
        "phase03_passive_morphology_challenge",
        "phase03",
        "results/phase03/smi_challenge_suite.csv",
        "passive_morphology_challenge",
        "passive",
    ),
    DatasetSpec(
        "phase03_spatial_convergence",
        "phase03",
        "results/phase03/spatial_convergence.csv",
        "spatial_convergence",
        "passive",
        caveat="Spatial convergence rows are validation rows, not independent biological samples.",
    ),
    DatasetSpec(
        "phase04_active_nonlinear_challenge",
        "phase04",
        "results/phase04/active_smi_challenge_suite.csv",
        "active_nonlinear_challenge",
        "designed_active_stress_test",
    ),
    DatasetSpec(
        "phase05_global_uncertainty_N96",
        "phase05",
        "results/phase05/global_uncertainty_samples.csv",
        "global_uncertainty_N96",
        "passive",
        include_active_target=True,
        caveat="Deterministic uncertainty-design rows; not biological samples.",
    ),
    DatasetSpec(
        "phase05_1_global_uncertainty_N96",
        "phase05_1",
        "results/phase05_1/global_uncertainty_samples_N96.csv",
        "progressive_uncertainty_N96",
        "passive",
        include_active_target=True,
        caveat="Deterministic uncertainty-design rows; not biological samples.",
    ),
    DatasetSpec(
        "phase05_1_global_uncertainty_N192",
        "phase05_1",
        "results/phase05_1/global_uncertainty_samples_N192.csv",
        "progressive_uncertainty_N192",
        "passive",
        include_active_target=True,
        caveat="Deterministic uncertainty-design rows; not biological samples.",
    ),
    DatasetSpec(
        "phase05_1_global_uncertainty_N384",
        "phase05_1",
        "results/phase05_1/global_uncertainty_samples_N384.csv",
        "progressive_uncertainty_N384",
        "passive",
        include_active_target=True,
        caveat="Deterministic uncertainty-design rows; not biological samples.",
    ),
    DatasetSpec(
        "phase05_1_global_uncertainty_N768",
        "phase05_1",
        "results/phase05_1/global_uncertainty_samples_N768.csv",
        "progressive_uncertainty_N768",
        "passive",
        include_active_target=True,
        caveat="Deterministic uncertainty-design rows; not biological samples.",
    ),
    DatasetSpec(
        "phase06_exploratory_scenario_metrics",
        "phase06",
        "results/phase06/scenario_metrics.csv",
        "exploratory_scenarios",
        "exploratory_active_stress_test",
        exploratory=True,
        caveat="Exploratory supplemental scenarios only; no disease or clinical claim.",
    ),
    DatasetSpec(
        "phase06_exploratory_uncertainty_samples",
        "phase06",
        "results/phase06/scenario_uncertainty_samples.csv",
        "exploratory_scenario_uncertainty",
        "exploratory_active_stress_test",
        exploratory=True,
        caveat="N=8 per exploratory scenario sensitivity screen; no biological inference.",
    ),
    DatasetSpec(
        "phase06_exploratory_matched_baseline_comparisons",
        "phase06",
        "results/phase06/matched_baseline_comparisons.csv",
        "exploratory_matched_baseline_comparisons",
        "exploratory_active_stress_test",
        exploratory=True,
        caveat="Comparison table uses *_value columns and may overlap scenario_metrics.",
    ),
    DatasetSpec(
        "phase06_exploratory_mechanistic_decomposition",
        "phase06",
        "results/phase06/mechanistic_decomposition.csv",
        "exploratory_mechanistic_decomposition",
        "exploratory_active_stress_test",
        exploratory=True,
        caveat="Exploratory decomposition rows only.",
    ),
)


INVENTORY_ROOTS = (
    "results/phase02",
    "results/phase03",
    "results/phase04",
    "results/phase05",
    "results/phase05_1",
    "results/phase06",
    "results/revision_v2/r3",
    "results/revision_v2/r4",
)


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("/", "\\")


def first_existing_column(columns: Iterable[str], candidates: Iterable[str]) -> str | None:
    cols = list(columns)
    lower_to_real = {c.lower(): c for c in cols}
    for candidate in candidates:
        if candidate.lower() in lower_to_real:
            return lower_to_real[candidate.lower()]
    return None


def find_contains_column(columns: Iterable[str], tokens: Iterable[str]) -> str | None:
    for col in columns:
        low = col.lower()
        if all(token.lower() in low for token in tokens):
            return col
    return None


def safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def infer_columns(df: pd.DataFrame) -> dict[str, str | None]:
    cols = list(df.columns)
    return {
        "smi": first_existing_column(cols, ["SMI", "SMI_value", "true_SMI"]),
        "r_neck": first_existing_column(
            cols,
            [
                "R_neck_Mohm",
                "neck_resistance_Mohm",
                "R_neck_Mohm_value",
                "effective_R_neck_Mohm",
                "true_R_neck_Mohm",
            ],
        ),
        "r_in_d": first_existing_column(cols, ["R_in_d_Mohm", "R_in_d_Mohm_value", "R_in_d"]),
        "gamma": first_existing_column(cols, ["Gamma_h_to_d", "Gamma_h_to_d_value"]),
        "gamma_active": first_existing_column(cols, ["active_Gamma_h_to_d"]),
        "gamma_s": first_existing_column(cols, ["Gamma_h_to_s", "Gamma_h_to_s_value"]),
        "gamma_s_active": first_existing_column(cols, ["active_Gamma_h_to_s"]),
        "a_h": first_existing_column(cols, ["A_h_mV", "A_h_mV_value"]),
        "a_h_active": first_existing_column(cols, ["active_A_h_mV"]),
        "a_d": first_existing_column(cols, ["A_d_mV", "A_d_mV_value"]),
        "a_s": first_existing_column(cols, ["A_s_mV", "A_s_mV_value"]),
        "condition": first_existing_column(cols, ["condition", "scenario", "case", "experiment", "protocol"]),
        "case": first_existing_column(cols, ["case", "condition", "scenario"]),
        "protocol": first_existing_column(cols, ["protocol", "active_profile", "event_pattern"]),
        "experiment": first_existing_column(cols, ["experiment", "scenario", "group"]),
        "synaptic_scale": first_existing_column(cols, ["synaptic_g_scale", "synaptic_conductance_scale"]),
        "neck_length": first_existing_column(cols, ["neck_length_um"]),
        "neck_radius": first_existing_column(cols, ["neck_radius_um"]),
        "path_length": first_existing_column(cols, ["path_length_um"]),
        "branch_order": first_existing_column(cols, ["branch_order"]),
        "membrane_area": first_existing_column(cols, ["membrane_area_um2"]),
        "zin": first_existing_column(
            cols,
            ["Zin_50Hz_Mohm", "active_Zin_50Hz_Mohm", "active_frozen_Zin_50Hz_Mohm", "Zin_Mohm"],
        ),
        "ztransfer": first_existing_column(
            cols,
            ["Ztransfer_50Hz_Mohm", "active_frozen_Ztransfer_50Hz_Mohm", "Z_transfer_abs_Mohm"],
        ),
        "transfer_gain": first_existing_column(
            cols,
            ["transfer_gain_50Hz", "active_transfer_gain_50Hz", "active_frozen_transfer_gain_50Hz", "transfer_gain"],
        ),
        "dynamic_smi": first_existing_column(cols, ["dynamic_SMI_abs_50Hz", "active_dynamic_SMI_abs_50Hz"]),
    }


def make_label(row: pd.Series, mapping: dict[str, str | None], fallback: str) -> str:
    pieces: list[str] = []
    for key in ("experiment", "case", "protocol"):
        col = mapping.get(key)
        if col and col in row.index and pd.notna(row[col]):
            text = str(row[col])
            if text and text not in pieces:
                pieces.append(text)
    return " / ".join(pieces) if pieces else fallback


def collect_rows() -> tuple[pd.DataFrame, pd.DataFrame]:
    residual_rows: list[dict[str, object]] = []
    inventory_rows: list[dict[str, object]] = []

    specs_by_path = {spec.path.replace("/", "\\").lower(): spec for spec in DATASETS}
    primary_paths = {spec.path.replace("/", "\\").lower() for spec in DATASETS}

    for root_name in INVENTORY_ROOTS:
        root = ROOT / root_name
        if not root.exists():
            inventory_rows.append(
                {
                    "file_path": root_name,
                    "row_count": "",
                    "relevant_columns": "",
                    "analytic_divider_computable": "no",
                    "observed_gamma_available": "no",
                    "regime_labels_available": "no",
                    "residual_analysis_possible": "no",
                    "used_in_phase1_primary": "no",
                    "caveats": "Listed input directory missing.",
                }
            )
            continue
        for path in sorted(root.rglob("*.csv")):
            try:
                df = load_csv(path)
            except Exception as exc:  # pragma: no cover - defensive inventory path
                inventory_rows.append(
                    {
                        "file_path": rel(path),
                        "row_count": "",
                        "relevant_columns": "",
                        "analytic_divider_computable": "no",
                        "observed_gamma_available": "no",
                        "regime_labels_available": "unknown",
                        "residual_analysis_possible": "no",
                        "used_in_phase1_primary": "no",
                        "caveats": f"CSV read failed: {type(exc).__name__}: {exc}",
                    }
                )
                continue

            mapping = infer_columns(df)
            relevant = [
                c
                for c in df.columns
                if any(
                    token in c.lower()
                    for token in (
                        "smi",
                        "r_neck",
                        "neck_resistance",
                        "r_in",
                        "gamma_h_to_d",
                        "gamma_h_to_s",
                        "a_h",
                        "zin",
                        "transfer",
                        "scenario",
                        "condition",
                        "case",
                        "regime",
                        "active",
                        "protocol",
                    )
                )
            ]
            analytic = mapping["smi"] is not None
            gamma_available = mapping["gamma"] is not None or mapping["gamma_active"] is not None
            possible = analytic and gamma_available
            rel_path = rel(path)
            rel_key = rel_path.lower()
            is_r4_snapshot = rel_key.startswith("results\\revision_v2\\r4\\")
            used = rel_key in primary_paths
            caveats: list[str] = []
            if is_r4_snapshot:
                caveats.append("R4 figure-data snapshot; not used in primary residual table to avoid duplicate rows.")
            spec = specs_by_path.get(rel_key)
            if spec and spec.caveat:
                caveats.append(spec.caveat)
            if not possible and relevant:
                caveats.append("Relevant descriptors present but SMI and observed Gamma_h_to_d are not both available.")

            inventory_rows.append(
                {
                    "file_path": rel_path,
                    "row_count": len(df),
                    "relevant_columns": "; ".join(relevant),
                    "analytic_divider_computable": "yes" if analytic else "no",
                    "observed_gamma_available": "yes" if gamma_available else "no",
                    "regime_labels_available": "yes"
                    if any(mapping[k] for k in ("condition", "case", "protocol", "experiment"))
                    else "no",
                    "residual_analysis_possible": "yes" if possible else "no",
                    "used_in_phase1_primary": "yes" if used else "no",
                    "caveats": " ".join(caveats),
                }
            )

            if used:
                spec = specs_by_path[rel_key]
                add_residual_rows(df, mapping, spec, path, residual_rows)

    return pd.DataFrame(residual_rows), pd.DataFrame(inventory_rows)


def add_residual_rows(
    df: pd.DataFrame,
    mapping: dict[str, str | None],
    spec: DatasetSpec,
    path: Path,
    out_rows: list[dict[str, object]],
) -> None:
    if mapping["smi"] is None:
        return
    target_defs = [
        ("Gamma_h_to_d_peak", mapping["gamma"], mapping["gamma_s"], mapping["a_h"], spec.active_or_passive),
    ]
    if spec.include_active_target and mapping["gamma_active"]:
        target_defs.append(
            (
                "active_Gamma_h_to_d_peak",
                mapping["gamma_active"],
                mapping["gamma_s_active"],
                mapping["a_h_active"],
                "active_uncertainty_design",
            )
        )

    for target_type, gamma_col, gamma_s_col, a_h_col, active_label in target_defs:
        if not gamma_col:
            continue
        smi = safe_numeric(df[mapping["smi"]])
        gamma = safe_numeric(df[gamma_col])
        valid = smi.notna() & gamma.notna() & np.isfinite(smi) & np.isfinite(gamma) & (smi > -0.999999)
        for idx in df.index[valid]:
            row = df.loc[idx]
            smi_value = float(smi.loc[idx])
            observed = float(gamma.loc[idx])
            divider = 1.0 / (1.0 + smi_value)
            residual = observed - divider
            rel_error = residual / divider if abs(divider) > 1e-15 else math.nan
            record: dict[str, object] = {
                "dataset": spec.dataset,
                "phase_source": spec.phase_source,
                "condition": make_label(row, mapping, f"row_{idx}"),
                "regime": spec.regime,
                "active_or_passive": active_label,
                "target_type": target_type,
                "source_file": rel(path),
                "row_id": int(idx),
                "SMI": smi_value,
                "observed_Gamma_h_to_d": observed,
                "Gamma_divider": divider,
                "residual": residual,
                "absolute_residual": abs(residual),
                "relative_error": rel_error,
                "absolute_relative_error": abs(rel_error) if np.isfinite(rel_error) else math.nan,
                "log10_absolute_relative_error": math.log10(abs(rel_error))
                if np.isfinite(rel_error) and abs(rel_error) > 0
                else math.nan,
                "exploratory_only": bool(spec.exploratory),
                "source_caveat": spec.caveat,
            }
            optional_map = {
                "R_neck_Mohm": mapping["r_neck"],
                "R_in_d_Mohm": mapping["r_in_d"],
                "A_h_mV": a_h_col,
                "A_d_mV": mapping["a_d"],
                "A_s_mV": mapping["a_s"],
                "Gamma_h_to_s": gamma_s_col,
                "synaptic_conductance_scale": mapping["synaptic_scale"],
                "neck_length_um": mapping["neck_length"],
                "neck_radius_um": mapping["neck_radius"],
                "path_length_um": mapping["path_length"],
                "branch_order": mapping["branch_order"],
                "membrane_area_um2": mapping["membrane_area"],
                "Zin_Mohm": mapping["zin"],
                "Ztransfer_Mohm": mapping["ztransfer"],
                "transfer_gain": mapping["transfer_gain"],
                "dynamic_SMI_abs": mapping["dynamic_smi"],
            }
            for out_col, source_col in optional_map.items():
                if source_col and source_col in row.index:
                    value = row[source_col]
                    record[out_col] = value
            out_rows.append(record)


def percentile(series: pd.Series, q: float) -> float:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return math.nan
    return float(np.percentile(clean.to_numpy(dtype=float), q))


def spearman(x: pd.Series, y: pd.Series) -> float:
    xnum = pd.to_numeric(x, errors="coerce")
    ynum = pd.to_numeric(y, errors="coerce")
    valid = xnum.notna() & ynum.notna()
    if valid.sum() < 2:
        return math.nan
    if xnum[valid].nunique() < 2 or ynum[valid].nunique() < 2:
        return math.nan
    return float(xnum[valid].rank(method="average").corr(ynum[valid].rank(method="average")))


def summarize(rows: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    summaries: list[dict[str, object]] = []
    if rows.empty:
        return pd.DataFrame()
    for keys, group in rows.groupby(group_cols, dropna=False, sort=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        summary: dict[str, object] = dict(zip(group_cols, keys))
        residual = pd.to_numeric(group["residual"], errors="coerce")
        abs_residual = pd.to_numeric(group["absolute_residual"], errors="coerce")
        abs_rel = pd.to_numeric(group["absolute_relative_error"], errors="coerce")
        observed = pd.to_numeric(group["observed_Gamma_h_to_d"], errors="coerce")
        divider = pd.to_numeric(group["Gamma_divider"], errors="coerce")
        diff = observed - divider
        summary.update(
            {
                "n_rows": int(len(group)),
                "median_observed_Gamma_h_to_d": float(observed.median()),
                "median_Gamma_divider": float(divider.median()),
                "median_residual": float(residual.median()),
                "median_absolute_residual": float(abs_residual.median()),
                "median_absolute_relative_error": float(abs_rel.median()),
                "residual_p05": percentile(residual, 5),
                "residual_p95": percentile(residual, 95),
                "maximum_absolute_residual": float(abs_residual.max()),
                "spearman_SMI_vs_observed_Gamma_h_to_d": spearman(group["SMI"], observed),
                "spearman_Gamma_divider_vs_observed_Gamma_h_to_d": spearman(divider, observed),
                "rmse_observed_vs_divider": float(math.sqrt(np.nanmean(np.square(diff.to_numpy(dtype=float))))),
                "mae_observed_vs_divider": float(np.nanmean(np.abs(diff.to_numpy(dtype=float)))),
            }
        )
        summaries.append(summary)
    return pd.DataFrame(summaries)


def make_outliers(rows: pd.DataFrame, n: int = 12) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    if rows.empty:
        return pd.DataFrame()
    specs = (
        ("largest_absolute_residual", "absolute_residual", False),
        ("largest_absolute_relative_error", "absolute_relative_error", False),
        ("divider_overprediction_most_negative_residual", "residual", True),
        ("divider_underprediction_most_positive_residual", "residual", False),
    )
    for category, col, ascending in specs:
        subset = rows.replace([np.inf, -np.inf], np.nan).dropna(subset=[col])
        subset = subset.sort_values(col, ascending=ascending).head(n).copy()
        subset.insert(0, "outlier_category", category)
        parts.append(subset)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def write_manifest(inventory: pd.DataFrame, rows: pd.DataFrame) -> pd.DataFrame:
    used_sources = sorted(rows["source_file"].unique()) if not rows.empty else []
    manifest_rows: list[dict[str, object]] = []
    outputs = {
        "phase1_data_inventory.csv": "schema discovery for all candidate CSVs",
        "phase1_divider_residual_rows.csv": "row-level Gamma_divider and residual calculation",
        "phase1_divider_residual_summary_by_dataset.csv": "descriptive summaries grouped by dataset and target",
        "phase1_divider_residual_summary_by_regime.csv": "descriptive summaries grouped by regime and active/passive label",
        "phase1_baseline_target_residuals.csv": "subset of low/intermediate/high baseline target cases",
        "phase1_active_passive_residual_comparison.csv": "descriptive summaries grouped by active/passive label",
        "phase1_residual_outlier_cases.csv": "largest residual and relative-error cases",
        "diagnostic_figures/*.svg": "diagnostic-only plots derived from phase1_divider_residual_rows.csv",
    }
    for output, transformation in outputs.items():
        for source in used_sources:
            inv = inventory[inventory["file_path"] == source]
            columns_used = ""
            source_rows = ""
            notes = ""
            if not inv.empty:
                columns_used = str(inv.iloc[0]["relevant_columns"])
                source_rows = inv.iloc[0]["row_count"]
                notes = str(inv.iloc[0]["caveats"])
            manifest_rows.append(
                {
                    "derived_file": output,
                    "source_file": source,
                    "source_columns_used": columns_used,
                    "row_count": source_rows,
                    "transformation": transformation,
                    "notes": notes,
                }
            )
    return pd.DataFrame(manifest_rows)


def scaled(value: float, vmin: float, vmax: float, out_min: float, out_max: float) -> float:
    if not np.isfinite(value) or not np.isfinite(vmin) or not np.isfinite(vmax) or vmax == vmin:
        return (out_min + out_max) / 2.0
    return out_min + (value - vmin) * (out_max - out_min) / (vmax - vmin)


def write_svg_scatter(
    rows: pd.DataFrame,
    x_col: str,
    y_col: str,
    path: Path,
    title: str,
    x_label: str,
    y_label: str,
    analytic_curve: bool = False,
) -> None:
    subset = rows[[x_col, y_col, "active_or_passive"]].replace([np.inf, -np.inf], np.nan).dropna()
    if subset.empty:
        return
    width, height = 760, 520
    left, right, top, bottom = 80, 30, 55, 75
    xvals = subset[x_col].astype(float)
    yvals = subset[y_col].astype(float)
    xmin, xmax = float(xvals.min()), float(xvals.max())
    ymin, ymax = float(yvals.min()), float(yvals.max())
    if analytic_curve and x_col == "SMI":
        ymins = min(ymin, 1.0 / (1.0 + xmax))
        ymaxs = max(ymax, 1.0 / (1.0 + xmin))
        ymin, ymax = ymins, ymaxs
    if ymin == ymax:
        ymin -= 0.1
        ymax += 0.1
    pad_y = 0.05 * (ymax - ymin)
    ymin -= pad_y
    ymax += pad_y
    colors = {
        "passive": "#2B6CB0",
        "designed_active_stress_test": "#C2410C",
        "active_uncertainty_design": "#9D174D",
        "exploratory_active_stress_test": "#047857",
    }
    elements = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<desc>Restart Phase 1 diagnostic-only figure; not a publication figure.</desc>",
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width/2}" y="28" text-anchor="middle" font-family="Arial" font-size="17" font-weight="700">{title}</text>',
        f'<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#222" stroke-width="1"/>',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#222" stroke-width="1"/>',
        f'<text x="{width/2}" y="{height-25}" text-anchor="middle" font-family="Arial" font-size="13">{x_label}</text>',
        f'<text x="20" y="{height/2}" text-anchor="middle" font-family="Arial" font-size="13" transform="rotate(-90 20 {height/2})">{y_label}</text>',
    ]
    if analytic_curve and x_col == "SMI":
        pts = []
        for x in np.linspace(max(0.0, xmin), xmax, 160):
            y = 1.0 / (1.0 + x)
            sx = scaled(float(x), xmin, xmax, left, width - right)
            sy = scaled(float(y), ymin, ymax, height - bottom, top)
            pts.append(f"{sx:.2f},{sy:.2f}")
        elements.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#111" stroke-width="2"/>')
        elements.append(
            f'<text x="{width-right-5}" y="{top+18}" text-anchor="end" font-family="Arial" font-size="12">1/(1+SMI)</text>'
        )
    for _, row in subset.iterrows():
        x = scaled(float(row[x_col]), xmin, xmax, left, width - right)
        y = scaled(float(row[y_col]), ymin, ymax, height - bottom, top)
        color = colors.get(str(row["active_or_passive"]), "#555")
        elements.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.8" fill="{color}" fill-opacity="0.38"/>')
    legend_y = 55
    for label, color in colors.items():
        if label in set(subset["active_or_passive"].astype(str)):
            elements.append(f'<rect x="{width-245}" y="{legend_y-10}" width="10" height="10" fill="{color}" fill-opacity="0.7"/>')
            elements.append(f'<text x="{width-230}" y="{legend_y}" font-family="Arial" font-size="11">{label}</text>')
            legend_y += 16
    elements.append("</svg>")
    path.write_text("\n".join(elements), encoding="utf-8")


def write_figures(rows: pd.DataFrame) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    write_svg_scatter(
        rows,
        "SMI",
        "observed_Gamma_h_to_d",
        FIG_DIR / "phase1_observed_gamma_vs_smi.svg",
        "Observed local transfer vs SMI",
        "SMI",
        "observed Gamma_h_to_d",
        analytic_curve=True,
    )
    write_svg_scatter(
        rows,
        "SMI",
        "residual",
        FIG_DIR / "phase1_residual_vs_smi.svg",
        "Divider residual vs SMI",
        "SMI",
        "observed - divider",
    )
    write_svg_scatter(
        rows,
        "SMI",
        "absolute_residual",
        FIG_DIR / "phase1_absolute_residual_vs_smi.svg",
        "Absolute divider residual vs SMI",
        "SMI",
        "|observed - divider|",
    )
    write_svg_scatter(
        rows,
        "Gamma_divider",
        "observed_Gamma_h_to_d",
        FIG_DIR / "phase1_observed_vs_divider.svg",
        "Observed local transfer vs divider prediction",
        "Gamma_divider",
        "observed Gamma_h_to_d",
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows, inventory = collect_rows()
    rows = rows.sort_values(["dataset", "target_type", "row_id"]).reset_index(drop=True)

    summary_dataset = summarize(rows, ["dataset", "target_type"])
    summary_regime = summarize(rows, ["regime", "active_or_passive", "target_type"])
    baseline = rows[rows["dataset"] == "phase02_baseline_target_cases"].copy()
    active_passive = summarize(rows, ["active_or_passive", "target_type"])
    outliers = make_outliers(rows)
    manifest = write_manifest(inventory, rows)

    rows.to_csv(OUT / "phase1_divider_residual_rows.csv", index=False)
    summary_dataset.to_csv(OUT / "phase1_divider_residual_summary_by_dataset.csv", index=False)
    summary_regime.to_csv(OUT / "phase1_divider_residual_summary_by_regime.csv", index=False)
    baseline.to_csv(OUT / "phase1_baseline_target_residuals.csv", index=False)
    active_passive.to_csv(OUT / "phase1_active_passive_residual_comparison.csv", index=False)
    outliers.to_csv(OUT / "phase1_residual_outlier_cases.csv", index=False)
    inventory.to_csv(OUT / "phase1_data_inventory.csv", index=False)
    manifest.to_csv(OUT / "phase1_source_manifest.csv", index=False)
    write_figures(rows)

    print("phase1_divider_residual_analysis")
    print(f"datasets_used={rows['dataset'].nunique() if not rows.empty else 0}")
    print(f"residual_rows={len(rows)}")
    print(f"inventory_rows={len(inventory)}")
    print(f"baseline_rows={len(baseline)}")
    print(f"outlier_rows={len(outliers)}")
    if not rows.empty:
        print(f"overall_median_absolute_residual={rows['absolute_residual'].median():.9g}")
        print(f"overall_max_absolute_residual={rows['absolute_residual'].max():.9g}")
        print(f"diagnostic_figures={len(list(FIG_DIR.glob('*.svg')))}")


if __name__ == "__main__":
    main()
