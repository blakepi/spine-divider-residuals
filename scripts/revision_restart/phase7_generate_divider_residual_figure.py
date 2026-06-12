"""Generate the Phase 7 divider/residual manuscript figure.

This script is intentionally post-processing only. It reads the Restart
Phase 1 residual table, writes a Phase 7 figure-data snapshot, and exports
publication assets without modifying raw simulation outputs or solver code.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "results" / "revision_restart" / "phase1" / "phase1_divider_residual_rows.csv"
OUTDIR = ROOT / "results" / "revision_restart" / "phase7"
FIGDIR = ROOT / "manuscript" / "figures_publication"


def _dataset_group(dataset: str) -> str:
    if "baseline" in dataset:
        return "Baseline targets"
    if "matched" in dataset:
        return "Matched-load sweep"
    if "fixed" in dataset or "geometry" in dataset:
        return "Fixed-load sweep"
    if "phase03" in dataset or "morphology" in dataset:
        return "Passive morphology"
    if "phase04" in dataset or "active" in dataset:
        return "Active stress tests"
    if "uncertainty" in dataset or "phase05" in dataset:
        return "Uncertainty rows"
    if "phase06" in dataset:
        return "Exploratory rows"
    return "Other rows"


def _load_data() -> pd.DataFrame:
    df = pd.read_csv(SOURCE)
    needed = [
        "dataset",
        "condition",
        "SMI",
        "observed_Gamma_h_to_d",
        "Gamma_divider",
        "residual",
        "absolute_residual",
        "exploratory_only",
    ]
    df = df[needed].copy()
    for col in ["SMI", "observed_Gamma_h_to_d", "Gamma_divider", "residual", "absolute_residual"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["exploratory_only"] = df["exploratory_only"].astype(str).str.lower().eq("true")
    df = df.dropna(subset=["SMI", "observed_Gamma_h_to_d", "Gamma_divider", "residual"])
    df = df[df["SMI"] > 0].copy()
    df["plot_group"] = df["dataset"].map(_dataset_group)
    return df


def _write_snapshot(df: pd.DataFrame) -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    snapshot = OUTDIR / "phase7_divider_residual_figure_data.csv"
    df.to_csv(snapshot, index=False)

    summary = OUTDIR / "phase7_divider_residual_figure_summary.csv"
    rows = []
    for group, sub in df.groupby("plot_group", dropna=False):
        rows.append(
            {
                "plot_group": group,
                "rows": len(sub),
                "median_absolute_residual": sub["absolute_residual"].median(),
                "max_absolute_residual": sub["absolute_residual"].max(),
                "negative_residual_rows": int((sub["residual"] < 0).sum()),
                "positive_residual_rows": int((sub["residual"] > 0).sum()),
            }
        )
    with summary.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "plot_group",
                "rows",
                "median_absolute_residual",
                "max_absolute_residual",
                "negative_residual_rows",
                "positive_residual_rows",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def _make_figure(df: pd.DataFrame) -> None:
    FIGDIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.35), constrained_layout=True)
    ax0, ax1 = axes

    palette = {
        "Baseline targets": "#1f77b4",
        "Fixed-load sweep": "#4c78a8",
        "Matched-load sweep": "#f58518",
        "Passive morphology": "#54a24b",
        "Active stress tests": "#b279a2",
        "Uncertainty rows": "#8c8c8c",
        "Exploratory rows": "#bab0ab",
        "Other rows": "#666666",
    }
    order = [
        "Fixed-load sweep",
        "Matched-load sweep",
        "Passive morphology",
        "Active stress tests",
        "Uncertainty rows",
        "Exploratory rows",
        "Baseline targets",
    ]

    for group in order:
        sub = df[df["plot_group"] == group]
        if sub.empty:
            continue
        alpha = 0.32 if group != "Baseline targets" else 0.95
        size = 13 if group != "Baseline targets" else 32
        zorder = 4 if group == "Baseline targets" else 2
        marker = "o" if group != "Baseline targets" else "D"
        ax0.scatter(
            sub["SMI"],
            sub["observed_Gamma_h_to_d"],
            s=size,
            alpha=alpha,
            color=palette[group],
            edgecolors="none",
            label=group,
            marker=marker,
            zorder=zorder,
        )
        ax1.scatter(
            sub["SMI"],
            sub["residual"],
            s=size,
            alpha=alpha,
            color=palette[group],
            edgecolors="none",
            marker=marker,
            zorder=zorder,
        )

    x_min = max(df["SMI"].min() * 0.75, 1e-4)
    x_max = df["SMI"].max() * 1.15
    xs = np.logspace(np.log10(x_min), np.log10(x_max), 500)
    ax0.plot(xs, 1.0 / (1.0 + xs), color="#111111", lw=1.8, label=r"$1/(1+\mathrm{SMI})$")
    ax1.axhline(0.0, color="#111111", lw=1.2)

    for ax in axes:
        ax.set_xscale("log")
        ax.set_xlim(x_min, x_max)
        ax.grid(True, which="major", color="#dddddd", lw=0.65)
        ax.grid(True, which="minor", color="#eeeeee", lw=0.35, alpha=0.65)
        ax.tick_params(labelsize=8)
        ax.set_xlabel("SMI = Rneck/Rin,d", fontsize=9)

    ax0.set_ylim(-0.03, 1.05)
    ax0.set_ylabel("Observed peak local transfer", fontsize=9)
    ax0.set_title("A  Divider expectation", loc="left", fontsize=10, weight="bold")
    ax1.set_ylim(-0.54, 0.08)
    ax1.set_ylabel("Residual: observed - divider", fontsize=9)
    ax1.set_title("B  Residual domain", loc="left", fontsize=10, weight="bold")

    # Keep the legend compact enough for journal-width placement.
    handles, labels = ax0.get_legend_handles_labels()
    ax0.legend(handles, labels, loc="lower left", fontsize=6.5, frameon=True, framealpha=0.9)

    for ext in ("pdf", "svg", "png"):
        fig.savefig(FIGDIR / f"Fig3_divider_residuals.{ext}", dpi=300)
    plt.close(fig)


def main() -> None:
    df = _load_data()
    _write_snapshot(df)
    _make_figure(df)
    print(f"Wrote Phase 7 divider/residual figure from {len(df)} rows.")


if __name__ == "__main__":
    main()
