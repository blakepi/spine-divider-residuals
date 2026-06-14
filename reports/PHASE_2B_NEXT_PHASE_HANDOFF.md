# Phase 2b Next Phase Handoff

## Current State

Phase 2b is complete and stops here.

Final recommendation: `PROCEED_TO_CONTROLLED_MANUSCRIPT_ADDON`.

Recommended next phase: `Phase 3 - Controlled Summary-Level Manuscript Add-On Integration`.

## Allowed Phase 3 Work

- Edit manuscript source to add a compact Results/Methods/Discussion add-on.
- Integrate one external empirical candidate figure or candidate table if approved.
- Update manuscript ledgers and manifests.
- Maintain all summary-only caveats.
- Run static language audits, LaTeX validation, and the existing test suite.

## Forbidden Phase 3 Work

- Per-spine claims.
- Broad empirical-validation reframing.
- New literature acquisition.
- Manual digitization.
- Public release, DOI, preprint, or submission actions.
- Claims that Kwon or Cornejo are plotted numeric `rho_L` rows.
- External residual claims from proxy transfer metrics.

## Authoritative Phase 2b Files

- `results/external_empirical/phase2b_load_sensitivity/phase2b_decision_result.json`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_load_model_calculations.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_class_threshold_loads.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_uncertainty_envelopes.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_separation_robustness_summary.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_transfer_proxy_interpretation.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_allowed_claims.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_candidate_claim_ledger_rows.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_candidate_table_rows.csv`
- `figures/external_empirical/phase2b_load_sensitivity/phase2b_summary_load_sensitivity.svg`
- `figures/external_empirical/phase2b_load_sensitivity/phase2b_summary_load_sensitivity.png`
- `figures/external_empirical/phase2b_load_sensitivity/phase2b_summary_load_sensitivity.pdf`

## Key Numeric Carry-Forward

- Harnett source-native `rho_L = 4`, `Gamma_div = 0.2`, high.
- Popovic measured source-native `rho_L = 0.0981818182`, `Gamma_div = 0.910596026`, low.
- Popovic model-fit source-native `rho_L = 0.0718085106`, `Gamma_div = 0.933002481`, low.
- Under fixed/recovered common loads, Harnett is high, Popovic measured is low, and Popovic model-fit is low or intermediate.
- Diagnostic grid preserves ordered separation but moves Harnett just into intermediate at 666.667 MOhm.
- Popovic measured uncertainty envelope remains low: `rho_L = 0.06953642384` to `0.1330645161`.
- All transfer rows have `residual_allowed = false`.

## Required Phase 3 Caveat

This analysis uses summary-level anchors only: it is not a per-spine reanalysis, Harnett is a model/summary anchor rather than recovered paired measured per-spine data, Kwon and Cornejo remain context/exclusion rows, and transfer proxies are not SPINE residuals.

## Stop Condition

Do not begin Phase 3 automatically. Phase 3 must be a separate controlled manuscript-integration phase.
