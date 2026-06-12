# Manuscript Reproduction - Phase 02

Date: 2026-06-09

## Scope

This report reproduces the manuscript's passive proof-of-principle results using the `manuscript_faithful` configuration exactly as implemented in Phase 01/01.1. No parameters, metric windows, solver settings, or implementation details were tuned to improve agreement.

Configuration and numerical settings:

- config: `configs/manuscript_faithful/baseline.toml`
- solver: backward Euler
- `dt = 0.01 ms`
- `t0 = 20 ms`
- simulation stop: `80 ms`
- metric window: `50 ms` after `t0`
- `R_in,d` method: steady-state dendrite-soma load with stimulated spine omitted
- output source data: `results/phase02/`
- output figures: `figures/phase02/`

Because matplotlib is not available in the bundled runtime, Phase 02 writes editable SVG figures directly from source data. No raster figure export was generated in this environment.

## Figure 1 - Architecture

Output:

- figure: `figures/phase02/Figure1_architecture.svg`
- source: model specification and faithful configuration

Status: exact schematic reproduction of the implemented architecture. This is a scripted schematic, not a pixel reproduction of the manuscript image.

## Figure 2 - Representative Low, Intermediate, and High SMI Traces

Outputs:

- low trace source: `results/phase02/Figure2_low_trace.csv`
- intermediate trace source: `results/phase02/Figure2_intermediate_trace.csv`
- high trace source: `results/phase02/Figure2_high_trace.csv`
- summary: `results/phase02/Figure2_representative_summary.csv`
- figures:
  - `figures/phase02/Figure2_low_trace.svg`
  - `figures/phase02/Figure2_intermediate_trace.svg`
  - `figures/phase02/Figure2_high_trace.svg`

Representative reproduction:

| Condition | L_n (um) | r_n (um) | SMI reproduced | Gamma h-to-d | Gamma h-to-s | A_h (mV) | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| low | 0.25 | 0.25 | 0.008812 | 0.983970 | 0.356657 | 1.823487 | exact reproduction |
| intermediate | 0.75 | 0.12 | 0.114742 | 0.751282 | 0.272671 | 2.355775 | exact reproduction |
| high | 1.50 | 0.05 | 1.321824 | 0.102132 | 0.037556 | 15.067988 | exact reproduction |

Caption discrepancy table:

- `results/phase02/caption_discrepancy_table.csv`

All nine reported caption values for SMI, `Gamma_h_to_d`, and `Gamma_h_to_s` are exact reproductions under the predefined classification rule.

## Figure 3 - Fixed-Load Geometry Sweep

Outputs:

- source: `results/phase02/Figure3_geometry_sweep.csv`
- figures:
  - `figures/phase02/Figure3A_Gamma_hs_heatmap.svg`
  - `figures/phase02/Figure3B_SMI_heatmap.svg`
  - `figures/phase02/Figure3C_SMI_vs_Gamma_hs.svg`
  - `figures/phase02/Figure3D_SMI_vs_Ah.svg`

Parameters:

- neck length: 0.10-2.00 um, 20 linear steps
- neck radius: 0.035-0.25 um, 20 linear steps
- dendrite-soma load held fixed
- `R_in,d = 144.486692 Mohm`

Sweep ranges:

| Quantity | Min | Max |
|---|---:|---:|
| R_neck (Mohm) | 0.509296 | 519.689610 |
| SMI | 0.003525 | 3.596799 |
| Gamma h-to-s | 0.015815 | 0.360137 |
| A_h (mV) | 1.806991 | 29.643585 |

Central finding:

- `Spearman(SMI, R_neck) = 1.0`
- `Spearman(SMI, Gamma_h_to_s) = -1.0`
- `Spearman(SMI, A_h) = 1.0`

Status: exact reproduction of the manuscript's qualitative fixed-load claims. Limiting/contradictory finding: at fixed load, SMI has exactly the same rank ordering as `R_neck`, so it adds no information beyond scaled neck resistance in this experiment.

## Figure 4 - Matched-Neck Heterogeneous-Load Validation

Outputs:

- source: `results/phase02/Figure4_matched_neck_heterogeneous_load.csv`
- figures:
  - `figures/phase02/Figure4A_Rneck_vs_Gamma_hs.svg`
  - `figures/phase02/Figure4B_SMI_vs_Gamma_hs.svg`
  - `figures/phase02/Figure4C_SMI_vs_Ah.svg`

Parameters:

- `R_neck = 100 Mohm`
- `g_L,d = 0.1-30 nS`, 30 log-spaced values
- `g_DS = 12 nS`
- all other values from `manuscript_faithful`

Sweep ranges:

| Quantity | Min | Max |
|---|---:|---:|
| R_neck (Mohm) | 100.000000 | 100.000000 |
| R_in,d (Mohm) | 29.051988 | 221.187427 |
| SMI | 0.452105 | 3.442105 |
| Gamma h-to-s | 0.028858 | 0.076982 |
| A_h (mV) | 8.943838 | 8.976751 |

Central finding:

- unique `R_neck` values: 1
- `Spearman(SMI, Gamma_h_to_s) = -1.0`

Status: exact reproduction of the matched-neck logic. Supporting finding: `R_neck` is constant and cannot rank outputs, while SMI varies with dendritic load and orders transfer in this implemented manipulation.

## Convergence Check

Output:

- `results/phase02/convergence_dt_intermediate.csv`
- `figures/phase02/convergence_dt_vs_Ah.svg`

Intermediate condition convergence against `dt = 0.0025 ms`:

| dt (ms) | A_h abs diff (mV) | Gamma h-to-d abs diff | Gamma h-to-s abs diff |
|---:|---:|---:|---:|
| 0.02 | 0.001442 | 0.000875 | 0.000315 |
| 0.01 | 0.000631 | 0.000375 | 0.000135 |
| 0.005 | 0.000213 | 0.000125 | 0.000045 |
| 0.0025 | 0.000000 | 0.000000 | 0.000000 |

The manuscript timestep discrepancy relative to the finest tested timestep is much smaller than caption-level reporting precision for the reproduced attenuation ratios.

## Exact, Approximate, and Failed Reproduction

Exact reproduction:

- Figure 2 caption values for SMI, `Gamma_h_to_d`, and `Gamma_h_to_s`.
- Figure 3 qualitative fixed-load trends and rank-order identity between SMI and `R_neck`.
- Figure 4 matched-neck logic that `R_neck` is constant while SMI varies with load.

Approximate reproduction:

- None identified for captioned quantitative targets under the predefined thresholds.

Failed reproduction:

- None identified for the reported passive caption values tested in Phase 02.

Scientific limitation:

- Fixed-load SMI does not outperform `R_neck`; it is mathematically the same ordering. This supports the manuscript's caution and constrains any stronger interpretation.
