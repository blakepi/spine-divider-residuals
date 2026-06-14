# Phase 2a Summary Route 1 Decision-Gate Overlay

## Executive Verdict

Phase 2a classification: `SUMMARY_SIGNAL_FOR_REFRAMING_HYPOTHESIS`.

The Phase 1 summary anchors support a cautious Route 1 decision-gate overlay: Harnett remains in a high `rho_L` regime, while Popovic measured and model-fit anchors remain low or intermediate across all four Phase 2a load models. This is useful for hypothesis reframing, but it is not per-spine empirical validation, not biological validation of SPINE, and not a resolution of the literature controversy.

Recommended manuscript shape: `Shape_A_plus_reframing_hypothesis_only`.

Recommended next phase: `Phase 2b - Bounded Summary-Level Load-Sensitivity and Manuscript Add-On Draft`.

## Scope

Phase 2a used only locked Phase 0.1 and Phase 1 outputs. It did not acquire new sources, digitize figures, add per-spine rows, run a full load-sensitivity sweep, modify manuscript equations, alter model code/configs, update submission packages, or touch public release records.

Primary inputs:

- `results/external_empirical/phase0_1_feasibility/go_no_go_decision.json`
- `data/external_empirical/external_summary_measurements.csv`
- `results/external_empirical/phase1_summary_dataset/phase1_dataset_summary.json`
- `data/external_empirical/schema/external_summary_measurements_schema.json`
- Targeted SMI/divider interpretation from `spec/MASTER_BUILD_SPECIFICATION.md` and `spec/SPINE_MANUSCRIPT.tex`

## Gate Confirmation

The governing Phase 0.1 classification is `GO_SUMMARY_ONLY`.

The locked Phase 1 dataset contains 7 rows:

- 3 usable summary Route 1 rows.
- 4 excluded or context-only rows.
- 0 per-spine rows.

The three usable summary rows are:

- `harnett_2012_summary_model_anchor`
- `popovic_2015_measured_summary_anchor`
- `popovic_2015_model_fit_reference`

Every row has `usable_for_per_spine_route1 = false`.

## Source-Native Summary Calculations

Source-native feasibility calculations:

| row_id | rho_L | Gamma_div | class |
|---|---:|---:|---|
| `harnett_2012_summary_model_anchor` | 4 | 0.2 | `high_gte_0p75` |
| `popovic_2015_measured_summary_anchor` | 0.09818181818 | 0.9105960265 | `low_lt_0p25` |
| `popovic_2015_model_fit_reference` | 0.07180851064 | 0.9330024814 | `low_lt_0p25` |

These calculations use `rho_L = R_neck / load` and `Gamma_div = 1 / (1 + rho_L)`. They are summary-level feasibility calculations only.

## Load Models

Phase 2a applied four load models:

- `source_native`: each row's locked Phase 1 load.
- `common_SPINE_baseline_144p487`: fixed common load 144.487 MOhm.
- `common_Harnett_model_125`: fixed common load 125 MOhm.
- `common_Popovic_measured_275`: fixed common load 275 MOhm.

This is a decision-gate overlay, not the full Phase 2b sweep.

## Separation Result

Separation was preserved under all four load models.

| load_model_id | Harnett class | Popovic measured class | Popovic model class | Harnett/Popovic measured rho ratio | Harnett/Popovic model rho ratio |
|---|---|---|---|---:|---:|
| `source_native` | high | low | low | 40.74074074 | 55.7037037 |
| `common_SPINE_baseline_144p487` | high | low | intermediate | 18.51851852 | 12.34567901 |
| `common_Harnett_model_125` | high | low | intermediate | 18.51851852 | 12.34567901 |
| `common_Popovic_measured_275` | high | low | low | 18.51851852 | 12.34567901 |

The minimum Harnett-to-Popovic measured ratio is 18.51851852. The minimum Harnett-to-Popovic model-fit ratio is 12.34567901.

## Transfer Metric Compatibility

Transfer metrics were audited but not used as SPINE residuals.

- Harnett amplification range is incompatible or ambiguous for exact `Gamma_div` residuals.
- Popovic measured AR gives a proxy transfer value of 0.9090909091, compared with source-native `Gamma_div = 0.910596026`; the proxy difference is -0.001505116909.
- Popovic model-fit AR expression gives a proxy transfer value of 0.93, compared with source-native `Gamma_div = 0.933002481`; the proxy difference is -0.003002481.
- Kwon and Cornejo remain nonnumeric for rho_L.
- Zecevic remains qualitative interpretive context only.

All rows have `residual_allowed = false`.

## Figure Output

Created:

- `figures/external_empirical/phase2a_decision_gate/phase2a_summary_route1_decision_gate.svg`
- `figures/external_empirical/phase2a_decision_gate/phase2a_summary_route1_decision_gate.png`
- `figures/external_empirical/phase2a_decision_gate/phase2a_summary_route1_decision_gate.pdf`

Panel A plots the analytic divider curve with the three source-native summary anchors. Panel B shows the low/intermediate/high `rho_L` class grid across the four Phase 2a load models. The figure supports only the summary-level claim that the locked anchors separate into high versus low/intermediate load-normalized regimes.

## Outputs Created

- `scripts/external_empirical/phase2a_decision_gate_overlay.py`
- `results/external_empirical/phase2a_decision_gate/phase2a_source_native_calculations.csv`
- `results/external_empirical/phase2a_decision_gate/phase2a_load_model_definitions.csv`
- `results/external_empirical/phase2a_decision_gate/phase2a_load_model_calculations.csv`
- `results/external_empirical/phase2a_decision_gate/phase2a_summary_anchor_separation.csv`
- `results/external_empirical/phase2a_decision_gate/phase2a_transfer_metric_compatibility_audit.csv`
- `results/external_empirical/phase2a_decision_gate/phase2a_summary_route1_decision_gate_figure_data.csv`
- `results/external_empirical/phase2a_decision_gate/phase2a_figure_manifest.csv`
- `results/external_empirical/phase2a_decision_gate/phase2a_decision_gate_result.json`
- `results/external_empirical/phase2a_decision_gate/phase2a_validation_summary.csv`
- `results/external_empirical/phase2a_decision_gate/phase2a_validation_summary.json`

## Validation

Commands run:

```powershell
python scripts\external_empirical\phase2a_decision_gate_overlay.py --build
python scripts\external_empirical\phase2a_decision_gate_overlay.py --hash-after --compare-hashes --validate
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONPATH=(Resolve-Path -LiteralPath 'src').Path
python -m pytest -q -p no:cacheprovider
python scripts\external_empirical\phase2a_decision_gate_overlay.py --hash-after --compare-hashes --validate
```

Results:

- Phase 2a validation passed.
- Existing pytest suite passed: 63 tests.
- Protected hash comparison checked 1,630 pre-existing protected files and found 0 changed/added/removed rows. The new Phase 2a figure directory is an allowed deliverable and is excluded from the protected pre-existing-artifact comparison.

## Claim Boundaries

Phase 2a does not support:

- Per-spine empirical validation.
- Population prevalence.
- Harnett native measured paired-row recovery.
- Biological validation of SPINE.
- Resolution of the Harnett/Popovic/Kwon/Cornejo controversy.
- Exact transient or nonlinear prediction.

Phase 2a supports only a summary-level reframing hypothesis: the locked external summary anchors are compatible with a load-normalized divider interpretation and justify a bounded Phase 2b summary-level sensitivity/manuscript-add-on phase.
