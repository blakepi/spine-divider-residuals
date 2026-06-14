# Phase 2a Next Phase Handoff

## Current State

Phase 2a is complete and stops here.

Decision-gate classification: `SUMMARY_SIGNAL_FOR_REFRAMING_HYPOTHESIS`.

Recommended next phase: `Phase 2b - Bounded Summary-Level Load-Sensitivity and Manuscript Add-On Draft`.

## Key Results To Carry Forward

Source-native summary values:

| row_id | rho_L | Gamma_div | class |
|---|---:|---:|---|
| `harnett_2012_summary_model_anchor` | 4 | 0.2 | high |
| `popovic_2015_measured_summary_anchor` | 0.09818181818 | 0.9105960265 | low |
| `popovic_2015_model_fit_reference` | 0.07180851064 | 0.9330024814 | low |

Across all four Phase 2a load models:

- Harnett remains high.
- Popovic measured remains low.
- Popovic model fit remains low or intermediate.
- Minimum Harnett-to-Popovic measured `rho_L` ratio is 18.51851852.
- Minimum Harnett-to-Popovic model-fit `rho_L` ratio is 12.34567901.

Transfer audit:

- Popovic AR values were converted only to proxy transfer values.
- No exact SPINE residuals were computed or authorized.
- All transfer-audit rows have `residual_allowed = false`.

## Files For Phase 2b

Use these as the authoritative Phase 2a outputs:

- `results/external_empirical/phase2a_decision_gate/phase2a_source_native_calculations.csv`
- `results/external_empirical/phase2a_decision_gate/phase2a_load_model_definitions.csv`
- `results/external_empirical/phase2a_decision_gate/phase2a_load_model_calculations.csv`
- `results/external_empirical/phase2a_decision_gate/phase2a_summary_anchor_separation.csv`
- `results/external_empirical/phase2a_decision_gate/phase2a_transfer_metric_compatibility_audit.csv`
- `results/external_empirical/phase2a_decision_gate/phase2a_summary_route1_decision_gate_figure_data.csv`
- `results/external_empirical/phase2a_decision_gate/phase2a_decision_gate_result.json`
- `figures/external_empirical/phase2a_decision_gate/phase2a_summary_route1_decision_gate.svg`
- `figures/external_empirical/phase2a_decision_gate/phase2a_summary_route1_decision_gate.png`
- `figures/external_empirical/phase2a_decision_gate/phase2a_summary_route1_decision_gate.pdf`

## Phase 2b Boundaries

Phase 2b may:

- Run a bounded summary-level load/uncertainty sensitivity analysis.
- Keep Harnett, Popovic measured, and Popovic model-fit rows separate.
- Draft an optional manuscript add-on using conservative language.
- Reuse the Phase 2a figure only if the caption remains summary-only.

Phase 2b must not:

- Create per-spine rows.
- Treat Harnett as recovered native paired measured data.
- Treat Kwon or Cornejo as numeric `rho_L` rows without a new accepted acquisition phase.
- Compute or label transfer differences as SPINE residuals unless an exact compatible metric is established.
- Modify manuscript equations, validated model code, public release records, DOI metadata, or submission state without a separate explicit phase.

## Validation State

Phase 2a validation passed:

- `GO_SUMMARY_ONLY` gate confirmed.
- 7 Phase 1 rows confirmed.
- Exactly 3 summary-usable rows confirmed.
- No per-spine rows confirmed.
- 12 load-model calculation rows validated.
- Separation preserved under all 4 load models.
- Figure-data provenance validated.
- Protected hash comparison found 0 non-unchanged pre-existing protected files out of 1,630.
- Existing pytest suite passed: 63 tests.

## Handoff Decision

Proceed only to the bounded Phase 2b summary-level sensitivity/manuscript-add-on phase. Do not silently begin Phase 2b from this Phase 2a run.
