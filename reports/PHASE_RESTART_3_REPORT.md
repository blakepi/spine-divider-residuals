# Phase Restart 3 Report

## Phase

Revision Restart Phase 3: statistical reframing, sensitivity-language correction, and high-SMI coverage audit.

## Work Completed

- Verified Restart Phase 1 and Phase 2 artifacts existed.
- Created deterministic post-processing script `scripts/revision_restart/phase3_statistical_reframing.py`.
- Generated Phase 3 derived outputs under `results/revision_restart/phase3/`.
- Created manuscript-facing statistical-language audit and claim-reframing CSVs under `manuscript/revision_restart/`.
- Wrote Phase 3 narrative reports and handoff artifacts.
- Updated project state and decision log.

## Main Results

- Statistical language audit produced 712 rows, including high-priority CI, bootstrap, prevalence, class-flip, and best-predictor wording issues.
- Interval classification produced 50 rows:
  - 30 Wilson/binomial interval rows classified as inappropriate or misleading;
  - 14 bootstrap rows classified as stability intervals over designed rows;
  - deterministic percentile/fraction/CV summaries classified as descriptive design summaries.
- Descriptive sensitivity summaries produced 122 rows.
- Predictor-family summary produced 85 target/regime rows.
- Design-permutation checks produced 6 rows; all six selected observed associations exceeded random within-dataset label pairings in 1,000 deterministic permutations.
- High-SMI coverage audit produced 14 rows; the N=768 uncertainty ensemble contains 0 high-SMI rows.

## High-SMI Conclusion

No high-SMI diagnostic extension was run. Phase 3 recommends scope limitation only: the N=768 uncertainty ensemble supports sampled low/intermediate SMI sensitivity summaries, not high-SMI uncertainty claims. High-SMI examples remain supported by reference and designed challenge datasets.

## Validation

Validation completed:

- Python compile check for the Phase 3 script.
- Phase 3 script execution.
- CSV parsing for generated Phase 3 outputs:
  - interval classification: 50 rows;
  - descriptive sensitivity summaries: 122 rows;
  - predictor-family summary: 85 rows;
  - design-permutation checks: 6 rows;
  - high-SMI coverage audit: 14 rows;
  - claim-reframing table: 8 rows;
  - statistical-language audit: 712 rows.
- Required artifact existence check.
- Protected-file hash comparison: 157 checked, 0 changed, 0 missing.
- Full unittest discovery with `PYTHONPATH=src`: 63 tests passed.
- Git status attempted; failed because the current directory is not recognized
  as a Git repository in this environment.

## Boundary

Phase 3 did not modify validated model code, raw result CSVs, manuscript TeX source, manuscript tables, publication figures, release state, license state, DOI state, public repository state, preprint state, or submission state.

## Next Recommended Phase

Restart Phase 4: external/independent validation and computational credibility work.

## Checkpoint

Created:

- `checkpoints/SPINE_restart_phase_3_checkpoint.zip`
- `checkpoints/SPINE_restart_phase_3_checkpoint.zip.sha256`

The SHA-256 digest is stored in the adjacent sidecar file and reported in the
Phase 3 final response.
