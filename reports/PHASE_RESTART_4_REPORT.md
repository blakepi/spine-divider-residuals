# Phase Restart 4 Report

## Phase

Revision Restart Phase 4: external/independent validation and computational
credibility.

## Work Completed

- Read `AGENTS.md`, project state, decision log, required Restart Phase 0-3
  artifacts, passive implementation files, manuscript-faithful and related
  configs, Phase 02 baseline source data, and Restart Phase 1-2 derived
  source tables.
- Checked NEURON availability in the bundled Python runtime.
- Created `scripts/revision_restart/phase4_independent_matrix_benchmark.py`.
- Created `scripts/revision_restart/phase4_validation_runner.py`.
- Generated Phase 4 derived outputs under
  `results/revision_restart/phase4/`.
- Generated one diagnostic-only trace overlay SVG.
- Created Phase 4 manuscript-facing validation reports under
  `manuscript/revision_restart/`.
- Updated project state and decision log.

## NEURON Availability

NEURON was unavailable:

```text
importlib.util.find_spec('neuron') returned None
```

No NEURON validation result is claimed. NEURON remains an optional validation
dependency only, not a SPINE runtime dependency.

## Independent Matrix Benchmark

Output:

- `results/revision_restart/phase4/phase4_independent_matrix_benchmark.csv`

The independent benchmark parsed the manuscript-faithful TOML and reimplemented
the passive three-compartment matrix, double-exponential synapse, Backward
Euler update, and metrics without importing the production passive solver or
matrix assembly.

Results:

- Rows: 3 baseline reference cases.
- Maximum all-trace absolute voltage difference: `1.249000902703301e-13` mV.
- Maximum head-amplitude difference: `1.4210854715202e-14` mV.
- Maximum local-transfer difference: `7.54951656745106e-15`.

Interpretation: the independent direct matrix implementation reproduces the
existing SPINE baseline traces to numerical roundoff.

## DC Analytic Benchmark

Output:

- `results/revision_restart/phase4/phase4_dc_analytic_benchmark.csv`

Rows: 9.

Key results:

- Closed-form spine-omitted `R_in,d`: `144.48669201520912` MOhm.
- Direct two-node solve `R_in,d`: `144.48669201520914` MOhm.
- Difference: `2.980232238769531e-14` MOhm.
- DC divider predictions:
  - low: `0.9912648179022261`;
  - intermediate: `0.8970688495921831`;
  - high: `0.4306959250822274`.
- High-coupling limit with `SMI=1e-09`: `0.9999999989999999`.
- Very large-neck limit with `SMI=1e+09`: `9.99999999e-10`.
- Attached one-port relative `R_in,d` difference: about `-6.6726e-07`.

Interpretation: the DC divider/load algebra and limiting cases close as
expected. These checks validate algebraic limits, not transient peak response.

## BE-vs-CN Peak Comparison

Output:

- `results/revision_restart/phase4/phase4_be_cn_peak_comparison.csv`

Rows: 3.

Maximum differences across low/intermediate/high:

- `A_h`: `0.0020271018306221578` mV.
- `A_d`: `0.000533646319702985` mV.
- `A_s`: `0.00018858397472787392` mV.
- `Gamma_h_to_d`: `0.0004997756786381258`.
- `Gamma_h_to_s`: `0.00017959782401766322`.
- Trace voltage: `0.11155834897932926` mV.

Interpretation: BE-vs-CN differences are small internal numerical
self-consistency checks, not independent external validation.

## Outputs Created

Scripts:

- `scripts/revision_restart/phase4_independent_matrix_benchmark.py`
- `scripts/revision_restart/phase4_validation_runner.py`

Derived outputs:

- `results/revision_restart/phase4/phase4_independent_matrix_benchmark.csv`
- `results/revision_restart/phase4/phase4_dc_analytic_benchmark.csv`
- `results/revision_restart/phase4/phase4_be_cn_peak_comparison.csv`
- `results/revision_restart/phase4/phase4_validation_summary.csv`
- `results/revision_restart/phase4/diagnostic_figures/phase4_independent_trace_overlay.svg`

Reports:

- `manuscript/revision_restart/PHASE4_VALIDATION_STRATEGY.md`
- `manuscript/revision_restart/PHASE4_VALIDATION_INTERPRETATION.md`
- `manuscript/revision_restart/PHASE4_MANUSCRIPT_INSERT_DRAFT.md`
- `manuscript/revision_restart/PHASE4_CLAIM_REASSESSMENT.md`
- `manuscript/revision_restart/PHASE4_NEXT_PHASE_HANDOFF.md`
- `reports/PHASE_RESTART_4_REPORT.md`

## Validation

Validation completed:

- Python compile check for Phase 4 scripts.
- Phase 4 validation runner execution.
- CSV parsing for generated Phase 4 outputs.
- Required artifact existence check.
- Protected-file hash comparison.
- Full unittest discovery with `PYTHONPATH=src`.
- Git status attempted.

Validation details:

- Required files missing: 0.
- `phase4_independent_matrix_benchmark.csv`: 3 rows, 65 columns.
- `phase4_dc_analytic_benchmark.csv`: 9 rows, 16 columns.
- `phase4_be_cn_peak_comparison.csv`: 3 rows, 35 columns.
- `phase4_validation_summary.csv`: 5 rows, 6 columns.
- Protected-file hash comparison: 162 checked, 0 changed or missing.
- Phase 4 text hygiene scan: 0 non-ASCII hits.
- Full unittest discovery: 63 tests passed in 3.370s.
- Git status: failed because the current directory is not recognized as a Git
  repository in this environment.

Boundary preserved:

- No validated model code changed.
- No raw result CSVs changed.
- No manuscript TeX source changed.
- No manuscript tables changed.
- No publication figures changed.
- No release, DOI, license, repository publication, preprint, or submission
  work started.

## Checkpoint

Created:

- `checkpoints/SPINE_restart_phase_4_checkpoint.zip`
- `checkpoints/SPINE_restart_phase_4_checkpoint.zip.sha256`

The SHA-256 digest is stored in the adjacent sidecar file and reported in the
Phase 4 final response.

## Next Recommended Phase

Restart Phase 5: reviewer-access/code-release readiness and reproducibility
package planning, only if explicitly requested.
