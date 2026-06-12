# Numerical Verification Report

Date: 2026-06-12

## Scope

This report verifies the major quantitative claims in the Phase 7 manuscript rewrite against machine-readable repository outputs and restart reports. It does not modify validated model code, raw simulation outputs, or primary ensembles.

## Verified Phase 7 Values

### Baseline Reference Cases

Source: `results/phase02/Figure2_representative_summary.csv`.

| Condition | SMI | Gamma_h_to_d | Gamma_h_to_s | A_h (mV) |
|---|---:|---:|---:|---:|
| low | 0.008812157901719679 | 0.9839703151549639 | 0.35665667443127486 | 1.8234865679095102 |
| intermediate | 0.1147416393453083 | 0.7512821308690512 | 0.27267058580960674 | 2.355775379339703 |
| high | 1.3218236852579517 | 0.10213244622161508 | 0.037555947626859855 | 15.067988039710302 |

All nine reference target rows are classified as exact target-case validation in `results/phase02/caption_discrepancy_table.csv`.

### Analytic Divider And Residuals

Sources: `manuscript/revision_restart/PHASE1_RESIDUAL_ANALYSIS_REPORT.md`, `results/revision_restart/phase1/phase1_divider_residual_rows.csv`, and `results/revision_restart/phase1/phase1_baseline_target_residuals.csv`.

- Total residual rows: `3718`.
- Non-exploratory residual rows: `3584`.
- Median absolute residual: `0.054751694`.
- Mean absolute residual: `0.073401014`.
- RMSE: `0.103138355`.
- Maximum absolute residual: `0.492427929`.
- Residual sign counts: `3680` negative and `38` positive.
- Baseline low residual: `-0.0072945027`.
- Baseline intermediate residual: `-0.1457867187`.
- Baseline high residual: `-0.3285634789`.

### Descriptor-Family Comparisons

Source: `manuscript/revision_restart/PHASE2_DESCRIPTOR_VALUE_ANALYSIS_REPORT.md` and Phase 2 CSV outputs.

- For non-exploratory local transfer, the analytic divider direct scalar CV RMSE was `0.051987`, raw SMI CV RMSE was `0.091467`, and the log component-pair CV RMSE was `0.071815`.
- For divider residuals, `dynamic_SMI_abs` had absolute Spearman association `0.853168`; `R_neck` was about `0.765`; raw SMI was about `0.704`.
- For head amplitude, synaptic conductance scale had absolute Spearman association `0.982396`, while raw SMI was `0.142920`.
- For somatic transfer, transfer gain was `0.635330`, transfer impedance was `0.602448`, and SMI was `0.552575`.
- Attached-versus-omitted one-port reconstruction analyzed `3702` rows, with median relative difference `-1.528e-6` and `0/3702` class changes.

### Deterministic Uncertainty Scope

Sources: `manuscript/revision_restart/PHASE3_HIGH_SMI_COVERAGE_REPORT.md`, `results/revision_restart/phase3/phase3_high_smi_coverage_audit.csv`, and `results/phase05_1/radius_uncertainty_by_n.csv`.

- N=768 SMI classes: `757` low, `11` intermediate, `0` high.
- N=768 maximum SMI: `0.316648`.
- Radius-error class flips at N=768: `184/768`, reported as a deterministic design fraction of `24.0%`.
- No Wilson or population confidence interval is used in the Phase 7 manuscript wording.

### Computational Credibility Checks

Sources: `results/revision_restart/phase4/phase4_independent_matrix_benchmark.csv`, `phase4_dc_analytic_benchmark.csv`, `phase4_be_cn_peak_comparison.csv`, and `phase4_validation_summary.csv`.

- Independent matrix benchmark rows: `3`.
- Maximum all-trace absolute voltage difference: `1.249000902703301e-13` mV.
- Maximum head-amplitude difference: `1.4210854715202004e-14` mV.
- Maximum local-transfer difference: `7.549516567451064e-15`.
- DC two-node `R_in,d` closed-form value: `144.48669201520912` MOhm.
- Direct DC solve value: `144.48669201520914` MOhm.
- BE-vs-CN maximum peak differences: `0.0020271018306221578` mV for `A_h`, `0.000533646319702985` mV for `A_d`, `0.00018858397472787392` mV for `A_s`, `0.0004997756786381258` for `Gamma_h_to_d`, and `0.00017959782401766322` for `Gamma_h_to_s`.
- NEURON status: unavailable; no NEURON validation is claimed.

### Reviewer And Release Packages

Sources: `manuscript/revision_restart/PHASE5_PACKAGE_CONTENT_AUDIT.md` and `PHASE5_PACKAGE_MANIFEST_SUMMARY.md`.

- Blinded reviewer draft: `275` files, SHA-256 `efaca101ecbd3df262f502f5c24e3b55012cbbf70c06c09d351226eefeaa428c`.
- Unblinded internal release candidate: `279` files, SHA-256 `42caa289d4d7e45838a67b2de0b9b1f679ea2a8aeec49695a04967bd57cdeaf0`.
- Final public release metadata is verified: repository https://github.com/blakepi/spine-divider-residuals, release https://github.com/blakepi/spine-divider-residuals/releases/tag/v1.0.0-submission, and version DOI https://doi.org/10.5281/zenodo.20672333.

## Rounding Policy

The manuscript rounds values for readability and preserves exact values in CSV files and ledgers. Percentages from deterministic sensitivity designs are described as design fractions, not prevalence estimates. Resampling summaries over designed rows are not described as biological confidence intervals.

## Pending Or Out-Of-Scope Items

- NEURON validation was not performed.
- Zenodo version DOI is verified as https://doi.org/10.5281/zenodo.20672333; concept DOI is https://doi.org/10.5281/zenodo.20672356.
- Full LaTeX compilation depends on local TeX availability; final submission cleanup records build output and static validation in `submission/final/FINAL_SUBMISSION_QA_REPORT.md`.
