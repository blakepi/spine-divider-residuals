# Phase Restart 2 Report

## Phase

Revision Restart Phase 2: ratio-versus-components and descriptor-value analysis.

## Work Completed

- Verified required Restart Phase 0 and Phase 1 artifacts were present.
- Created deterministic post-processing script `scripts/revision_restart/phase2_descriptor_value_analysis.py`.
- Generated Phase 2 derived tables under `results/revision_restart/phase2/`.
- Compared SMI, analytic divider, component resistances, log-component OLS, impedance/dynamic descriptors, and synaptic conductance scale across available targets.
- Computed a DC one-port spine-attached versus spine-omitted `R_in,d` reconstruction where possible.
- Generated diagnostic-only SVGs under `results/revision_restart/phase2/diagnostic_figures/`.
- Created Phase 2 manuscript-facing restart artifacts under `manuscript/revision_restart/`.

## Principal Findings

- For non-exploratory local transfer, raw SMI and `Gamma_divider` had identical absolute Spearman association (0.948576), but `Gamma_divider` had better scalar CV RMSE (0.051987) than raw SMI (0.091467).
- The log component pair improved over raw SMI for local-transfer CV RMSE (0.071815 vs 0.091467) but did not beat the analytic divider.
- Dynamic SMI was the strongest scalar where available for local transfer and residuals.
- Residuals were better explained by dynamic/component/conductance descriptors than by raw SMI alone.
- Head amplitude was dominated by synaptic conductance scale; SMI was weak for amplitude.
- Somatic transfer was better aligned with downstream transfer descriptors than with raw SMI alone.
- Attached-vs-omitted `R_in,d` differences were negligible in the DC reconstruction: median relative difference -1.528e-6 and 0/3,702 SMI class changes.

## Validation

Validation completed:

- Python compile check for the Phase 2 script.
- Phase 2 script execution.
- CSV parsing for generated Phase 2 outputs:
  - standardized descriptor table: 3,718 rows;
  - scalar correlations: 690 rows;
  - ratio-vs-components model comparison: 575 rows;
  - target-specific summary: 85 rows;
  - residual-predictor summary: 34 rows;
  - attached-vs-omitted `R_in,d`: 3,702 rows;
  - descriptor recommendation table: 85 rows;
  - source manifest: 153 rows.
- Required artifact existence check.
- Protected-file hash comparison: 157 checked, 0 changed, 0 missing.
- Full unittest discovery with `PYTHONPATH=src`: 63 tests passed.
- Git status attempted; failed because the current directory is not recognized
  as a Git repository in this environment.

Boundary preserved:

- No validated model code changed.
- No raw result CSVs changed.
- No manuscript TeX source changed.
- No manuscript tables changed.
- No publication figures changed.
- No release, DOI, license, repository publication, or submission work started.

## Checkpoint

Created:

- `checkpoints/SPINE_restart_phase_2_checkpoint.zip`
- `checkpoints/SPINE_restart_phase_2_checkpoint.zip.sha256`

The SHA-256 digest is stored in the adjacent sidecar file and reported in the
Phase 2 final response.

## Next Recommended Phase

Restart Phase 3: statistical reframing and descriptive-language repair, consuming the Phase 2 model-comparison outputs and static-language audit.
