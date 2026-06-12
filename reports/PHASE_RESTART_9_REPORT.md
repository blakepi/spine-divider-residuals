# Revision Restart Phase 9 Report

## Purpose

Phase 9 synchronized the private reviewer-access packages with the current post-Phase-8 manuscript state and created a PI/coauthor review bundle.

## Files Created

- `scripts/revision_restart/phase9_sync_review_packages.py`
- `manuscript/revision_restart/PHASE9_PACKAGE_REBUILD_PLAN.md`
- `manuscript/revision_restart/PHASE9_IDENTIFIER_AND_PATH_AUDIT.md`
- `manuscript/revision_restart/PHASE9_PACKAGE_MANUSCRIPT_CONSISTENCY_AUDIT.md`
- `manuscript/revision_restart/PHASE9_ADMIN_METADATA_READINESS.md`
- `manuscript/revision_restart/PHASE9_OPTIONAL_FIGURE_POLISH_AUDIT.md`
- `manuscript/revision_restart/PHASE9_FINAL_PACKAGE_REPORT.md`
- `manuscript/revision_restart/PHASE9_NEXT_PHASE_HANDOFF.md`
- `results/revision_restart/phase9/*`
- `submission/pi_coauthor_review_package/*`
- `reports/PHASE_RESTART_9_REPORT.md`

## Packages Rebuilt

| Package | Files | Archive SHA-256 |
|---|---:|---|
| Blinded reviewer package | 424 | `c91dc922c5a786dafca433dea4f845a2b1a9c9ff6bc859c18c51a002083958bf` |
| Unblinded internal package | 478 | `74a9cebcdbd52d3989025f0d54feeb4e16efc6ef3ff20c843abf6504e5a254c3` |
| PI/coauthor package | 22 | `a0f5f2ce25bd41b9ab49fd830b18a08c248b147ece670ca1c32672b1df28ec3f` |

## Audit Outcome

- Blinded identifier/local-path audit: pass, 0 hits.
- Unblinded local-path audit: pass, 0 hits. Identifier hits are expected because it is unblinded.
- PI/coauthor local-path audit: pass, 0 hits. Identifier hits are expected because it includes unblinded PDFs.
- Package document risky-language audit: pass, 0 hits.
- Package-manuscript consistency audit: pass.
- Figure polish audit: pass for the Phase 8-targeted checks.

## Validation

Phase 9 package script compiled and ran. Manifests parsed. Archive checksums verified. Protected hash comparison found 304 unchanged paths, 0 changed, 0 missing, and 0 added. Blinded package unittest discovery ran 57 tests and passed. A fresh extraction of the blinded archive ran `phase4_validation_runner.py` successfully, with NEURON unavailable and maximum independent-matrix trace difference `1.2490009027e-13` mV. Full repository unittest discovery ran 63 tests and passed.

## Boundary

No validated model code, raw result CSVs, broad scientific analyses, public repository, DOI, license, preprint, or manuscript submission action was changed or performed.

## Verdict

Phase 8's package synchronization blocker is resolved for private package readiness. The project is ready for PI/coauthor review. Journal submission still requires human administrative metadata and release-route decisions.
