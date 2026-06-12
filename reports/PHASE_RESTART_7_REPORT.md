# Restart Phase 7 Report

## Phase

Revision Restart Phase 7: manuscript rewrite around the analytic-divider and residual-domain thesis.

## Work Completed

- Rewrote manuscript title, abstract, Introduction, Methods, Results, Discussion, Conclusion, and Data/Code Availability.
- Rewrote supplement title and key supplement sections for equations, validation, uncertainty, exploratory scenarios, reproducibility commands, and limitations.
- Updated Tables 1-4.
- Updated `CLAIM_TO_SOURCE_LEDGER.csv`, `FIGURE_SOURCE_MANIFEST.csv`, `TABLE_SOURCE_MANIFEST.csv`, and `NUMERICAL_VERIFICATION_REPORT.md`.
- Created new Figure 3 divider/residual assets and Phase 7 figure-data snapshots.
- Created all required Phase 7 restart reports.

## Validation Summary

- Phase 7 script compile: passed.
- Phase 7 figure generation: passed; 3718 rows plotted.
- CSV parsing: passed for claim ledger, figure manifest, table manifest, and Phase 7 figure-data outputs.
- Protected hash comparison: 189 tracked model/config/result files; 0 changed, 0 missing, 0 added protected files outside Phase 7 outputs.
- Unit tests: 63 tests passed.
- LaTeX builds: `main_unblinded`, `main_blinded`, `target_journal`, and `supplement` all built successfully with direct `pdflatex`/`bibtex` passes.
- Static language audit: old statistical/naming/NEURON/clinical overclaim language removed from visible source; availability hits are pending/not-claimed caveats only.
- Blinding audit: 0 blinded identifier hits.

## Scientific Outcome

The manuscript no longer presents SMI as a universal predictor or standalone novelty. It now states the classical divider relation, quantifies residual departures, scopes descriptor utility by target, reports deterministic uncertainty limitations including zero high-SMI rows at N=768, and supports passive computational credibility through independent direct-matrix and analytic benchmarks without claiming NEURON validation.

## Boundary Check

No validated solver/model code was edited. No raw result CSVs were edited. No broad primary ensembles were rerun. Manuscript source and tables were edited intentionally under Phase 7 authorization.

## Checkpoint

Checkpoint created:

- `checkpoints/SPINE_restart_phase_7_checkpoint.zip`
- `checkpoints/SPINE_restart_phase_7_checkpoint.zip.sha256`
