# Revision Restart Phase 8 Report

## Purpose

Phase 8 performed final pre-submission QA, hostile reviewer simulation, external-review response audit, static leakage audit, package consistency audit, and blocker classification for the rewritten analytic-divider/residual-domain manuscript.

## Files Created

- `manuscript/revision_restart/PHASE8_PDF_QA_REPORT.md`
- `manuscript/revision_restart/PHASE8_EXTERNAL_REVIEW_RESPONSE_AUDIT.md`
- `manuscript/revision_restart/PHASE8_HOSTILE_REVIEWER_SIMULATION.md`
- `manuscript/revision_restart/PHASE8_CLAIM_EVIDENCE_AUDIT.csv`
- `manuscript/revision_restart/PHASE8_STATIC_LANGUAGE_AND_LEAKAGE_AUDIT.md`
- `manuscript/revision_restart/PHASE8_REPRODUCIBILITY_PACKAGE_AUDIT.md`
- `manuscript/revision_restart/PHASE8_JOURNAL_STRATEGY_RECOMMENDATION.md`
- `manuscript/revision_restart/PHASE8_SUBMISSION_BLOCKER_LIST.md`
- `manuscript/revision_restart/PHASE8_MINOR_FIX_LOG.md`
- `manuscript/revision_restart/PHASE8_BUILD_AND_VALIDATION_REPORT.md`
- `manuscript/revision_restart/PHASE8_NEXT_PHASE_HANDOFF.md`
- `reports/PHASE_RESTART_8_REPORT.md`
- `scripts/revision_restart/phase8_final_qa_audit.py`
- QA outputs under `results/revision_restart/phase8/`

## Minor Fixes Made

Phase 8 made only minor production/surface fixes:

- Removed a visible correspondence placeholder from the title block.
- Removed visible internal R4 provenance text from Figure 1.
- Reworded Table 4 to avoid "SMI predicts" language.
- Reworded Figure 8 source-asset label from "prevalence" to "design fraction."
- Reworded and relaid out Figure S9 labels to remove "epileptogenesis" and overlapping scenario text.

No validated model code, raw result CSVs, broad analyses, public repository, DOI, license, or submission action was changed.

## QA Outcome

The manuscript thesis is internally consistent: the load-normalized ratio is presented as the coordinate for the classical local divider, and residuals are the domain-of-validity object. The manuscript no longer claims NEURON validation, biological prevalence, inferential confidence intervals, universal SMI prediction, or public release.

PDF text has no remaining hits for old internal phase tags, placeholders, local paths, NEURON-validation overclaim, "SMI predicts", "Spine Morphology Index", "best predictor", or "epileptogenesis."

## Reproducibility Package Outcome

The existing Phase 5 blinded and unblinded package archives match their SHA-256 sidecars and include Phase 1-4 restart evidence. They are not synchronized with the current Phase 7/8 manuscript, figure, ledger, and numerical-verification state. A package rebuild is a submission blocker.

## Journal Strategy

Primary target: Journal of Computational Neuroscience.

Backup target: Neuroinformatics.

## Blocker Verdict

Ready for PI/coauthor review: yes.

Ready for journal submission: no.

Submission blockers:

1. Rebuild/synchronize reviewer packages after Phase 8.
2. Supply final correspondence metadata.
3. Resolve public repository/archive/DOI/license route if required by the selected journal.

## Final Validation

Completed checks:

- Phase 8 audit script compiled.
- Phase 8 audit runner executed and regenerated QA summaries.
- Rebuilt PDFs parsed and rendered for visual/textual QA.
- Key CSVs parsed successfully.
- LaTeX logs had 0 undefined control sequences, 0 undefined references, 0 citation warnings, 0 overfull boxes, and 0 fatal errors.
- Package archives matched their SHA-256 sidecars.
- Protected model/config/result hash comparison found 189 unchanged paths, 0 changed paths, and 0 missing paths.
- Full unittest discovery ran 63 tests and passed.
- Required Phase 8 files existed before checkpoint creation.
- Git status was attempted but unavailable because this directory is not recognized as a Git repository in the current environment.

Checkpoint created: `checkpoints/SPINE_restart_phase_8_checkpoint.zip` with adjacent SHA-256 sidecar.
