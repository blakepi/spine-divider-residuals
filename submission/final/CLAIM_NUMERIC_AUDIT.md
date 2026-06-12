# Claim Numeric Audit

Date: 2026-06-12

| Claim | Manuscript location | Source | Source value | Manuscript value | Status |
|---|---|---|---:|---:|---|
| Baseline low SMI | Results | results/phase02/Figure2_representative_summary.csv | 0.008812157901719679 | 0.00881 | pass |
| Baseline intermediate SMI | Results | results/phase02/Figure2_representative_summary.csv | 0.1147416393453083 | 0.115 | pass |
| Baseline high SMI | Results | results/phase02/Figure2_representative_summary.csv | 1.3218236852579517 | 1.32 | pass |
| Total residual rows | Abstract/Results | results/revision_restart/phase1/phase1_divider_residual_rows.csv | 3718 | 3718 | pass |
| Median absolute residual | Abstract/Results | PHASE1_RESIDUAL_ANALYSIS_REPORT.md | 0.054751694 | 0.0548 | pass |
| Maximum absolute residual | Abstract/Results | PHASE1_RESIDUAL_ANALYSIS_REPORT.md | 0.492427929 | 0.492 | pass |
| Residual sign counts | Results | PHASE1_RESIDUAL_ANALYSIS_REPORT.md | 3680 negative; 38 positive | usually negative | pass |
| Analytic divider CV RMSE | Results | PHASE2_DESCRIPTOR_VALUE_ANALYSIS_REPORT.md | 0.051987 | 0.052 | pass |
| Raw SMI CV RMSE | Results | PHASE2_DESCRIPTOR_VALUE_ANALYSIS_REPORT.md | 0.091467 | 0.091 | pass |
| Head amplitude conductance scale Spearman | Results | PHASE2_DESCRIPTOR_VALUE_ANALYSIS_REPORT.md | 0.982396 | 0.982 | pass |
| N=768 SMI classes | Results/Discussion | phase3_high_smi_coverage_audit.csv | 757 low; 11 intermediate; 0 high | zero high-SMI rows | pass |
| Radius class flips | Results/Discussion | results/phase05_1/radius_uncertainty_by_n.csv | 184/768 | 24.0% | pass |
| Independent matrix all-trace max diff | Abstract/Results | phase4_independent_matrix_benchmark.csv | 1.249000902703301e-13 mV | roundoff | pass |
| Independent matrix local-transfer max diff | Results | phase4_independent_matrix_benchmark.csv | 7.549516567451064e-15 | roundoff | pass |
| DC two-node R_in,d | Methods/Results | phase4_dc_analytic_benchmark.csv | 144.48669201520912 MOhm | 144.486692 MOhm | pass |
| BE-vs-CN A_h peak diff | Results | phase4_be_cn_peak_comparison.csv | 0.0020271018306221578 mV | 0.00203 mV | pass |
| NEURON status | Methods/Results | phase4_validation_summary.csv | unavailable | no NEURON result claimed | pass |

No scientific number was changed during final submission cleanup; values are rounded for readability in manuscript prose and exact values remain in source CSVs/reports.
