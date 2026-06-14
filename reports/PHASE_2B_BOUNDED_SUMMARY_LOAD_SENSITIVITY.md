# Phase 2b Bounded Summary Load Sensitivity

## 1. Executive Verdict

Phase 2b final recommendation: `PROCEED_TO_CONTROLLED_MANUSCRIPT_ADDON`.

The Phase 2a summary-level signal survives the bounded, transparent sensitivity checks well enough to prepare a controlled manuscript add-on in a later phase. The supported scope remains narrow: summary-level load-normalization hypothesis only. The analysis does not support per-spine inference, biological-validation claims, prevalence estimates, or field-resolution claims.

Recommended next phase: `Phase 3 - Controlled Summary-Level Manuscript Add-On Integration`.

## 2. Phase 2a Decision Carried Forward

Phase 2a classification was `SUMMARY_SIGNAL_FOR_REFRAMING_HYPOTHESIS`, with recommended manuscript shape `Shape_A_plus_reframing_hypothesis_only`. Phase 2b carried this forward without changing manuscript source.

## 3. Summary-Only Constraint

Phase 0.1 remains `GO_SUMMARY_ONLY`. Phase 1 contains 7 rows, exactly 3 summary-usable rows, and 0 per-spine rows. Every row has `usable_for_per_spine_route1 = false`. Kwon and Cornejo remain context/exclusion rows without accepted numeric `rho_L` coordinates.

## 4. Inputs And Usable Rows

Usable summary Route 1 rows:

- `harnett_2012_summary_model_anchor`
- `popovic_2015_measured_summary_anchor`
- `popovic_2015_model_fit_reference`

Primary input files:

- `data/external_empirical/external_summary_measurements.csv`
- `results/external_empirical/phase2a_decision_gate/phase2a_decision_gate_result.json`
- `results/external_empirical/phase2a_decision_gate/phase2a_transfer_metric_compatibility_audit.csv`

## 5. Load Models Used

Phase 2b preserved Phase 2a load models and added bounded extensions:

- `source_native`
- `common_SPINE_baseline_144p487`
- `common_Harnett_model_125`
- `common_Popovic_measured_275`
- `common_Popovic_model_fit_564`
- deterministic diagnostic grid: 75, 100, 108, 125, 144.487, 162, 200, 275, 400, 564, and 666.667 MOhm.

The diagnostic grid is not a biological distribution.

## 6. Source-Native And Common-Load Calculations

Source-native anchors:

| row_id | rho_L | Gamma_div | class |
|---|---:|---:|---|
| `harnett_2012_summary_model_anchor` | 4 | 0.2 | high |
| `popovic_2015_measured_summary_anchor` | 0.0981818182 | 0.910596026 | low |
| `popovic_2015_model_fit_reference` | 0.0718085106 | 0.933002481 | low |

Under fixed/recovered common loads, Harnett remains high, Popovic measured remains low, and Popovic model-fit remains low or intermediate. Under the diagnostic grid, ordered class separation remains preserved, but the 666.667 MOhm threshold probe moves Harnett just into intermediate by the strict threshold rule.

For any common-load model applied to both Harnett and Popovic, the `rho_L` ratio equals the `R_neck` ratio. This means common-load separation mainly tests class-boundary stability, not a new empirical statistic.

## 7. Analytic Class-Threshold Load Analysis

Threshold loads:

| row_id | high if load <= | intermediate if load > | intermediate if load <= | low if load > |
|---|---:|---:|---:|---:|
| `harnett_2012_summary_model_anchor` | 666.6666667 | 666.6666667 | 2000 | 2000 |
| `popovic_2015_measured_summary_anchor` | 36 | 36 | 108 | 108 |
| `popovic_2015_model_fit_reference` | 54 | 54 | 162 | 162 |

Interpretation:

- Harnett remains high through recovered/common loads up to 564 MOhm; 666.667 MOhm is a diagnostic boundary probe.
- Popovic measured would require load <= 36 MOhm to enter high, outside the bounded recovered/common-load set used here.
- Popovic model-fit would require load <= 54 MOhm to enter high, outside the bounded recovered/common-load set used here.

## 8. Source-Reported Uncertainty Envelopes

Only the Popovic measured summary row has numeric source-reported uncertainty for both `R_neck` and load in the locked Phase 1 dataset.

Popovic measured deterministic envelope:

- `R_neck = 27 +/- 6 MOhm`
- `load = 275 +/- 27 MOhm`
- `rho_min = 0.06953642384`
- `rho_max = 0.1330645161`
- `Gamma_div_min = 0.8825622776`
- `Gamma_div_max = 0.9349845201`
- classes touched: `low_lt_0p25`

No uncertainty was invented for Harnett or the Popovic model-fit row.

## 9. Separation Robustness Summary

Separation summary:

| family | Harnett class set | Popovic measured class set | Popovic model-fit class set | Harnett/Popovic measured ratio | Harnett/Popovic model ratio |
|---|---|---|---|---:|---:|
| source native | high | low | low | 40.74074074 | 55.7037037 |
| fixed/recovered common | high | low | low; intermediate | 18.51851852 | 12.34567901 |
| diagnostic grid | intermediate; high | low; intermediate | low; intermediate | 18.51851851 to 18.51851852 | 12.34567901 |

Class separation is preserved for all tested values under the ordinal rule that Harnett stays in a higher class than both Popovic anchors. Harnett is always high under fixed/recovered common loads; the diagnostic grid intentionally includes a boundary probe.

## 10. Transfer-Proxy Interpretation

No SPINE residuals were computed.

Popovic measured and model-fit AR rows remain proxy-only compatibility checks:

- Popovic measured: proxy `0.9090909091`, source-native `Gamma_div = 0.910596026`, proxy minus Gamma `-0.0015051169`.
- Popovic model-fit: proxy `0.93`, source-native `Gamma_div = 0.933002481`, proxy minus Gamma `-0.003002481`.

All rows have `residual_allowed = false`.

## 11. What The Sensitivity Analysis Supports

Supported scope:

- Machine-recoverable summary-level anchors occupy distinct load-normalized regimes.
- Harnett model/summary anchor remains high under fixed/recovered common loads.
- Popovic measured summary remains low under fixed/recovered common loads and low under its source-reported uncertainty envelope.
- Popovic model-fit remains low or intermediate and never high under the bounded calculations.
- The result supports a load-normalization hypothesis for part of the apparent high- versus low-isolation contrast.

## 12. What It Does Not Support

The analysis does not support:

- Per-spine empirical inference.
- Claims that Harnett native paired measured rows were recovered.
- Biological-validation claims.
- Biological prevalence estimates.
- Field-resolution claims.
- Exact external residual analysis.
- Plotting Kwon or Cornejo as `rho_L` data.

## 13. Recommended Manuscript Integration Scope

Proceed only to a controlled summary-level manuscript add-on. The add-on may include one compact candidate figure or table, a short Results paragraph, a brief Methods note, and explicit limitation language. It must retain all summary-only caveats.

## 14. Files Created

- `scripts/external_empirical/phase2b_bounded_load_sensitivity.py`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_input_gate_validation.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_load_model_definitions.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_load_model_calculations.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_class_threshold_loads.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_uncertainty_envelopes.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_separation_robustness_summary.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_transfer_proxy_interpretation.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_allowed_claims.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_candidate_claim_ledger_rows.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_candidate_table_rows.csv`
- `results/external_empirical/phase2b_load_sensitivity/phase2b_decision_result.json`
- `figures/external_empirical/phase2b_load_sensitivity/phase2b_summary_load_sensitivity.svg`
- `figures/external_empirical/phase2b_load_sensitivity/phase2b_summary_load_sensitivity.png`
- `figures/external_empirical/phase2b_load_sensitivity/phase2b_summary_load_sensitivity.pdf`

## 15. Validation Commands And Results

Commands:

```powershell
python scripts\external_empirical\phase2b_bounded_load_sensitivity.py --build
python scripts\external_empirical\phase2b_bounded_load_sensitivity.py --hash-after --compare-hashes --validate
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONPATH=(Resolve-Path -LiteralPath 'src').Path; python -m pytest -q -p no:cacheprovider
python scripts\external_empirical\phase2b_bounded_load_sensitivity.py --hash-after --compare-hashes --validate
```

Final result: Phase 2b validation passed and the existing pytest suite passed with 63 tests. The final validation JSON is `results/external_empirical/phase2b_load_sensitivity/phase2b_validation_summary.json`.

## 16. Protected Hash Comparison

Protected baseline hash count: 1,630 files.

Final result: 0 changed protected files. Protected hash outputs are:

- `results/external_empirical/phase2b_load_sensitivity/protected_hashes_before.csv`
- `results/external_empirical/phase2b_load_sensitivity/protected_hashes_after.csv`
- `results/external_empirical/phase2b_load_sensitivity/protected_hash_comparison.csv`

## 17. Git / Root Status

The workspace root is not a Git repository, so no commit was possible. The nested public-release mirror must not be used as the working root.

## 18. Checkpoint Path And SHA-256

Checkpoint path:

`checkpoints/SPINE_phase_2b_bounded_summary_load_sensitivity_checkpoint_20260613_173330.zip`

The archive SHA-256 is written in the adjacent `.sha256` sidecar after archive creation, because the report itself is included in the checkpoint.
