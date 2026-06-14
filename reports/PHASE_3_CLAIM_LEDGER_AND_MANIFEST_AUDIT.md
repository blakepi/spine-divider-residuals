# Phase 3 Claim Ledger And Manifest Audit

## New Claim Ledger Rows

The following Phase 3 rows were added to `manuscript/CLAIM_TO_SOURCE_LEDGER.csv`:

- Summary-level external anchors occupy distinct `rho_L` regimes under source-native calculations.
- Harnett model/summary anchor remains high under fixed/recovered common loads.
- Popovic measured summary remains low under fixed/recovered common loads and its source-reported uncertainty envelope remains low.
- Popovic model-fit row remains low or intermediate and never high under bounded common-load calculations.
- External transfer ratios are proxy-only compatibility checks and not SPINE residuals.
- Per-spine empirical inference remains unsupported by the external summary dataset.
- Biological validation of SPINE remains unsupported by the external summary add-on.
- Full controversy resolution remains unsupported by the external summary add-on.

## Evidence Paths

- `reports/PHASE_2B_BOUNDED_SUMMARY_LOAD_SENSITIVITY.md`
- `reports/PHASE_2B_CLAIM_LANGUAGE_GUARDRAILS.md`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_load_model_calculations.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_separation_robustness_summary.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_uncertainty_envelopes.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_transfer_proxy_interpretation.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_decision_result.json`
- `data/external_empirical/external_summary_measurements.csv`

## Figure/Table Manifest Updates

`manuscript/FIGURE_SOURCE_MANIFEST.csv` includes Figure S10:

- Submission/publication asset: `manuscript/figures_publication/FigS10_external_summary_load_sensitivity.pdf`
- Original/source figure: `manuscript/supplement/figures/FigS10_external_summary_load_sensitivity.svg`
- Source data: Phase 2b load-model, threshold-load, and uncertainty-envelope CSVs
- Scripts: `scripts/external_empirical/phase2b_bounded_load_sensitivity.py`; `scripts/external_empirical/phase3_integrate_summary_manuscript_addon.py`

No table manifest update was needed because no table was integrated.

## Source-Data Traceability

The Phase 3 claim rows trace to Phase 2b derived CSV/JSON outputs, which trace to the locked Phase 1 summary dataset. No new source acquisition, manual transcription, or figure digitization was performed in Phase 3.

## Forbidden Claims Not Added

The ledger and manuscript do not add claims of per-spine empirical validation, biological validation, prevalence, controversy resolution, recovered native Harnett paired measured rows, or SPINE residuals from transfer proxies.

## Any Unsupported Candidate Claims Rejected

The following unsupported candidate claims were explicitly rejected in the integrated claim ledger:

- `phase2b_claim_06_per_spine_unsupported`
- `phase2b_claim_07_biological_validation_unsupported`
- `phase2b_claim_08_controversy_resolution_unsupported`
