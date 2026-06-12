# SPINE Project State

## Active phase

**Revision Restart Phase 9 - completed**

Active task:

Final package synchronization, admin metadata readiness, and PI/coauthor review package

## Verified repository state

Phase 01 manuscript-faithful passive core exists. The passive
three-compartment solver, double-exponential synapse, dendrite-soma input
resistance with the stimulated spine omitted, SMI, metrics, source-data export,
and CLI smoke path are implemented and tested.

Phase 01.1 audit cleanup is complete. Documentation, traceability, validation
guardrails, signed-current metric clarification, driving-force reduction
metrics, and unit-boundary clarification were updated without changing passive
solver equations or manuscript-faithful baseline values.

Phase 02 manuscript reproduction is complete. Manuscript-faithful
representative traces, fixed-load geometry sweep, SMI heatmap/scatters,
matched-neck heterogeneous-load validation, convergence checks, source-data
CSV files, SVG figures, discrepancy tables, and central SMI claim tests were
generated.

Phase 03 morphology and impedance work is complete. The repository now
contains a generalized passive morphology engine, lightweight sparse COO
matrix assembly, procedural cables and branch trees, an internal SWC parser,
arbitrary passive spine attachment, spatial convergence checks, advanced neck
models, frequency-domain impedance tools, sinusoidal and logarithmic-chirp
validation, an SMI challenge suite, alternative predictor comparison, source
data, SVG figures, and Phase 03 reports.

Phase 04 active/nonlinear work is complete. The repository now contains
opt-in active-extension configuration, AMPA and NMDA synapses with magnesium
block, Na/KDR/HCN/A-type/restrained-calcium conductances, a semi-implicit
active solver with exponential gate updates, explicit limiting-case solver
cross-checks, active validation tables, active SMI challenge experiments,
protocol-library outputs, exploratory frozen-gate operating-point impedance,
source data, SVG figures, and Phase 04 reports.

Phase 05 sensitivity/statistics work is complete. The repository now contains
normalized local sensitivity analysis, deterministic Latin-hypercube global
uncertainty sampling, explicit neck-radius uncertainty propagation,
uncertainty intervals, rank-correlation uncertainty screening, practical
identifiability examples, predictor comparison with bootstrap and
cross-validation, focused residual analysis, counterexample-prevalence
estimates, claim robustness classification, machine-readable source tables,
SVG figures, and Phase 05 reports.

Phase 05.1 robustness and convergence audit is complete. The repository now
contains progressive N=96/192/384/768 uncertainty convergence tables, SMI and
response-metric convergence curves, radius-only uncertainty propagation,
radius class-boundary examples, predictor-stability tables, counterexample
prevalence convergence, claim reassessment, machine-readable source tables,
SVG figures, and Phase 05.1 reports. No passive or active model implementation
behavior was changed.

Phase 06 exploratory epilepsy/epileptogenesis work is complete. The repository
now contains a separated `epilepsy_exploratory` configuration family, a
literature-grounded evidence table, predeclared hypotheses, restrained
scenario perturbations, isolated and clustered/synchronous/asynchronous active
protocols, deterministic uncertainty propagation, SMI/predictor comparisons,
mechanistic decomposition tables, SVG figures, and Phase 06 reports. No
validated manuscript-faithful, passive, active, Phase 05, or Phase 05.1 model
behavior was modified. Phase 06 makes no clinical, diagnostic, prognostic, or
therapeutic claims.

Phase 07 final release work is complete. The repository now contains final
audit, reproducibility, scientific synthesis, publication guide, figure index,
claim audit, future-work, README, install, quickstart, and changelog
documentation. Phase 07 updated traceability closure and release validation,
fixed a configuration metadata reporting defect for top-level Phase 06 TOML
tracks, and did not add biological mechanisms or alter validated scientific
solver behavior.

Phase 08 manuscript and repository-submission packaging is complete. The
repository now contains a journal-target assessment, final unblinded, blinded,
and JCNS-target LaTeX manuscript variants, a standalone supplement, curated
main and supplemental SVG figure sets, table and figure manifests, a
claim-to-source ledger, a numerical verification report, submission materials,
repository-release planning files, build wrappers, LaTeX validation notes,
Phase 08 reports, and final ZIP archives. Phase 08 did not add biological
mechanisms, publish code, select a license, create a public repository, submit
a preprint, or alter validated scientific code/results.

A post-Phase-08 LaTeX production/proof pass is complete. It replaced figure
placeholder boxes with direct `\includegraphics` PDF figure embeddings,
generated manuscript-local PDF figure fallbacks from the curated SVG files,
wrapped main tables to page width, tightened title-page formatting, updated
build wrappers, and added production/proof reports. This was not a new
scientific phase and did not alter validated scientific code, source data,
numerical results, references, or claims. Existing compiled PDFs in
`manuscript/` predate this production pass and should be rebuilt before
circulation or submission.

Revision Phase R0 editorial triage is complete. The repository now contains
`manuscript/revision_v2/` with the preserved editorial review source, issue
response matrix, R0-R8 action plan, terminology map, figure rebuild
requirements, statistics/methods gap list, literature queue, risk register, and
R0 summary report. R0 was planning/audit only: it did not revise manuscript
prose, alter scientific code, change result CSVs, rebuild figures, add
citations, select a license, create a public repository, or submit anything.
R0 explicitly records that the earlier manuscript was hypothetical/internal and
must not be framed as a prior published or external manuscript.

Revision Phase R1 provenance, novelty, and narrative reframing is complete.
The manuscript title, abstract, introduction, methods terminology, results
framing, discussion, conclusion, selected tables, selected supplement sections,
claim ledger wording, figure/table manifest notes, and numerical verification
report wording were revised to remove misleading prior-manuscript/reproduction
framing. The paper now presents SMI as an operational load-normalized
spine-neck descriptor grounded in classical cable-theory/load logic, with the
new contribution framed as reproducible domain-of-validity and falsification
analysis. R1 did not modify scientific code, model implementation, numerical
source data, result CSVs, figure assets, analyses, bibliography entries,
licenses, repository visibility, or submission state. R1 artifacts are in
`manuscript/revision_v2/`.

Revision Phase R2 literature and bibliography repair is complete. The
manuscript now includes the requested Magee 2000 dendritic integration and
Magee and Cook 2000 somatic EPSP/location-dependence references, verified
Magee 1998 and Magee 1999 HCN/Ih entries, added spine-neck amplification,
spine-neck geometry/plasticity, ModelDB, and FAIR-data references, and corrected
the erroneous `Major2008DendriticSpikes` record to the verified
`Jarsky2005DendriticSpikePropagation` metadata. R2 did not change scientific
code, validated model behavior, source-data CSVs, figures, statistical
precision, model equations, repository visibility, or license state. R2
artifacts are in `manuscript/revision_v2/` and `reports/PHASE_R2_REPORT.md`.

Revision Phase R5 manuscript compression and journal-article restructuring is
complete. The main manuscript has been reorganized into a compact journal-style
article with six Methods subsections, seven science-first Results subsections,
four Discussion subsections, eight retained main figures, and four retained
main tables. R5 preserved validated model code, raw outputs, primary analyses,
figure assets, R1 provenance reframing, R2 literature grounding, R3 statistical
reporting, and R4 figure integration. Exploratory perturbation material is
minimized in the main text and remains clearly supplemental/non-disease-
validating.

Revision Phase R6 administrative cleanup and submission-readiness preparation
is complete. Raw author-confirmation, bracketed blinded-review, repository-link,
and institutional/IP action-item scaffolding was removed from the submitted
manuscript body and moved into submission and repository checklists. R6 created
author, IP/repository, data/code availability, AI disclosure, cover-letter,
submission-readiness, and private-review repository planning files. R6 did not
modify validated model code, raw result CSVs, primary analyses, figure assets,
scientific claims, numerical values, citations, license state, repository
visibility, DOI state, preprint state, or submission state.

Revision Phase R7 LaTeX production and journal-format finalization is complete
within the available environment. R7 hardened build wrappers, added
repository-level and manuscript-local build instructions, applied conservative
LaTeX line-breaking and title-block fixes, removed a visible internal
target-journal note, created a JCNS source package, created R7 archive
sidecars, and performed static LaTeX/source-package validation. Fresh R7 PDFs
could not be compiled because no TeX engine or BibTeX tool is available on
PATH. R7 did not modify validated model code, raw result CSVs, primary
analyses, numerical results, scientific conclusions, figure scientific content,
license state, repository visibility, DOI state, preprint state, or submission
state.

Revision Restart Phase 0 is complete. After R7, an external
pre-submission editorial review was received for the manuscript, and the old
R0-R7 internal revision sequence was closed rather than continued. A new
`manuscript/revision_restart/` sequence now begins with Phase 0: editorial
triage, scientific reframing blueprint, and revision architecture. Phase 0
preserved the external review verbatim, extracted 30 substantive issues,
classified them by severity and type, recommended a revised analytic-divider
and residual-domain thesis, designed Restart Phases 1-8, created decision
queues and analysis requirements, ran static source/SVG/PDF-text searches, and
updated the project state and decision log. Phase 0 was planning only: no
validated model code, raw result files, primary analyses, manuscript scientific
prose, tables, bibliography, figures, release state, license state, DOI state,
public repository, preprint, or submission state was modified.

Revision Restart Phase 4 is complete. NEURON was checked first as an optional
validation dependency but was unavailable in the bundled Python runtime, so no
NEURON result is claimed. Phase 4 added a separated independent direct-matrix
passive benchmark, DC analytic divider/load/limit checks, a bounded BE-vs-CN
peak-difference summary, a diagnostic-only trace overlay, validation
interpretation and manuscript-insert drafts, claim reassessment, and Phase 4
reports. The independent matrix benchmark reproduced existing SPINE baseline
traces to numerical roundoff, with maximum all-trace absolute difference
`1.249e-13` mV across the low/intermediate/high reference cases. Phase 4 did
not modify validated model code, raw result CSVs, manuscript TeX source,
manuscript tables, publication figures, release state, license state, DOI
state, public repository state, preprint state, or submission state.

Revision Restart Phase 5 is complete. Phase 5 created a curated reviewer-access
reproducibility package draft and an unblinded internal release-candidate
package under `submission/reviewer_access_package/`, plus a staging record
under `reproducibility_review_package/`. The blinded package contains 275
files and the unblinded internal package contains 279 files. Both packages
include package-specific reviewer instructions, environment files, test and
reproduction instructions, manifests with file-level SHA-256 checksums, source
code, configs, tests, selected scripts, selected derived source data, generated
figure assets, traceability ledgers, validation reports, and Phase 1-4 restart
outputs. The blinded package identifier audit found 0 text hits after curation
and sanitization. Phase 5 did not create a public repository, select a license,
mint a DOI, submit a preprint, edit manuscript TeX source, edit manuscript
tables, regenerate publication figures, modify validated model code, or modify
raw simulation outputs.

Revision Restart Phase 6 is complete. Phase 6 synthesized the external review
with Restart Phases 1-5 and created a controlled manuscript-rewrite blueprint
without editing manuscript source. The planning-level revised thesis is that
the load-normalized spine-neck ratio recovers the classical local voltage-
divider expectation in the appropriate low-frequency limit, while SPINE's
scientific contribution is quantifying residual departures and identifying
when transient conductance dynamics, impedance, active mechanisms, morphology,
and measurement uncertainty make the scalar descriptor insufficient. Phase 6
recommends using `load-normalized spine-neck ratio` as the lead term and
retaining `SMI` only as author-defined shorthand if needed. It created a
30-row response-to-review matrix, section rewrite blueprint, figure/table
blueprint, availability-language options, pre-submission risk review, Phase 7
prompt draft, and high-level Phase 6 report. Phase 6 did not modify validated
model code, raw result CSVs, manuscript TeX source, manuscript tables,
publication figures, public repository state, license state, DOI state,
preprint state, or submission state.

Revision Restart Phase 7 is complete. Phase 7 executed the controlled
manuscript rewrite around the analytic-divider and residual-domain thesis. The
manuscript now treats the local divider relation as the expected first-order
behavior and residuals/domain boundaries as the scientific object. Phase 7
rewrote the manuscript and supplement source, updated tables, ledgers,
manifests, bibliography details, numerical verification language, and the
divider/residual figure assets, rebuilt unblinded, blinded, target-journal,
and supplement PDFs, and preserved validated solver/runtime code, configs, raw
result CSVs, broad primary ensembles, public repository state, license state,
DOI state, preprint state, and submission state.

Revision Restart Phase 8 is complete. Phase 8 performed final PDF QA, static
language/leakage audit, external-review response audit, hostile reviewer
simulation, claim-evidence audit, reproducibility-package audit, blocker
classification, and build validation. Phase 8 made only minor production
fixes: removed a visible correspondence placeholder, removed visible internal
R4 provenance text from Figure 1, reworded Table 4 to avoid "SMI predicts"
language, changed Figure 8 "prevalence" wording to "design fraction," and
cleaned Figure S9 scenario labeling/layout. The Phase 5 package archives still
match their checksum sidecars, but they predate the current Phase 7/8
manuscript, figure, ledger, and numerical-verification state and must be
rebuilt before reviewer distribution or journal submission. Phase 8 did not
modify validated model code, raw result CSVs, broad primary analyses, public
repository state, license state, DOI state, preprint state, or submission
state.

Revision Restart Phase 9 is complete. Phase 9 rebuilt and synchronized the
private reviewer-access package directories from the current post-Phase-8
state, created new blinded and unblinded Phase 9 archives with checksum
sidecars, created a PI/coauthor review package with decision forms, regenerated
package manifests, ran identifier/local-path/package-language/package-
consistency audits, ran full repository tests and blinded-package smoke tests,
and preserved validated model code, raw result CSVs, broad scientific analyses,
public repository state, license state, DOI state, preprint state, and
submission state.

## Next action

Stop after Revision Restart Phase 9. The next action is PI/coauthor review of
`submission/pi_coauthor_review_package/`. Do not submit, publish a repository,
mint a DOI, select a license, post a preprint, or distribute reviewer packages
until author, PI, institutional, and journal approvals are explicitly obtained.
After human review, perform only the bounded follow-up needed to incorporate
approved metadata/release decisions and any requested production polish.

For scientific interpretation, start with:

- `reports/FINAL_SCIENTIFIC_SYNTHESIS.md`
- `reports/FINAL_CLAIM_AUDIT.md`
- `reports/PUBLICATION_GUIDE.md`
- `manuscript/main_unblinded.tex`
- `manuscript/JOURNAL_TARGET_ASSESSMENT.md`
- `manuscript/NUMERICAL_VERIFICATION_REPORT.md`
- `reports/PHASE_08_REPORT.md`
- `manuscript/LATEX_PRODUCTION_AUDIT.md`
- `manuscript/FIGURE_EMBEDDING_REPORT.md`
- `manuscript/FORMATTING_FIX_REPORT.md`
- `manuscript/PUBLISHER_PROOF_REPORT.md`
- `reports/PHASE07_REPRODUCIBILITY.md`
- `reports/PHASE07_FULL_AUDIT.md`
- `manuscript/revision_v2/R0_SUMMARY_REPORT.md`
- `manuscript/revision_v2/EDITORIAL_REVIEW_RESPONSE_MATRIX.csv`
- `manuscript/revision_v2/REVISION_ACTION_PLAN.md`
- `manuscript/revision_v2/MANUSCRIPT_TERMINOLOGY_MAP.md`
- `manuscript/revision_v2/R1_PROVENANCE_NOVELTY_REPORT.md`
- `manuscript/revision_v2/R1_TERMINOLOGY_AUDIT.csv`
- `manuscript/revision_v2/R1_NEXT_PHASE_HANDOFF.md`
- `manuscript/revision_v2/R2_LITERATURE_AUDIT.md`
- `manuscript/revision_v2/R2_REFERENCE_VERIFICATION_TABLE.csv`
- `manuscript/revision_v2/R2_CITATION_PLACEMENT_LOG.csv`
- `manuscript/revision_v2/R2_BIBLIOGRAPHY_CLEANUP_REPORT.md`
- `manuscript/revision_v2/R2_MAIN_TEXT_CITATION_AUDIT.md`
- `manuscript/revision_v2/R2_SUPPLEMENT_CITATION_AUDIT.md`
- `manuscript/revision_v2/R2_NEXT_PHASE_HANDOFF.md`
- `reports/PHASE_R2_REPORT.md`
- `manuscript/revision_v2/R5_STRUCTURE_AND_COMPRESSION_REPORT.md`
- `manuscript/revision_v2/R5_SECTION_REORGANIZATION_MAP.csv`
- `manuscript/revision_v2/R5_PROSE_CHANGE_LOG.md`
- `manuscript/revision_v2/R5_PHASE06_DEMOTION_REPORT.md`
- `manuscript/revision_v2/R5_STATIC_SEARCH_AUDIT.md`
- `manuscript/revision_v2/R5_WORD_COUNT_AND_STRUCTURE_AUDIT.md`
- `manuscript/revision_v2/R5_NEXT_PHASE_HANDOFF.md`
- `reports/PHASE_R5_REPORT.md`
- `manuscript/revision_v2/R6_ADMIN_CLEANUP_REPORT.md`
- `manuscript/revision_v2/R6_STATIC_PLACEHOLDER_AUDIT.md`
- `manuscript/revision_v2/R6_BLINDING_AND_ADMIN_AUDIT.md`
- `manuscript/revision_v2/R6_NEXT_PHASE_HANDOFF.md`
- `reports/PHASE_R6_REPORT.md`
- `submission/AUTHOR_CONFIRMATION_CHECKLIST.md`
- `submission/IP_AND_REPOSITORY_RELEASE_CHECKLIST.md`
- `submission/DATA_CODE_AVAILABILITY_OPTIONS.md`
- `submission/AI_DISCLOSURE_OPTIONS.md`
- `submission/COVER_LETTER_DRAFT.md`
- `submission/SUBMISSION_READINESS_CHECKLIST.md`
- `repository/PRIVATE_REVIEW_REPOSITORY_PLAN.md`
- `LATEX_BUILD_INSTRUCTIONS.md`
- `manuscript/BUILD_INSTRUCTIONS.md`
- `submission/jcns_source_package/README_BUILD.txt`
- `manuscript/revision_v2/R7_LATEX_PRODUCTION_REPORT.md`
- `manuscript/revision_v2/R7_OVERFULL_BOX_REPORT.md`
- `manuscript/revision_v2/R7_FIGURE_TABLE_LAYOUT_AUDIT.md`
- `manuscript/revision_v2/R7_BLINDED_PDF_AUDIT.md`
- `manuscript/revision_v2/R7_JCNS_SOURCE_PACKAGE_REPORT.md`
- `manuscript/revision_v2/R7_STATIC_PLACEHOLDER_AND_PATH_AUDIT.md`
- `manuscript/revision_v2/R7_NEXT_PHASE_HANDOFF.md`
- `reports/PHASE_R7_REPORT.md`
- `manuscript/revision_restart/PHASE0_EXTERNAL_REVIEW_SOURCE.md`
- `manuscript/revision_restart/PHASE0_EXECUTIVE_TRIAGE.md`
- `manuscript/revision_restart/PHASE0_REVIEW_RESPONSE_MATRIX.csv`
- `manuscript/revision_restart/PHASE0_REVISED_THESIS_BLUEPRINT.md`
- `manuscript/revision_restart/PHASE0_PHASE_ARCHITECTURE.md`
- `manuscript/revision_restart/PHASE0_DECISION_QUEUES.md`
- `manuscript/revision_restart/PHASE0_ANALYSIS_REQUIREMENTS_SPEC.md`
- `manuscript/revision_restart/PHASE0_STATIC_SEARCH_AUDIT.md`
- `manuscript/revision_restart/PHASE0_RISK_REGISTER.md`
- `manuscript/revision_restart/PHASE0_NEXT_PHASE_HANDOFF.md`
- `reports/PHASE_RESTART_0_REPORT.md`
- `manuscript/revision_restart/PHASE1_ANALYTIC_DIVIDER_DERIVATION.md`
- `manuscript/revision_restart/PHASE1_RESIDUAL_ANALYSIS_REPORT.md`
- `manuscript/revision_restart/PHASE1_CLAIM_REASSESSMENT.md`
- `manuscript/revision_restart/PHASE1_NEXT_PHASE_HANDOFF.md`
- `reports/PHASE_RESTART_1_REPORT.md`
- `manuscript/revision_restart/PHASE2_DESCRIPTOR_VALUE_ANALYSIS_REPORT.md`
- `manuscript/revision_restart/PHASE2_CLAIM_REASSESSMENT.md`
- `manuscript/revision_restart/PHASE2_NAMING_AND_NOVELTY_IMPLICATIONS.md`
- `manuscript/revision_restart/PHASE2_NEXT_PHASE_HANDOFF.md`
- `reports/PHASE_RESTART_2_REPORT.md`
- `manuscript/revision_restart/PHASE3_STATISTICAL_REFRAMING_REPORT.md`
- `manuscript/revision_restart/PHASE3_HIGH_SMI_COVERAGE_REPORT.md`
- `manuscript/revision_restart/PHASE3_NEXT_PHASE_HANDOFF.md`
- `reports/PHASE_RESTART_3_REPORT.md`
- `manuscript/revision_restart/PHASE4_VALIDATION_STRATEGY.md`
- `manuscript/revision_restart/PHASE4_VALIDATION_INTERPRETATION.md`
- `manuscript/revision_restart/PHASE4_MANUSCRIPT_INSERT_DRAFT.md`
- `manuscript/revision_restart/PHASE4_CLAIM_REASSESSMENT.md`
- `manuscript/revision_restart/PHASE4_NEXT_PHASE_HANDOFF.md`
- `reports/PHASE_RESTART_4_REPORT.md`

## Phase table

| Phase | Status | Report | Checkpoint |
|---|---|---|---|
| 00 | Completed | `reports/PHASE_00_REPORT.md` | `checkpoints/SPINE_phase_00_checkpoint.zip` |
| 01 | Completed | `reports/PHASE_01_REPORT.md` | `checkpoints/SPINE_phase_01_checkpoint.zip` |
| 01.1 | Completed | `reports/PHASE_01_1_REPORT.md` | `checkpoints/SPINE_phase_01_1_checkpoint.zip` |
| 02 | Completed | `reports/PHASE_02_REPORT.md` | `checkpoints/SPINE_phase_02_checkpoint.zip` |
| 03 | Completed | `reports/PHASE_03_REPORT.md` | `checkpoints/SPINE_phase_03_checkpoint.zip` |
| 04 | Completed | `reports/PHASE_04_REPORT.md` | `checkpoints/SPINE_phase_04_checkpoint.zip` |
| 05 | Completed | `reports/PHASE_05_REPORT.md` | `checkpoints/SPINE_phase_05_checkpoint.zip` |
| 05.1 | Completed | `reports/PHASE_05_1_REPORT.md` | `checkpoints/SPINE_phase_05_1_checkpoint.zip` |
| 06 | Completed | `reports/PHASE_06_REPORT.md` | `checkpoints/SPINE_phase_06_checkpoint.zip` |
| 07 | Completed | `reports/PHASE_07_REPORT.md` | `checkpoints/SPINE_phase_07_checkpoint.zip` |
| 08 | Completed | `reports/PHASE_08_REPORT.md` | `checkpoints/SPINE_phase_08_checkpoint.zip` |
| R5 | Completed | `reports/PHASE_R5_REPORT.md` | `checkpoints/SPINE_phase_R5_checkpoint.zip` |
| R6 | Completed | `reports/PHASE_R6_REPORT.md` | `checkpoints/SPINE_phase_R6_checkpoint.zip` |
| R7 | Completed | `reports/PHASE_R7_REPORT.md` | `checkpoints/SPINE_phase_R7_checkpoint.zip` |
| Restart 0 | Completed | `reports/PHASE_RESTART_0_REPORT.md` | `checkpoints/SPINE_restart_phase_0_checkpoint.zip` |
| Restart 1 | Completed | `reports/PHASE_RESTART_1_REPORT.md` | `checkpoints/SPINE_restart_phase_1_checkpoint.zip` |
| Restart 2 | Completed | `reports/PHASE_RESTART_2_REPORT.md` | `checkpoints/SPINE_restart_phase_2_checkpoint.zip` |
| Restart 3 | Completed | `reports/PHASE_RESTART_3_REPORT.md` | `checkpoints/SPINE_restart_phase_3_checkpoint.zip` |
| Restart 4 | Completed | `reports/PHASE_RESTART_4_REPORT.md` | `checkpoints/SPINE_restart_phase_4_checkpoint.zip` |

## Last verified checks

- `python` on PATH: failed; command not available in this shell.
- Bundled runtime: `C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe --version` -> Python 3.12.13.
- `pytest`: unavailable in bundled runtime (`No module named pytest`).
- Phase 00 scaffold tests: `PYTHONPATH=src <bundled-python> -m unittest discover -s tests -p 'test_*.py'` -> 5 tests passed.
- Git status: attempted `git status --short`; failed because `git` is not available on PATH.
- Phase 01 tests: `PYTHONPATH=src <bundled-python> -m unittest discover -s tests -p 'test_*.py'` -> 16 tests passed.
- Phase 01 CLI smoke: `PYTHONPATH=src <bundled-python> -m spine.cli smoke configs\manuscript_faithful\baseline.toml --output-csv results\phase01_smoke_trace.csv` -> passed and exported CSV.
- Phase 01 checkpoint created at `checkpoints/SPINE_phase_01_checkpoint.zip`; see adjacent `.sha256` file for digest.
- Phase 01.1 tests: `PYTHONPATH=src <bundled-python> -m unittest discover -s tests -p 'test_*.py'` -> 18 tests passed.
- Phase 01.1 checkpoint created at `checkpoints/SPINE_phase_01_1_checkpoint.zip`; see adjacent `.sha256` file for digest.
- Phase 02 reproduction: `PYTHONPATH=src <bundled-python> scripts/reproduce_manuscript.py` -> passed and generated source data/figures.
- Phase 02 tests: `PYTHONPATH=src <bundled-python> -m unittest discover -s tests -p 'test_*.py'` -> 22 tests passed.
- Phase 03 generation: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\run_phase03.py` -> passed and generated source data/figures.
- Phase 03 tests: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p 'test_*.py'` -> 29 tests passed in 2.569s.
- Phase 03 checkpoint created at `checkpoints/SPINE_phase_03_checkpoint.zip`; see adjacent `.sha256` file for digest.
- Final Phase 03 Git status review: `git status --short` failed because `git` is not available on PATH in this shell.
- Phase 04 generation: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\run_phase04.py` -> passed and generated source data/figures.
- Phase 04 tests: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p 'test_*.py'` -> 34 tests passed in 2.836s.
- Phase 04 checkpoint created at `checkpoints/SPINE_phase_04_checkpoint.zip`; see adjacent `.sha256` file for digest.
- Final Phase 04 Git status review: `git status --short` failed because `git` is not available on PATH in this shell.
- Phase 05 generation: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\run_phase05.py` -> passed and generated source data/figures.
- Phase 05 focused tests: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_phase05_sensitivity_statistics` -> 6 tests passed in 0.034s.
- Phase 05 tests: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p 'test_*.py'` -> 40 tests passed in 2.998s.
- Phase 05 validation table: 6 of 7 validation checks passed; the predefined `uncertainty_convergence_48_vs_96` check failed with value `0.18885434806962575` against threshold `0.10`, driven by SMI median instability.
- Phase 05 checkpoint created at `checkpoints/SPINE_phase_05_checkpoint.zip`; see adjacent `.sha256` file for digest.
- Final Phase 05 Git status review: `git status --short` failed because `git` is not available on PATH in this shell.
- Phase 05.1 syntax check: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m py_compile src\spine\phase05_1.py scripts\run_phase05_1.py` -> passed.
- Phase 05.1 generation: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\run_phase05_1.py` -> passed and generated progressive N=96/192/384/768 audit source data/figures.
- Revision R1 static terminology audit: high-risk provenance terms
  `manuscript-faithful`, `reproduction`, `reproduced`, `reported caption`,
  `caption targets`, `prior manuscript`, `original manuscript`, `manuscript
  findings`, `Phase 02` through `Phase 08`, `candidate revised`, `publication
  figure logic`, and `epileptogenesis` were absent from the comparable
  manuscript/supplement source scope after edits.
- Revision R1 manuscript-package tests: `$env:PYTHONPATH='src'; &
  'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
  -m unittest tests.test_phase08_manuscript_package` -> 6 tests passed in
  0.035s.
- Revision R1 full tests: `$env:PYTHONPATH='src'; &
  'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
  -m unittest discover -s tests -p 'test_*.py'` -> 63 tests passed in
  3.493s.
- Revision R1 checkpoint created at
  `checkpoints/SPINE_phase_R1_checkpoint.zip`.
- Revision R1 LaTeX compilation: not attempted because `latexmk`, `pdflatex`,
  `biber`, `bibtex`, and `tectonic` were not visible on PATH.
- Revision R1 Git status review: attempted `git status --short`; failed
  because `git` is not available on PATH in this shell.
- Revision R2 Crossref verification: DOI lookups verified the R2-added or
  corrected records for `Magee2000Review`, `MageeCook2000`, `Magee1998`,
  `Magee1999`, `Harnett2012SpineAmplification`,
  `Tonnesen2014SpineNeckPlasticity`, `TonnesenNagerl2016`,
  `Hines2004ModelDB`, `Wilkinson2016FAIR`, and
  `Jarsky2005DendriticSpikePropagation`.
- Revision R2 CSV parse check: `Import-Csv
  manuscript\revision_v2\R2_REFERENCE_VERIFICATION_TABLE.csv` -> 35 rows;
  `Import-Csv manuscript\revision_v2\R2_CITATION_PLACEMENT_LOG.csv` -> 10
  rows.
- Revision R2 static citation/BibTeX check: manuscript bibliography keys = 34;
  used citation keys = 34; duplicate manuscript keys = 0; duplicate broader
  keys = 0; missing citation keys = 0; uncited manuscript entries = 0;
  suspicious DOI fields = 0; non-ASCII reference characters = 0; `and others`
  or `et al.` author-field hits = 0.
- Revision R2 stale-key scan: `rg -n
  "Major2008|Magee1998HCN|and others|et al\." manuscript\references.bib
  references\references.bib manuscript\sections manuscript\supplement\sections`
  -> no hits.
- Revision R2 TeX/toolchain audit:
  `Get-Command latexmk,pdflatex,biber,bibtex,tectonic,make,git
  -ErrorAction SilentlyContinue` -> no matching executables were visible on
  PATH.
- Revision R2 focused manuscript-package tests: `$env:PYTHONPATH='src'; &
  'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
  -m unittest tests.test_phase08_manuscript_package` -> 6 tests passed in
  0.031s.
- Revision R2 full tests: `$env:PYTHONPATH='src'; &
  'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
  -m unittest discover -s tests -p 'test_*.py'` -> 63 tests passed in 3.633s.
- Revision R2 checkpoint created at
  `checkpoints/SPINE_phase_R2_checkpoint.zip`; see adjacent `.sha256` sidecar
  for digest.
- Final Revision R2 Git status review: `git status --short` failed because
  `git` is not available on PATH in this shell.
- Phase 05.1 focused tests: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_phase05_1_convergence_audit` -> 5 tests passed in 0.068s.
- Phase 05.1 tests: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p 'test_*.py'` -> 45 tests passed in 2.925s.
- Phase 05.1 validation table: 6 of 7 validation checks passed; final SMI median convergence passed with value `0.012090835475659055`, final all-median convergence passed with value `0.029154415501181967`, and the predefined final ranking stability check failed because near-tied active local dynamic-SMI predictors changed rank.
- Phase 05.1 checkpoint created at `checkpoints/SPINE_phase_05_1_checkpoint.zip`; see adjacent `.sha256` file for digest.
- Final Phase 05.1 Git status review: `git status --short` failed because `git` is not available on PATH in this shell.
- Phase 06 syntax check: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m py_compile src\spine\phase06.py scripts\run_phase06.py` -> passed.
- Phase 06 first generation attempt: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\run_phase06.py` -> timed out at 120 s with `N=32`; incomplete outputs were not accepted.
- Phase 06 generation: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\run_phase06.py` -> passed after using the documented `N=8` deterministic Phase 06 uncertainty screen.
- Phase 06 focused tests: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_phase06_epilepsy_exploratory` -> 6 tests passed in 0.003s.
- Phase 06 tests: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p 'test_*.py'` -> 51 tests passed in 4.294s.
- Phase 06 validation table: 6 of 6 validation checks passed; active solutions were finite for all 99 scenario/uncertainty simulations and gating variables stayed in bounds.
- Phase 06 final focused tests after report/state updates: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_phase06_epilepsy_exploratory` -> 6 tests passed in 0.004s.
- Phase 06 checkpoint created at `checkpoints/SPINE_phase_06_checkpoint.zip`; see adjacent `.sha256` file for digest.
- Final Phase 06 Git status review: `git status --short` failed because `git` is not available on PATH in this shell.
- Final Phase 06 full test suite after all report/state edits: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p 'test_*.py'` -> 51 tests passed in 2.963s.
- Phase 07 config-load audit before fix: `$env:PYTHONPATH='src'; Get-ChildItem configs -Recurse -Filter *.toml | ForEach-Object { & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m spine.cli load-config $_.FullName }` -> active extension and manuscript/plausibility tracks loaded, but Phase 06 TOML files reported `unknown`.
- Phase 07 config metadata fix: `spine.config.load_config` now falls back from `[meta].track` to top-level `track`, and `configs/epilepsy_exploratory/scenarios.toml` now declares `track = "epilepsy_exploratory"`.
- Phase 07 config-load audit after fix: same command -> `active_extension`, `epilepsy_exploratory`, `epilepsy_exploratory`, `manuscript_faithful`, `plausibility_revised`.
- Phase 07 CLI smoke: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m spine.cli smoke configs\manuscript_faithful\baseline.toml --output-csv results\phase07_cli_smoke_trace.csv` -> passed; `SMI=0.114742`, `A_h_mV=2.35578`, `Gamma_h_to_d=0.751282`.
- Phase 07 release tests: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_phase07_release_package` -> 6 tests passed in 0.004s.
- Phase 07 full test suite: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p 'test_*.py'` -> 57 tests passed in 2.905s.
- Final Phase 07 full test suite after all project-state edits: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p 'test_*.py'` -> 57 tests passed in 3.287s.
- Phase 07 checkpoint created: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\make_checkpoint.py 7` -> created `checkpoints/SPINE_phase_07_checkpoint.zip`; see adjacent `.sha256` file for digest.
- Final Phase 07 Git status review: `git status --short` failed because `git` is not available on PATH in this shell.
- Phase 08 journal/toolchain audit: `Get-Command latexmk,pdflatex,biber,bibtex,tectonic,make,git,gh -ErrorAction SilentlyContinue` -> no matching executables were visible on PATH.
- Phase 08 focused manuscript-package tests: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_phase08_manuscript_package` -> 6 tests passed in 0.014s.
- Phase 08 full test suite: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p 'test_*.py'` -> 63 tests passed in 2.920s.
- Phase 08 config-load audit: `$env:PYTHONPATH='src'; Get-ChildItem configs -Recurse -Filter *.toml | ForEach-Object { & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m spine.cli load-config $_.FullName }` -> `active_extension`, `epilepsy_exploratory`, `epilepsy_exploratory`, `manuscript_faithful`, `plausibility_revised`.
- Phase 08 text hygiene scan: new manuscript/submission/repository text files contained no non-ASCII characters.
- Phase 08 LaTeX compilation: pending because no TeX distribution or bibliography executable was visible on PATH in this shell; no compilation success is claimed.
- Final Phase 08 Git status review: `git status --short` failed because `git` is not available on PATH in this shell.
- Phase 08 archive creation: `Compress-Archive` created `checkpoints/SPINE_manuscript_submission_package.zip`, `checkpoints/SPINE_blinded_submission_package.zip`, and `checkpoints/SPINE_reproducible_repository_release_candidate.zip`; adjacent `.sha256` checksum files were generated with `Get-FileHash`.
- Phase 08 archive note: an initial parallel attempt to create the blinded package failed due temporary SVG file locks from another archive process; rerunning the blinded archive sequentially succeeded.
- Phase 08 checkpoint created: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\make_checkpoint.py 8` -> created `checkpoints/SPINE_phase_08_checkpoint.zip`; see adjacent `.sha256` file for digest.
- Production pass figure rendering: `& 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' manuscript\render_figure_pdfs.py` -> rendered 27 SVG figures to PDF fallbacks.
- Production pass static validation: custom bundled-Python check -> `STATIC_PRODUCTION_VALIDATION PASS`, with 18 main PDF figure assets and 9 supplemental PDF figure assets.
- Production pass build attempt: `powershell -ExecutionPolicy Bypass -File manuscript\build.ps1 all` -> failed because `pdflatex` is not available on PATH; no post-edit PDF compilation success is claimed.
- Production pass renderer syntax check: `& 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m py_compile manuscript\render_figure_pdfs.py` -> passed.
- Production pass focused manuscript-package tests: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_phase08_manuscript_package` -> 6 tests passed in 0.015s.
- Production pass full test suite: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p 'test_*.py'` -> 63 tests passed in 3.030s.
- Production pass Git status review: `git status --short` failed because `git` is not available on PATH in this shell.
- Production pass archive refresh: `Compress-Archive` refreshed `checkpoints/SPINE_manuscript_submission_package.zip`, `checkpoints/SPINE_blinded_submission_package.zip`, and `checkpoints/SPINE_reproducible_repository_release_candidate.zip` with updated checksum sidecars.
- Production pass checkpoint refresh: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\make_checkpoint.py 8` -> refreshed `checkpoints/SPINE_phase_08_checkpoint.zip`; see adjacent `.sha256` sidecar for the digest.
- Revision R5 word count and structure audit: bundled Python LaTeX-stripped counter -> main narrative 4459 words; abstract 161; introduction 503; methods 1402; results 1137; discussion 913; conclusion 63; 8 main figure includes; 4 main table inputs; 9 supplemental figures; 7 supplement sections.
- Revision R5 static search: `Select-String` over manuscript TeX/CSV sources for phase/reproduction/internal-memo/disease terms -> no main scientific narrative hits; remaining hits classified as R6 administrative placeholders or supplement/provenance exploratory context.
- Revision R5 citation consistency: bundled Python BibTeX/citation check -> used citation keys = 34; defined manuscript bibliography keys = 34; missing keys = 0; duplicate keys = 0; uncited manuscript entries = 0.
- Revision R5 figure include audit: `Select-String -Path manuscript\sections\results.tex -Pattern '\\includegraphics'` -> 8 main publication figure includes retained.
- Revision R5 TeX/Git tool discovery: `Get-Command latexmk,pdflatex,biber,bibtex,tectonic,git -ErrorAction SilentlyContinue` -> no matching executables visible on PATH.
- Revision R5 focused manuscript-package tests: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_phase08_manuscript_package` -> 6 tests passed in 0.013s.
- Revision R5 full tests: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p 'test_*.py'` -> 63 tests passed in 3.510s.
- Final Revision R5 Git status review: `git status --short` failed because `git` is not available on PATH in this shell.
- Revision R5 checkpoint created at `checkpoints/SPINE_phase_R5_checkpoint.zip`; see adjacent `.sha256` sidecar for digest.
- Revision R6 static placeholder search over manuscript/submission/repository sources -> no hits in manuscript or supplement source files; remaining hits are confined to submission checklists or repository technical/release-planning docs.
- Revision R6 manuscript-only placeholder search -> no hits for raw author-confirmation, bracketed review, action-item, repository-link, DOI, license, manuscript-faithful, prior-manuscript, reported-caption, Phase 06, clinical_claim, or epileptogenesis terms.
- Revision R6 blinded-source identifier search -> no hits for author names, institutional names, local workspace paths, or user identifiers in `main_blinded.tex`, shared manuscript sections, or supplement sections.
- Revision R6 TeX/Git tool discovery: `Get-Command latexmk,pdflatex,biber,bibtex,tectonic,git -ErrorAction SilentlyContinue` -> no matching executables visible on PATH.
- Revision R6 focused manuscript-package tests: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_phase08_manuscript_package` -> 6 tests passed in 0.013s.
- Revision R6 full tests: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p 'test_*.py'` -> 63 tests passed in 3.194s.
- Final Revision R6 Git status review: `git status --short` failed because `git` is not available on PATH in this shell.
- Revision R6 checkpoint created at `checkpoints/SPINE_phase_R6_checkpoint.zip`; see adjacent `.sha256` sidecar for digest.
- Revision R7 TeX/tool discovery: `Get-Command latexmk,pdflatex,biber,bibtex,tectonic,xelatex,lualatex,latex,kpsewhich,perl,magick,gs,mutool,pdftoppm -ErrorAction SilentlyContinue`, `where.exe pdflatex latexmk bibtex tectonic xelatex lualatex perl`, and common program-directory searches found no TeX engine, BibTeX tool, or Perl installation visible to this shell.
- Revision R7 build attempt: `powershell -ExecutionPolicy Bypass -File manuscript\build.ps1 all` -> failed with `pdflatex is not available on PATH.` No fresh R7 PDFs were generated.
- Revision R7 static LaTeX/source-package validation: `tex_files=27`, `used_citations=34`, `defined_bib_keys=34`, `source_package_files=51`, `errors=0`.
- Revision R7 static placeholder/path audit: no hits in manuscript, supplement, or JCNS source-package TeX files for local paths, raw placeholders, prior-manuscript framing, reported-caption language, or action-item text.
- Revision R7 blinded-source audit: no hits for author names, institution names, local paths, user identifiers, or GitHub URLs in the blinded manuscript source scope or corresponding source-package files.
- Revision R7 focused manuscript-package tests: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest tests.test_phase08_manuscript_package` -> 6 tests passed in 0.018s.
- Revision R7 full tests: `$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests -p 'test_*.py'` -> 63 tests passed in 3.989s.
- Revision R7 source package archive created at `checkpoints/SPINE_R7_jcns_source_package.zip`; SHA-256 digest `3c5e90aa64e2faf1ae5b8b2b4058abf383465fcd392246779d4088cdd3154a89`.
- Revision R7 compiled-PDF package archive created at `checkpoints/SPINE_R7_compiled_pdf_package.zip`; SHA-256 digest `7fb77952a85e47dbdf121c4ba4f1525f39106a06908828558ad423595b4be184`. The archive contains only a README because no R7 PDFs could be compiled in this environment.
- Final Revision R7 Git status review: `git status --short` failed because `git` is not available on PATH in this shell.
- Revision R7 checkpoint created at `checkpoints/SPINE_phase_R7_checkpoint.zip`; see adjacent `.sha256` sidecar for digest.
- Restart Phase 0 external review preservation: source hash `cc62eef531bf6bc07ff6d19b8196156a6c8dc28258ebfbe1b04899152a82f7ee` matched copied `PHASE0_EXTERNAL_REVIEW_SOURCE.md` hash.
- Restart Phase 0 required artifact check: 10 of 10 required `PHASE0_*` artifacts present, plus `reports/PHASE_RESTART_0_REPORT.md`.
- Restart Phase 0 issue-matrix parse: `Import-Csv manuscript\revision_restart\PHASE0_REVIEW_RESPONSE_MATRIX.csv` -> 30 issue rows; severity counts fatal=1, major=12, moderate=14, minor=3; all required columns present.
- Restart Phase 0 protected-file hash comparison: 185 protected source/data/manuscript/figure files checked; 0 hash changes after Phase 0 artifact creation.
- Restart Phase 0 static search audit: source search found 2 `Spine Morphology Index` hits, 6 `Load-Normalized Spine-Neck Index` hits, 35 `R3` hits, 17 `R4` hits, 7 `Wilson` hits, 15 `bootstrap` hits, 13 `prevalence` hits, and no raw placeholder/TODO/FIXME hits in searched manuscript source scope; SVG/PDF searches found visible Fig. 1 internal `R4 rebuild uses existing audited CSV outputs only` text and PDF `ltering` ligature-loss patterns.
- Final Restart Phase 0 Git status review: `git status --short` failed because `git` is not available on PATH in this shell.

## Phase 00 completed work

- Parsed the manuscript and targeted master specification sections relevant to Phase 00.
- Created traceability, research review, research ledger, references, unit audit, model specification, scientific decisions, and limitations documents.
- Verified a focused literature set with Crossref where possible on 2026-06-09.
- Created an installable Python package scaffold under `src/spine/`.
- Created separate `manuscript_faithful` and `plausibility_revised` TOML configs.
- Added minimal import, configuration-loading, and unit-conversion tests.
- Corrected a Phase 00 neck-resistance expected-value slip caught by tests.

## Phase 01 completed work

- Verified Phase 00 traceability, model specification, and unit audit consistency before implementation.
- Documented the full passive matrix form and backward Euler/Crank-Nicolson equations in `docs/MODEL_SPECIFICATION.md`.
- Implemented cylindrical and nonuniform neck resistance helpers.
- Implemented manuscript-faithful SI parameter conversion from `configs/manuscript_faithful/baseline.toml`.
- Implemented passive three-compartment backward Euler and Crank-Nicolson cross-check solvers.
- Implemented conductance-based normalized double-exponential synapse.
- Implemented dendrite-soma input resistance with the stimulated spine completely omitted.
- Implemented SMI and voltage/current/charge/driving-force metrics.
- Defined metric window `T = 50 ms` without tuning to manuscript figures.
- Added Phase 01 tests for units, geometry, synapse normalization, analytical limits, solver comparison, time-step refinement, current balance, SMI, and high-synapse stability.

## Phase 01.1 completed work

- Implemented Section 7 recommendations from `reports/PHASE_01_AUDIT.md`.
- Corrected stale traceability entries for nonuniform neck resistance, metric tests, and synaptic-current artifacts.
- Clarified `MODEL_SPECIFICATION.md` scope, `I_ext` availability, signed current metrics, driving-force reduction metrics, and validation guardrails.
- Clarified `UNIT_AUDIT.md` resistivity handling at the geometry boundary.
- Added validation for positive programmatic passive parameters and input-resistance duration.
- Added explicit driving-force reduction metrics without changing passive solver equations.

## Phase 02 completed work

- Generated all Phase 02 manuscript reproduction source data under `results/phase02/`.
- Generated editable SVG reproduction figures under `figures/phase02/`.
- Produced `reports/MANUSCRIPT_REPRODUCTION.md`.
- Produced `reports/VALIDATION_REPORT_BASELINE.md`.
- Produced `reports/PHASE_02_REPORT.md`.
- Produced quantitative discrepancy table against manuscript-reported Figure 2 caption values.
- Performed timestep convergence checks for the intermediate condition.
- Tested central SMI claims, recording both support and fixed-load limitations.

## Phase 03 completed work

- Wrote preimplementation hypotheses and falsification criteria in `reports/PHASE03_HYPOTHESES.md`.
- Implemented generalized passive compartment trees with first-principles matrix assembly.
- Implemented procedural cables, branch points, arbitrary spine attachment, and an internal lightweight SWC parser.
- Implemented cylindrical, tapered, constricted, nonuniform-profile, and distributed passive neck models.
- Implemented local input impedance, transfer impedance, gain, phase, impedance spectra, dynamic SMI candidates, sinusoidal validation, and logarithmic-chirp validation.
- Implemented iso-SMI, iso-neck-resistance, iso-transfer, location, and load challenge experiments.
- Compared SMI against neck, load, impedance, and morphology-derived predictors for `Gamma_h_to_d`, `Gamma_h_to_s`, and `A_h_mV`.
- Generated source data under `results/phase03/` and SVG figures under `figures/phase03/`.
- Produced `reports/PHASE03_IMPEDANCE_REPORT.md`, `reports/PHASE03_SMI_CHALLENGE_REPORT.md`, `reports/PHASE03_PREDICTOR_COMPARISON.md`, and `reports/PHASE_03_REPORT.md`.
- Preserved negative findings: SMI succeeds locally for `Gamma_h_to_d` but fails iso-SMI spread tests and is outperformed for somatic transfer and head amplitude.

## Pending Phase 04 work

None. Phase 04 is complete.

## Phase 04 completed work

- Wrote preimplementation hypotheses and validation criteria in `reports/PHASE04_HYPOTHESES.md`.
- Implemented AMPA and AMPA+NMDA synapses with voltage-dependent magnesium block.
- Implemented restrained Na, KDR, HCN, A-type potassium, and electrical-only calcium conductances.
- Kept active mechanisms disabled in `manuscript_faithful` and enabled only through active-extension configuration or explicit placement.
- Implemented a semi-implicit nonlinear solver with exponential gate updates, gate initialization, gate bounds, voltage safeguards, external current injection, and conductance voltage clamps.
- Added independent explicit-Euler limiting-case solver cross-checks.
- Generated active validation, active SMI challenge, predictor comparison, multivariable diagnostic, active impedance, protocol-library, and summary CSV files under `results/phase04/`.
- Generated Phase 04 SVG figures under `figures/phase04/`.
- Produced `reports/PHASE04_ACTIVE_VALIDATION.md`, `reports/PHASE04_ACTIVE_SMI_REPORT.md`, `reports/PHASE04_PROTOCOL_REPORT.md`, and `reports/PHASE_04_REPORT.md`.
- Preserved negative findings: SMI remains useful for local isolation but fails for somatic transfer, head amplitude, and active/NMDA iso-SMI counterexamples.

## Pending Phase 05 work

None. Phase 05 is complete.

## Phase 05 completed work

- Wrote preimplementation hypotheses, falsification criteria, and predefined
  uncertainty distributions in `reports/PHASE05_HYPOTHESES.md`.
- Implemented normalized local sensitivity analysis for geometry, load,
  synaptic, and active-extension parameters.
- Implemented deterministic Latin-hypercube uncertainty sampling with fixed
  seeds.
- Explicitly propagated neck-radius measurement uncertainty into `R_neck`, SMI,
  and SMI class stability.
- Generated percentile uncertainty intervals and rank-correlation uncertainty
  screening tables.
- Exported practical identifiability and parameter-degeneracy examples.
- Compared predictors with Pearson, Spearman, bootstrap intervals,
  cross-validated RMSE, fixed multivariable diagnostics, and focused residual
  analysis.
- Quantified passive and active counterexample prevalence.
- Classified major Phase 03-04 synthesis claims and wrote manuscript revision
  guidance.
- Preserved the negative validation result that the SMI median did not meet the
  predefined 48-vs-96 sample convergence threshold.

## Phase 05.1 completed work

- Implemented a Phase 05.1 audit layer in `src/spine/phase05_1.py` without
  modifying validated passive or active model behavior.
- Repeated deterministic global uncertainty analyses at N=96, 192, 384, and
  768 using the existing Phase 05 distributions and deterministic seed
  convention.
- Determined that the original Phase 05 `uncertainty_convergence_48_vs_96`
  failure was a real small-sample/partition warning for a skewed SMI
  distribution, not an implementation defect.
- Demonstrated final SMI median convergence by N=768 while preserving the
  failed exact predictor-ranking stability validation.
- Quantified radius-only uncertainty propagation, radius-driven SMI class
  instability, boundary-localized class flips, and explicit fragile examples.
- Recomputed predictor rankings, bootstrap intervals, cross-validation metrics,
  multivariable diagnostics, and counterexample prevalence across increasing
  sample sizes.
- Reassessed claims and manuscript impact: SMI local descriptor remains
  supported; SMI amplitude failure and equal-SMI non-equivalence remain
  strongly supported; non-universal transfer interpretation is supported;
  active-sharpening remains uncertain; SMI class stability is contradicted.

## Phase 06 completed work

- Wrote preimplementation hypotheses and falsification criteria in
  `reports/PHASE06_HYPOTHESES.md`.
- Created a separated `configs/epilepsy_exploratory/` configuration family
  with explicit no-clinical-claims and no-tuning metadata.
- Added `src/spine/phase06.py` and `scripts/run_phase06.py` without changing
  validated baseline/passive/active/Phase 05/Phase 05.1 behavior.
- Performed a focused literature review and exported
  `results/phase06/epilepsy_evidence_table.csv`; updated
  `docs/RESEARCH_LEDGER.csv` and `references/references.bib`.
- Implemented restrained exploratory scenarios for morphology, HCN, potassium,
  AMPA/NMDA synaptic strength, clustering/synchrony, combined perturbations,
  and a conflicting-direction alternative.
- Ran isolated single-spine, clustered synchronous, and clustered asynchronous
  protocols and exported machine-readable metrics.
- Propagated deterministic scenario uncertainty with `N=8` samples per
  scenario, explicitly documented as a sensitivity screen rather than a
  biological confidence interval.
- Computed SMI, passive/active impedance descriptors, voltage attenuation,
  latency, half-width, voltage-integral, driving-force, threshold, predictor,
  and mechanistic-decomposition metrics.
- Preserved negative findings: unchanged-SMI synaptic and active/channel
  scenarios changed voltage outcomes, and clustered synchronous drive produced
  threshold-like behavior not described by isolated single-spine SMI.
- Generated Phase 06 source data under `results/phase06/`, SVG figures under
  `figures/phase06/`, and required reports under `reports/`.

## Phase 07 completed work

- Audited implementation/documentation/report/source-data consistency.
- Updated `docs/TRACEABILITY_MATRIX.csv` to close stale early-phase entries
  and include Phase 03-06 artifacts.
- Added final release reports:
  `PHASE07_FULL_AUDIT.md`, `PHASE07_REPRODUCIBILITY.md`,
  `FINAL_SCIENTIFIC_SYNTHESIS.md`, `PUBLICATION_GUIDE.md`,
  `FIGURE_INDEX.md`, `FINAL_CLAIM_AUDIT.md`, `FUTURE_WORK.md`, and
  `PHASE_07_REPORT.md`.
- Added public release docs: `README.md`, `INSTALL.md`, `QUICKSTART.md`, and
  `CHANGELOG.md`.
- Updated `pyproject.toml` package metadata to use `README.md`.
- Added release-package tests covering release reports, documentation,
  traceability closure, configuration isolation, source data, figures, and
  final claim classifications.
- Found and fixed a release-scoped configuration reporting defect: top-level
  `track` metadata is now recognized by `load_config`, and Phase 06 scenario
  TOML declares its track.
- Ran release validation and full unittest suite successfully.
- Preserved final scientific conclusions: local SMI usefulness is supported;
  SMI amplitude prediction and equal-SMI equivalence are contradicted; somatic
  transfer is ensemble-dependent; radius class instability is strongly
  supported; epilepsy scenarios remain exploratory only.

## Phase 08 completed work

- Reviewed the Phase 07 final synthesis, publication guide, figure index, claim
  audit, reproducibility audit, prior synthesis reports, source data, figure
  manifests, bibliography, research ledger, manuscript, master specification,
  and the Phase 08 prompt.
- Reviewed official author instructions for Journal of Computational
  Neuroscience, eNeuro, Journal of Neuroscience, and Frontiers in Computational
  Neuroscience.
- Selected Journal of Computational Neuroscience as the primary target, eNeuro
  as the strong alternative, and Frontiers in Computational Neuroscience as the
  fallback.
- Created `manuscript/main_unblinded.tex`, `manuscript/main_blinded.tex`,
  `manuscript/target_journal.tex`, and
  `manuscript/supplement/supplement.tex` with modular sections, tables,
  figures, references, build wrappers, and validation notes.
- Created `manuscript/CLAIM_TO_SOURCE_LEDGER.csv`,
  `manuscript/NUMERICAL_VERIFICATION_REPORT.md`,
  `manuscript/FIGURE_SOURCE_MANIFEST.csv`, and
  `manuscript/TABLE_SOURCE_MANIFEST.csv`.
- Curated 8 main composite figures, 18 main SVG panel/source files, 9
  supplemental figures, 4 main tables, and 27 bibliography entries.
- Created submission materials under `submission/` and repository-release
  planning materials under `repository/`.
- Added Phase 08 validation tests covering required files, manifests,
  claim-source paths, bibliography/citation consistency, blinded-source
  hygiene, repository-release files, and manuscript-faithful configuration
  isolation.
- Created final archives under `checkpoints/` with adjacent SHA-256 checksum
  files.
- Left public repository creation, license selection, preprint posting, and
  manuscript submission pending explicit author, PI, and institutional
  technology-transfer/intellectual-property approval.

## Post-Phase-08 production/proof pass completed work

- Inspected manuscript entry points, supplement, preamble, manifests, figure
  directories, existing PDFs, journal-target assessment, and publication
  guides.
- Added `manuscript/render_figure_pdfs.py` and generated PDF fallbacks for all
  18 main and 9 supplemental SVG figures.
- Replaced all figure placeholder boxes with direct `\includegraphics`
  environments and subfigure layouts.
- Updated the figure manifest to point to embedded PDF assets while preserving
  SVG/source-data provenance.
- Wrapped main tables to page width without changing table content.
- Tightened blinded and unblinded title-block formatting.
- Updated `build.ps1`, `build.sh`, `Makefile`, and build instructions so figure
  fallbacks are regenerated before compilation.
- Added `manuscript/LATEX_PRODUCTION_AUDIT.md`,
  `manuscript/FIGURE_EMBEDDING_REPORT.md`,
  `manuscript/FORMATTING_FIX_REPORT.md`, and
  `manuscript/PUBLISHER_PROOF_REPORT.md`.
- Added manuscript-local `manuscript/PUBLICATION_GUIDE.md`.
- Verified static figure paths, manifest paths, absence of placeholder macros,
  renderer syntax, focused manuscript-package tests, and the full unittest
  suite.
- Could not regenerate post-edit PDFs because no TeX engine is available on
  PATH; existing PDFs are stale pre-production outputs.

## Revision R2 completed work

- Read the R2 prompt, project state, R0/R1 revision artifacts, manuscript
  sections, supplement sections, bibliography files, claim ledger, numerical
  verification report, and final synthesis/claim reports.
- Verified the R2-added and R2-corrected references through Crossref where
  network access was available.
- Added requested `Magee2000Review` and `MageeCook2000` citations, and verified
  existing `Magee1998` and `Magee1999` HCN/Ih citations without creating
  duplicates.
- Added verified Harnett 2012 spine-neck amplification, Tonnesen 2014/2016
  spine-neck geometry, ModelDB, and FAIR references.
- Corrected `Major2008DendriticSpikes` to
  `Jarsky2005DendriticSpikePropagation` after DOI verification.
- Removed `and others` author placeholders and duplicate Magee HCN records from
  the audited bibliography files.
- Added concise citation placements in Introduction, Methods, Discussion, and
  the separated exploratory supplement only.
- Created all required R2 audit, verification, placement, cleanup, main-text,
  supplement, and handoff reports under `manuscript/revision_v2/`, plus
  `reports/PHASE_R2_REPORT.md`.
- Ran static citation/BibTeX validation, focused manuscript-package tests, and
  the full unittest suite.
- Restart Phase 4 NEURON availability check: bundled Python
  `importlib.util.find_spec('neuron')` -> `None`; NEURON unavailable and no
  NEURON validation result claimed.
- Restart Phase 4 protected-file hash snapshot:
  `results/revision_restart/phase4/phase4_protected_hashes_before.csv` -> 162
  protected files recorded before Phase 4 edits.
- Restart Phase 4 script compile and runner:
  `py_compile scripts\revision_restart\phase4_independent_matrix_benchmark.py
  scripts\revision_restart\phase4_validation_runner.py` -> passed; runner ->
  NEURON unavailable, independent matrix rows=3, DC analytic rows=9, BE-CN
  rows=3, validation summary rows=5, max independent trace difference
  `1.2490009027e-13` mV, max BE-CN head-amplitude difference
  `0.00202710183062` mV.
- Restart Phase 4 required-file/CSV parse check -> missing required files=0;
  independent matrix rows=3, DC analytic rows=9, BE-CN rows=3, validation
  summary rows=5, protected before rows=162, protected after rows=162,
  protected comparison rows=162.
- Restart Phase 4 protected-file hash comparison -> 162 checked, 0 changed or
  missing.
- Restart Phase 4 text hygiene scan over Phase 4 reports and scripts -> 0
  non-ASCII hits.
- Restart Phase 4 full unittest discovery: `$env:PYTHONPATH='src'; &
  '<bundled-python>' -m unittest discover -s tests -p 'test_*.py'` -> 63
  tests passed in 3.370s.
- Restart Phase 4 Git status review: `git status --short` failed because the
  current directory is not recognized as a Git repository.
- Restart Phase 4 checkpoint created at
  `checkpoints/SPINE_restart_phase_4_checkpoint.zip`; see adjacent
  `.sha256` sidecar for digest.

## Revision R3 completed work

- Read the R3 prompt, project state, R2 handoff, statistics/methods gap list,
  manuscript sections, tables, supplement sections, claim ledger, numerical
  verification report, configuration files, and relevant result CSVs.
- Added `scripts/revision_v2/r3_statistical_summaries.py` to create derived
  statistical reporting tables from existing outputs only.
- Generated R3 derived source data under `results/revision_v2/r3/`, including
  predictor intervals, counterexample prevalence intervals, radius uncertainty
  intervals/examples, LHS parameter ranges, active parameter audit, validation
  tolerances, BE/CN comparison, and rounding maps.
- Added required R3 manuscript-facing CSVs:
  `R3_NUMERICAL_CLAIM_REVISION_TABLE.csv`,
  `R3_PREDICTOR_COMPARISON_AUDIT.csv`, and
  `R3_UNCERTAINTY_SPECIFICATION_TABLE.csv`.
- Revised manuscript Results, Methods, abstract, tables, and supplement to
  remove false precision, add interval-aware reporting, define tolerance-class
  validation, specify LHS/bootstrap/CV/radius/class-threshold methods, and add
  an active-parameter supplement table.
- Updated `manuscript/CLAIM_TO_SOURCE_LEDGER.csv`,
  `manuscript/TABLE_SOURCE_MANIFEST.csv`, and
  `manuscript/NUMERICAL_VERIFICATION_REPORT.md` with R3 traceability.
- Created required R3 reports:
  `R3_STATISTICAL_REPORTING_REPORT.md`,
  `R3_METHODS_SPECIFICATION_REPORT.md`,
  `R3_RADIUS_CLASS_AUDIT.md`,
  `R3_ACTIVE_PARAMETER_AUDIT.md`,
  `R3_BE_CN_AND_VALIDATION_AUDIT.md`,
  `R3_NEXT_PHASE_HANDOFF.md`, and `reports/PHASE_R3_REPORT.md`.
- Created `checkpoints/SPINE_phase_R3_checkpoint.zip`.
- Preserved validated model implementation and raw primary simulation source
  data. No R4 figure rebuild, R5 compression, R6 administration, R7 production,
  or R8 review work was started.

## Revision R4 completed work

- Read the R4 prompt, project state, R0-R3 revision artifacts, figure revision
  requirements, manuscript Results/Supplement LaTeX, existing figure manifests,
  available phase/R3/R5.1 source-data CSVs, and runtime constraints.
- Added `scripts/revision_v2/r4_generate_publication_figures.py`, a
  deterministic figure-generation script that reads existing audited CSV
  outputs only.
- Generated 8 main and 9 supplemental publication figures under
  `manuscript/figures_publication/`, with SVG, PDF, and PNG outputs for each.
- Generated R4 source-data snapshots under
  `results/revision_v2/r4/figure_data_snapshots/`.
- Updated main manuscript figure environments to use one composite
  publication PDF per main figure.
- Updated supplement figure includes to use rebuilt publication assets under
  `../figures_publication/`.
- Removed figure-caption source-path footers and moved figure provenance into
  `manuscript/FIGURE_SOURCE_MANIFEST.csv` and
  `manuscript/revision_v2/R4_FIGURE_QUALITY_AUDIT.csv`.
- Wrote required R4 reports:
  `R4_FIGURE_REBUILD_REPORT.md`,
  `R4_FIGURE_QUALITY_AUDIT.csv`,
  `R4_LATEX_FIGURE_INTEGRATION_REPORT.md`,
  `R4_CAPTION_REVISION_LOG.md`,
  `R4_STATIC_SEARCH_AUDIT.md`,
  `R4_NEXT_PHASE_HANDOFF.md`, and `reports/PHASE_R4_REPORT.md`.
- Ran the R4 figure-generation script, Python syntax check, CSV/asset/static
  include validation, and caption-footer static validation successfully.
- Attempted focused pytest validation, but `pytest` is not installed in the
  current Python environment.
- Attempted LaTeX tool discovery, but neither `pdflatex` nor `latexmk` is
  available on PATH.
- Attempted Git status review, but `git` is not available on PATH.
- Created `checkpoints/SPINE_phase_R4_checkpoint.zip` with an adjacent
  `.sha256` checksum file.
- Preserved validated model implementation and raw primary simulation source
  data. No R5 compression, R6 administration, R7 production compile, or R8
  review work was started.

## Revision R5 completed work

- Read the R5 prompt, project state, R0-R4 revision artifacts, manuscript
  entry points, manuscript sections, supplement sections, tables,
  bibliography, claim ledger, numerical verification report, figure manifest,
  table manifest, and publication-figure directory.
- Compressed the abstract, introduction, Methods, Results, Discussion, and
  conclusion into a journal-style narrative centered on SMI as a local
  low-frequency descriptor with explicit boundaries.
- Reorganized Methods into six publication-style subsections and Results into
  seven science-first subsections while retaining all eight R4 main figures in
  order and all four main table inputs.
- Compressed the Discussion from eleven subsections to four major interpretive
  subsections without removing local-usefulness, amplitude-failure,
  somatic-transfer, equal-index-nonequivalence, radius/class-fragility,
  active-state, no-disease-validation, or future-experiment claims.
- Demoted the exploratory perturbation material from a standalone main Results
  subsection to one restrained main-text paragraph; detailed scenario content
  remains in the supplement as exploratory, non-disease-validating stress tests.
- Cleaned journal-facing table/caption wording and supplement terminology
  without changing numerical values, source CSVs, analyses, citations, solver
  behavior, or figure assets.
- Updated figure/table manifest notes only where internal labels remained;
  source paths and provenance were preserved.
- Wrote required R5 artifacts:
  `R5_STRUCTURE_AND_COMPRESSION_REPORT.md`,
  `R5_SECTION_REORGANIZATION_MAP.csv`, `R5_PROSE_CHANGE_LOG.md`,
  `R5_PHASE06_DEMOTION_REPORT.md`, `R5_STATIC_SEARCH_AUDIT.md`,
  `R5_WORD_COUNT_AND_STRUCTURE_AUDIT.md`, `R5_NEXT_PHASE_HANDOFF.md`, and
  `reports/PHASE_R5_REPORT.md`.
- Ran R5 static searches, citation consistency checks, figure include audit,
  focused manuscript-package tests, and full unittest discovery successfully;
  TeX and Git remain unavailable on PATH.
- Created `checkpoints/SPINE_phase_R5_checkpoint.zip` with an adjacent
  `.sha256` checksum file.
- Preserved validated model implementation, raw primary simulation source data,
  primary analyses, and R4 publication figure assets. No R6 administrative
  cleanup, R7 production cleanup, or R8 reviewer simulation was started.

## Revision R6 completed work

- Read the R6 prompt, project state, R0-R5 revision artifacts, manuscript
  administrative sections, blinded/unblinded entry points, supplement entry
  point, submission files, repository planning files, journal-target materials,
  and release/reproducibility reports.
- Removed raw author-confirmation, bracketed blinded-review, repository-link,
  and institutional/IP action-item scaffolding from the manuscript body.
- Replaced manuscript-body administrative placeholders with neutral pending
  review language or polished draft language without inventing funding,
  conflicts, ORCIDs, CRediT roles, repository URLs, licenses, DOIs, or
  approvals.
- Added a polished AI-assistance disclosure draft to the manuscript and created
  separate AI disclosure options for author/journal-policy review.
- Updated data/code availability language for private reviewer access and
  approval-gated public release without creating a public repository or DOI.
- Created or updated submission decision files:
  `AUTHOR_CONFIRMATION_CHECKLIST.md`,
  `IP_AND_REPOSITORY_RELEASE_CHECKLIST.md`,
  `DATA_CODE_AVAILABILITY_OPTIONS.md`, `AI_DISCLOSURE_OPTIONS.md`,
  `COVER_LETTER_DRAFT.md`, `COVER_LETTER.md`,
  `DATA_AND_CODE_AVAILABILITY.md`, `SUBMISSION_READINESS_CHECKLIST.md`, and
  `TITLE_PAGE.md`.
- Created `repository/PRIVATE_REVIEW_REPOSITORY_PLAN.md` for private reviewer
  access planning without publication.
- Wrote required R6 reports:
  `R6_ADMIN_CLEANUP_REPORT.md`, `R6_STATIC_PLACEHOLDER_AUDIT.md`,
  `R6_BLINDING_AND_ADMIN_AUDIT.md`, `R6_NEXT_PHASE_HANDOFF.md`, and
  `reports/PHASE_R6_REPORT.md`.
- Ran static placeholder searches, blinded-source identifier search, focused
  manuscript-package tests, and full unittest discovery successfully; TeX and
  Git remain unavailable on PATH.
- Created `checkpoints/SPINE_phase_R6_checkpoint.zip` with an adjacent
  `.sha256` checksum file.
- Preserved validated model implementation, raw result CSVs, primary analyses,
  figure assets, scientific claims, numerical values, bibliography entries,
  license state, repository visibility, DOI state, preprint state, and
  submission state. No R7 production cleanup or R8 reviewer simulation was
  started.

## Revision R7 completed work

- Read the R7 prompt, project state, R6 handoff/report, manuscript entry
  points, supplement entry point, preamble, metadata, tables, figure assets,
  build wrappers, and submission-package materials.
- Confirmed that no TeX engine, BibTeX tool, latexmk, tectonic, or Perl
  executable is available on PATH or in common program directories in the
  current environment.
- Attempted the R7 all-target build with `manuscript\build.ps1`; it stopped
  cleanly because `pdflatex` is unavailable. No fresh R7 PDFs were generated,
  and stale pre-R7 PDFs in `manuscript/` were not treated as R7 outputs.
- Applied conservative LaTeX-production fixes only: line-breaking safeguards,
  shorter title-block metadata, removal of a visible internal target-journal
  note, improved wrapping for long paths, and supplement title alignment.
- Hardened `manuscript/build.ps1`, `manuscript/build.sh`, and
  `manuscript/Makefile` with explicit unblinded, blinded, target-journal, and
  supplement targets plus R7 output-copy conventions.
- Added repository-level and manuscript-local build instructions:
  `LATEX_BUILD_INSTRUCTIONS.md` and `manuscript/BUILD_INSTRUCTIONS.md`.
- Created `submission/jcns_source_package/` with 51 required source files and
  `submission/jcns_source_package/README_BUILD.txt`.
- Created `submission/compiled_pdfs/README.txt` explaining that compiled R7
  PDFs are pending a TeX-enabled environment.
- Wrote all required R7 reports under `manuscript/revision_v2/` plus
  `reports/PHASE_R7_REPORT.md`.
- Created `checkpoints/SPINE_R7_jcns_source_package.zip` and
  `checkpoints/SPINE_R7_compiled_pdf_package.zip` with adjacent SHA-256
  sidecars.
- Created `checkpoints/SPINE_phase_R7_checkpoint.zip` with an adjacent
  SHA-256 sidecar.
- Ran static LaTeX/source-package validation, static placeholder/path audit,
  blinded-source audit, focused manuscript-package tests, and full unittest
  discovery successfully.
- Preserved validated model implementation, raw result CSVs, primary analyses,
  numerical results, scientific conclusions, figure scientific content,
  license state, repository visibility, DOI state, preprint state, and
  submission state. No R8 hostile-review simulation or later revision phase
  was started.

## Revision Restart Phase 0 completed work

- Read the Restart Phase 0 and Phase 1 prompts, AGENTS instructions, project
  state, task listing, external review source, manuscript entry points,
  metadata, preamble, sections, tables, supplement, bibliography, manifests,
  claim ledger, numerical verification report, R6/R7 reports and handoffs,
  final scientific synthesis, final claim audit, and decision log.
- Determined that Restart Phase 1 could not begin first because its prompt
  depends on Phase 0 artifacts; executed Restart Phase 0 only.
- Created `manuscript/revision_restart/` without overwriting
  `manuscript/revision_v2/`.
- Preserved the external review verbatim in
  `PHASE0_EXTERNAL_REVIEW_SOURCE.md` and verified its SHA-256 hash against the
  supplied review file.
- Created a 30-row issue matrix classifying fatal, major, moderate, and minor
  critiques across scientific framing, analytic theory, statistics,
  computational validation, reproducibility, novelty, figures/tables,
  production, administration, and journal strategy.
- Recommended the analytic divider and residual-domain framing as the next
  organizing thesis.
- Designed the Restart Phase 1-8 architecture and direct Phase 1 handoff.
- Created scientific, PI/institution/release, journal-strategy, and
  administrative decision queues.
- Created analysis requirements for divider residuals, ratio-versus-components,
  attached-versus-omitted `R_in,d`, uncertainty/high-SMI coverage, statistical
  reframing, external validation, release packaging, and figure/PDF cleanup.
- Ran static searches over manuscript source, figure SVG text, and existing
  PDF text using bundled `pypdf`; recorded raw hit CSVs and an interpreted
  static search audit.
- Verified required Phase 0 artifacts, parsed the issue matrix, compared
  protected-file hashes, and attempted Git status review.
- Preserved the Phase 0 boundary: no validated model code, raw result CSVs,
  primary analyses, manuscript scientific prose, tables, bibliography, figures,
  release state, license state, DOI state, public repository, preprint, or
  submission state was modified.

## Revision Restart Phase 1 completed work

- Read the Restart Phase 1 prompt, AGENTS instructions, project state, Phase 0
  handoff/report/artifacts, current manuscript context, claim ledger, numerical
  verification report, final synthesis/audit context, and existing result CSV
  schemas.
- Executed Restart Phase 1 only: analytic divider derivation and residual-domain
  analysis.
- Added deterministic post-processing script
  `scripts/revision_restart/phase1_divider_residual_analysis.py`.
- Inventoried 104 candidate CSVs, found 24 residual-capable files, used 16
  primary source files, and skipped 8 R4 figure-data snapshots to avoid
  duplicate rows.
- Derived `Gamma_h_to_d,divider = 1/(1+SMI)` and computed signed, absolute, and
  relative residuals against observed peak `Gamma_h_to_d`.
- Generated 3718 residual rows, including passive, designed active,
  active-uncertainty, and clearly labeled exploratory Phase 06 rows.
- Found that residuals are predominantly negative: 3680 of 3718 rows have
  observed peak local transfer below the low-frequency divider prediction.
- Recorded overall median absolute residual 0.054751694, RMSE 0.103138355, and
  maximum absolute residual 0.492427929.
- Wrote all required Restart Phase 1 reports under
  `manuscript/revision_restart/` and `reports/PHASE_RESTART_1_REPORT.md`.
- Generated derived data and diagnostic-only SVGs under
  `results/revision_restart/phase1/`.
- Ran static manuscript-language audit over manuscript-facing TeX sources and
  recorded raw hits in `PHASE1_STATIC_LANGUAGE_RAW_HITS.csv`.
- Validated script syntax, reran the deterministic script, parsed generated
  CSVs, verified required artifacts, compared protected-file hashes, and ran
  the full unittest suite with `PYTHONPATH=src`.
- Protected hash comparison checked 157 files and found 0 changed and 0
  missing protected files.
- Created `checkpoints/SPINE_restart_phase_1_checkpoint.zip` with adjacent
  SHA-256 sidecar.
- Git status review was attempted but the Git executable is not available in
  this environment.
- Preserved the Phase 1 boundary: no validated model code, raw result CSVs,
  primary analyses, manuscript scientific prose, manuscript tables,
  publication figures, release state, license state, DOI state, repository
  publication, preprint, or submission state was modified. Restart Phase 2 was
  not begun.

## Revision Restart Phase 2 completed work

- Read the Restart Phase 2 prompt, AGENTS instructions, project state, decision
  log, Phase 0 artifacts, Phase 1 artifacts, manuscript/report context, source
  CSV schemas, scripts, and relevant descriptor/impedance utilities.
- Verified that required Restart Phase 1 artifacts existed before beginning
  Phase 2.
- Executed Restart Phase 2 only: ratio-versus-components and descriptor-value
  analysis.
- Added deterministic post-processing script
  `scripts/revision_restart/phase2_descriptor_value_analysis.py`.
- Generated a 3,718-row standardized descriptor table from the Phase 1
  residual table and existing source CSVs.
- Compared raw SMI, `Gamma_divider = 1/(1+SMI)`, `R_neck`, `R_in,d`,
  log-transformed components, two-variable component OLS models,
  impedance/dynamic descriptors, and synaptic conductance scale where
  available.
- Found that in non-exploratory local-transfer rows, raw SMI and
  `Gamma_divider` share the same rank association, but `Gamma_divider`
  improves scalar CV RMSE relative to raw SMI; the log component pair improves
  over raw SMI but does not beat the analytic divider.
- Found that residuals, amplitude, and somatic transfer require richer
  descriptors: dynamic/impedance descriptors and conductance/component models
  outperform raw SMI for key target-specific summaries.
- Computed a deterministic DC one-port spine-attached versus spine-omitted
  `R_in,d` reconstruction for 3,702 rows; median relative attached-minus-
  omitted difference was -1.528e-6 and 0 class assignments changed.
- Wrote all required Restart Phase 2 reports under
  `manuscript/revision_restart/` and `reports/PHASE_RESTART_2_REPORT.md`.
- Generated derived CSVs and diagnostic-only SVGs under
  `results/revision_restart/phase2/`.
- Ran the Phase 2 script syntax check, executed the script, parsed generated
  CSVs, verified required artifacts, compared protected-file hashes, and ran
  the full unittest suite with `PYTHONPATH=src`.
- Created `checkpoints/SPINE_restart_phase_2_checkpoint.zip` with adjacent
  SHA-256 sidecar.
- Git status review was attempted but failed because the current directory is
  not recognized as a Git repository in this environment.
- Preserved the Phase 2 boundary: no validated model code, raw result CSVs,
  primary analyses, manuscript TeX source, manuscript tables, publication
  figures, release state, license state, DOI state, repository publication,
  preprint, or submission state was modified.

## Revision Restart Phase 3 completed work

- Read the Restart Phase 3 prompt, AGENTS instructions, project state, decision
  log, Restart Phase 0-2 artifacts, manuscript/report context, source CSV
  schemas, scripts, configs, and relevant result tables.
- Verified that required Restart Phase 1 and Phase 2 artifacts existed before
  beginning Phase 3.
- Executed Restart Phase 3 only: statistical reframing, sensitivity-language
  correction, predictor-family language repair, design-permutation checks, and
  high-SMI coverage audit.
- Added deterministic post-processing script
  `scripts/revision_restart/phase3_statistical_reframing.py`.
- Generated Phase 3 outputs under `results/revision_restart/phase3/`:
  interval classification, descriptive sensitivity summaries,
  predictor-family summary, design-permutation checks, and high-SMI coverage
  audit.
- Generated manuscript-facing Phase 3 CSVs:
  `PHASE3_STATISTICAL_LANGUAGE_AUDIT.csv` with 712 language-audit rows and
  `PHASE3_CLAIM_REFRAMING_TABLE.csv` with 8 claim-reframing rows.
- Classified Wilson/binomial intervals over deterministic design fractions as
  inappropriate or misleading, and bootstrap intervals over designed rows as
  deterministic stability ranges rather than confidence intervals.
- Reframed counterexample and class-flip percentages as fractions of sampled
  parameter combinations, not biological prevalence estimates.
- Reframed predictor comparisons by descriptor family rather than exact
  winner labels.
- Ran six deterministic design-permutation checks with seed 202610; all six
  selected observed associations exceeded random within-dataset label
  pairings in 1,000 permutations, with the explicit caveat that these are not
  biological p-values.
- Audited high-SMI coverage and found that the N=768 deterministic uncertainty
  ensemble contains 0 high-SMI rows; Phase 3 recommends scope limitation
  rather than a new high-SMI diagnostic in this phase.
- Wrote all required Restart Phase 3 reports under
  `manuscript/revision_restart/` and `reports/PHASE_RESTART_3_REPORT.md`.
- Ran the Phase 3 script syntax check, executed the script, parsed generated
  CSVs, verified required artifacts, compared protected-file hashes, and ran
  the full unittest suite with `PYTHONPATH=src`.
- Protected hash comparison checked 157 files and found 0 changed and 0
  missing protected files.
- Full unittest discovery ran 63 tests and passed.
- Created `checkpoints/SPINE_restart_phase_3_checkpoint.zip` with adjacent
  SHA-256 sidecar.
- Git status review was attempted but failed because the current directory is
  not recognized as a Git repository in this environment.
- Preserved the Phase 3 boundary: no validated model code, raw result CSVs,
  primary analyses, manuscript TeX source, manuscript tables, publication
  figures, release state, license state, DOI state, repository publication,
  preprint, or submission state was modified.

## Revision Restart Phase 4 completed work

- Read the Restart Phase 4 prompt, AGENTS instructions, project state,
  decision log, Restart Phase 0-3 artifacts, Phase 1-3 reports, passive
  implementation files, manuscript-faithful/plausibility/active configs,
  Phase 02 baseline traces and summary, Phase 1 baseline residuals, and Phase
  2 descriptor recommendations.
- Verified that required Restart Phase 0-3 artifacts existed before beginning
  Phase 4.
- Executed Restart Phase 4 only: external/independent validation and
  computational credibility.
- Checked NEURON availability in the bundled Python runtime; NEURON was
  unavailable (`find_spec('neuron')` returned `None`). No NEURON validation
  result is claimed, and NEURON was not added as a runtime dependency.
- Added `scripts/revision_restart/phase4_independent_matrix_benchmark.py`, a
  separated direct-matrix passive benchmark that independently parses config
  values, computes the double-exponential synaptic waveform, assembles the
  three-node passive matrices, solves the Backward Euler update, and compares
  against existing Phase 02 SPINE trace CSVs.
- Added `scripts/revision_restart/phase4_validation_runner.py`, which checks
  NEURON availability, runs the independent matrix benchmark, runs DC analytic
  checks, runs a bounded BE-vs-CN peak comparison, writes a validation summary,
  and prints concise terminal output.
- Generated Phase 4 outputs under `results/revision_restart/phase4/`:
  `phase4_independent_matrix_benchmark.csv`,
  `phase4_dc_analytic_benchmark.csv`,
  `phase4_be_cn_peak_comparison.csv`, and
  `phase4_validation_summary.csv`.
- Generated diagnostic-only figure
  `results/revision_restart/phase4/diagnostic_figures/phase4_independent_trace_overlay.svg`.
- Independent direct matrix benchmark results: 3 baseline reference rows,
  maximum all-trace absolute voltage difference `1.249000902703301e-13` mV,
  maximum head-amplitude difference `1.4210854715202e-14` mV, and maximum
  local-transfer difference `7.54951656745106e-15`.
- DC analytic benchmark results: closed-form spine-omitted `R_in,d`
  `144.48669201520912` MOhm matched direct solve within
  `2.980232238769531e-14` MOhm; divider predictions were
  `0.9912648179022261`, `0.8970688495921831`, and `0.4306959250822274` for
  low, intermediate, and high cases; attached one-port relative `R_in,d`
  differences were about `-6.6726e-07`.
- BE-vs-CN peak comparison results: maximum differences across the reference
  cases were `0.0020271018306221578` mV for `A_h`,
  `0.000533646319702985` mV for `A_d`,
  `0.00018858397472787392` mV for `A_s`, `0.0004997756786381258` for
  `Gamma_h_to_d`, and `0.00017959782401766322` for `Gamma_h_to_s`.
- Wrote required Restart Phase 4 reports under `manuscript/revision_restart/`
  and `reports/PHASE_RESTART_4_REPORT.md`.
- Ran Phase 4 script syntax checks and the validation runner successfully.
- Parsed all required Phase 4 CSV outputs successfully and verified all
  required Phase 4 files existed.
- Protected hash comparison checked 162 model/raw-result/manuscript-source/
  publication-figure files and found 0 changed or missing protected files.
- Full unittest discovery ran 63 tests and passed.
- Git status review was attempted but failed because the current directory is
  not recognized as a Git repository in this environment.
- Created `checkpoints/SPINE_restart_phase_4_checkpoint.zip` with adjacent
  SHA-256 sidecar.
- Preserved the Phase 4 boundary: no validated model code, raw result CSVs,
  manuscript TeX source, manuscript tables, publication figures, release
  state, license state, DOI state, public repository state, preprint state, or
  submission state was modified.

## Revision Restart Phase 5 completed work

- Read the Restart Phase 5 prompt, AGENTS instructions, project state,
  decision log, old final-release task context, Restart Phase 0-4 artifacts,
  Phase 1-4 restart reports, existing release/readme/repository planning
  documents, package-related ledgers, and repository inventories.
- Executed Restart Phase 5 only: reviewer-access code/data release readiness
  and reproducibility package.
- Added `scripts/revision_restart/phase5_prepare_review_packages.py`, a
  deterministic packaging script that stages blinded and unblinded package
  drafts, writes package documentation, creates manifests, scans the blinded
  package for identifiers, builds ZIP archives, writes SHA-256 sidecars, and
  records protected-file hash comparisons.
- Created `reproducibility_review_package/` as the package-readiness staging
  record.
- Created `submission/reviewer_access_package/blinded_spine_review_package/`
  and `submission/reviewer_access_package/unblinded_internal_release_candidate/`.
- Created package documentation in both package drafts: reviewer/internal
  README, `ENVIRONMENT.md`, `REPRODUCE_CORE_RESULTS.md`, `RUN_TESTS.md`,
  `REGENERATE_FIGURES.md`, `requirements-review.txt`, and
  `environment-review.yml`.
- Created package manifests:
  `submission/reviewer_access_package/blinded_spine_review_package/PACKAGE_MANIFEST.csv`
  and
  `submission/reviewer_access_package/unblinded_internal_release_candidate/PACKAGE_MANIFEST.csv`.
- Generated Phase 5 outputs under `results/revision_restart/phase5/`:
  `phase5_package_summary.csv`, `phase5_blinded_identifier_audit.csv`,
  `phase5_protected_hashes_before.csv`, `phase5_protected_hashes_after.csv`,
  and `phase5_protected_hash_comparison.csv`.
- Wrote required Restart Phase 5 reports under `manuscript/revision_restart/`
  and `reports/PHASE_RESTART_5_REPORT.md`.
- Blinded package result: 275 files, 0 blinded identifier hits, archive
  `submission/reviewer_access_package/SPINE_blinded_reviewer_package_draft.zip`,
  SHA-256 `efaca101ecbd3df262f502f5c24e3b55012cbbf70c06c09d351226eefeaa428c`.
- Unblinded internal package result: 279 files, archive
  `submission/reviewer_access_package/SPINE_unblinded_internal_release_candidate.zip`,
  SHA-256 `42caa289d4d7e45838a67b2de0b9b1f679ea2a8aeec49695a04967bd57cdeaf0`.
- Protected hash comparison checked model/config/result/manuscript-source/
  publication-figure files and found 0 changed or missing protected files.
- Created `checkpoints/SPINE_restart_phase_5_checkpoint.zip` with adjacent
  SHA-256 sidecar.
- Preserved the Phase 5 boundary: no validated model code, raw result CSVs,
  manuscript TeX source, manuscript tables, publication figures, public
  repository state, license state, DOI state, preprint state, or submission
  state was modified.

## Revision Restart Phase 6 completed work

- Read the Restart Phase 6 prompt, AGENTS instructions, project state,
  decision log, old final-release task context, Restart Phase 0-5 artifacts,
  Phase 1-5 restart reports, current manuscript source, current manuscript
  tables, supplement source, references, figure/table manifests, claim ledger,
  numerical verification report, and Phase 5 package outputs.
- Executed Restart Phase 6 only: reviewer-response synthesis,
  availability-language finalization, and manuscript rewrite blueprint.
- Created `manuscript/revision_restart/PHASE6_REVISED_THESIS_AND_CLAIM_ARCHITECTURE.md`
  with the final planning-level revised thesis and tiered claim hierarchy.
- Created `manuscript/revision_restart/PHASE6_TITLE_AND_METRIC_NAME_RECOMMENDATION.md`,
  recommending `load-normalized spine-neck ratio` as the lead term and `SMI`
  only as author-defined shorthand if retained.
- Created
  `manuscript/revision_restart/PHASE6_RESPONSE_TO_EXTERNAL_REVIEW_MATRIX.csv`
  with 30 external-review issues mapped to Phase 1-5 actions, evidence,
  required Phase 7 edits, residual risks, edit locations, and status.
- Created `manuscript/revision_restart/PHASE6_SECTION_REWRITE_BLUEPRINT.md`
  and `manuscript/revision_restart/PHASE6_FIGURE_TABLE_UPDATE_BLUEPRINT.md`
  to direct Phase 7 manuscript source, table, and caption edits.
- Created
  `manuscript/revision_restart/PHASE6_AVAILABILITY_LANGUAGE_FINAL_OPTIONS.md`,
  `manuscript/revision_restart/PHASE6_PRE_SUBMISSION_RISK_REVIEW.md`,
  `manuscript/revision_restart/PHASE6_PHASE7_PROMPT_DRAFT.md`, and
  `manuscript/revision_restart/PHASE6_NEXT_PHASE_HANDOFF.md`.
- Created `reports/PHASE_RESTART_6_REPORT.md`.
- Generated Phase 6 protected-hash baseline under
  `results/revision_restart/phase6/phase6_protected_hashes_before.csv`.
- Parsed the Phase 6 response matrix successfully: 30 rows and 10 columns.
- Verified all required Phase 6 artifacts existed.
- Protected hash comparison checked 286 protected paths and found 0 changed,
  0 missing, and 0 added protected files.
- Full unittest discovery ran 63 tests and passed.
- Git status review was attempted but failed because the current directory is
  not recognized as a Git repository in this environment.
- Created `checkpoints/SPINE_restart_phase_6_checkpoint.zip` with adjacent
  SHA-256 sidecar.
- Preserved the Phase 6 boundary: no validated model code, raw result CSVs,
  manuscript TeX source, manuscript tables, publication figures, public
  repository state, license state, DOI state, preprint state, or submission
  state was modified.

## Revision Restart Phase 7 completed work

- Read the Restart Phase 7 prompt, AGENTS instructions, project state,
  decision log, Restart Phase 0-6 artifacts, Phase 1-5 restart reports,
  current manuscript source, supplement source, tables, manifests, claim
  ledger, numerical verification report, baseline configuration, and relevant
  result CSVs.
- Executed Restart Phase 7 only: controlled manuscript source rewrite around
  the analytic-divider and residual-domain thesis.
- Rewrote manuscript title/metadata, abstract, Introduction, Methods, Results,
  Discussion, Conclusion, Data and Code Availability, and key supplement
  sections.
- Updated Tables 1-4 to include baseline neck geometry, independent
  matrix/DC validation, descriptor-family conclusions, high-SMI uncertainty
  limitations, no NEURON result, and package approval scope.
- Created `scripts/revision_restart/phase7_generate_divider_residual_figure.py`.
- Created new main divider/residual figure assets:
  `manuscript/figures_publication/Fig3_divider_residuals.pdf`,
  `.svg`, and `.png`.
- Generated Phase 7 derived outputs under `results/revision_restart/phase7/`,
  including `phase7_divider_residual_figure_data.csv`,
  `phase7_divider_residual_figure_summary.csv`, protected-hash snapshots,
  static-language hits, blinding scan, and LaTeX log audit.
- Updated `manuscript/CLAIM_TO_SOURCE_LEDGER.csv`,
  `manuscript/FIGURE_SOURCE_MANIFEST.csv`,
  `manuscript/TABLE_SOURCE_MANIFEST.csv`, and
  `manuscript/NUMERICAL_VERIFICATION_REPORT.md`.
- Wrote required Phase 7 reports:
  `manuscript/revision_restart/PHASE7_MANUSCRIPT_REWRITE_REPORT.md`,
  `PHASE7_CLAIM_UPDATE_LOG.csv`, `PHASE7_TABLE_UPDATE_REPORT.md`,
  `PHASE7_FIGURE_UPDATE_REPORT.md`, `PHASE7_STATIC_LANGUAGE_AUDIT.md`,
  `PHASE7_AVAILABILITY_AND_BLINDING_AUDIT.md`,
  `PHASE7_LATEX_STATIC_OR_BUILD_REPORT.md`, and
  `PHASE7_NEXT_PHASE_HANDOFF.md`.
- Wrote high-level report `reports/PHASE_RESTART_7_REPORT.md`.
- Protected hash comparison tracked 189 model/config/result files and found
  0 changed, 0 missing, and 0 added protected files outside Phase 7 outputs.
- CSV parse checks passed for the claim ledger, Phase 7 claim update log,
  figure manifest, table manifest, and Phase 7 derived CSVs.
- Full unittest discovery ran 63 tests and passed.
- Direct LaTeX builds succeeded for `main_unblinded.tex`,
  `main_blinded.tex`, `target_journal.tex`, and `supplement.tex`.
  `latexmk` was present but blocked by missing Perl, so direct
  `pdflatex`/`bibtex` passes were used. Final logs have only one underfull
  path-line warning in each main manuscript variant.
- Static language audit found no visible old Wilson/prevalence/confidence
  interval/best-predictor/Spine Morphology Index/NEURON-validation/clinical
  overclaim wording; remaining hits are only pending/not-claimed availability
  caveats.
- Blinded identifier scan found 0 hits in blinded source.
- Created `checkpoints/SPINE_restart_phase_7_checkpoint.zip` with adjacent
  SHA-256 sidecar.
- Preserved the Phase 7 boundary: no validated solver/model code, configs, raw
  result CSVs, broad primary ensembles, public repository state, license state,
  DOI state, preprint state, or submission state were modified. Manuscript
  TeX, tables, supplement source, ledgers, manifests, and publication figure
  assets were edited intentionally under Phase 7 authorization.

## Revision Restart Phase 8 completed work

- Read the Restart Phase 8 prompt, AGENTS instructions, project state,
  decision log, Restart Phase 6-7 artifacts, external-review response
  artifacts, final manuscript source, supplement source, tables, figure/table
  manifests, claim ledger, numerical verification report, Phase 5 reviewer
  packages, Phase 7 PDFs, and relevant build outputs.
- Executed Restart Phase 8 only: final pre-submission QA, hostile reviewer
  simulation, external-review response audit, static leakage audit, package
  consistency audit, blocker classification, and validation reporting.
- Created `scripts/revision_restart/phase8_final_qa_audit.py` to extract PDF
  text, render PDF pages, audit static language/leakage, parse key CSVs, audit
  LaTeX logs, verify package checksums, check package-current synchronization,
  compare protected model/config/result hashes, and generate the Phase 8
  claim-evidence audit.
- Generated QA outputs under `results/revision_restart/phase8/`, including
  rendered PDF pages, extracted PDF text, PDF metadata, static-language hits,
  CSV parse summaries, LaTeX log audit rows, package checksum and sync audits,
  and protected model/result hash comparisons.
- Rebuilt and inspected `manuscript/main_unblinded.pdf`,
  `manuscript/main_blinded.pdf`, `manuscript/target_journal.pdf`, and
  `manuscript/supplement/supplement.pdf`.
- Made minor production fixes only: removed a visible correspondence
  placeholder from the title block, removed visible internal R4 provenance text
  from Figure 1, reworded Table 4 to avoid "SMI predicts" language, changed
  Figure 8 "prevalence" wording to "design fraction," and cleaned Figure S9
  scenario labeling/layout.
- Wrote required Phase 8 artifacts:
  `PHASE8_PDF_QA_REPORT.md`,
  `PHASE8_EXTERNAL_REVIEW_RESPONSE_AUDIT.md`,
  `PHASE8_HOSTILE_REVIEWER_SIMULATION.md`,
  `PHASE8_CLAIM_EVIDENCE_AUDIT.csv`,
  `PHASE8_STATIC_LANGUAGE_AND_LEAKAGE_AUDIT.md`,
  `PHASE8_REPRODUCIBILITY_PACKAGE_AUDIT.md`,
  `PHASE8_JOURNAL_STRATEGY_RECOMMENDATION.md`,
  `PHASE8_SUBMISSION_BLOCKER_LIST.md`,
  `PHASE8_MINOR_FIX_LOG.md`,
  `PHASE8_BUILD_AND_VALIDATION_REPORT.md`, and
  `PHASE8_NEXT_PHASE_HANDOFF.md`.
- Wrote high-level report `reports/PHASE_RESTART_8_REPORT.md`.
- Final static PDF audit found no old internal phase tags, placeholders, local
  paths, NEURON-validation overclaim, Wilson/confidence/prevalence language,
  "SMI predicts," "best predictor," "Spine Morphology Index," or
  "epileptogenesis" in the rebuilt PDFs.
- Blinded PDF/source identifier scanning found 0 word-boundary hits for the
  unblinded institutional identifiers checked during Phase 8.
- Package checksum audit confirmed that the Phase 5 blinded and unblinded
  archives still match their SHA-256 sidecars. Package synchronization audit
  found that those archives predate the current Phase 7/8 manuscript, figure,
  ledger, and numerical-verification state, so package rebuild is a submission
  blocker before reviewer distribution.
- Protected hash comparison against the Phase 7 model/config/result baseline
  found 189 unchanged protected paths, 0 changed paths, and 0 missing paths.
- Full unittest discovery ran 63 tests and passed.
- Git status review was attempted but failed because the current directory is
  not recognized as a Git repository in this environment.
- Created `checkpoints/SPINE_restart_phase_8_checkpoint.zip` with adjacent
  SHA-256 sidecar.
- Phase 8 verdict: ready for PI/coauthor review, not ready for journal
  submission until reviewer packages are synchronized and final administrative
  metadata/repository/archive/license decisions are resolved.
- Preserved the Phase 8 boundary: no validated model code, raw result CSVs,
  broad primary ensembles, public repository state, license state, DOI state,
  preprint state, or submission state were modified.

## Revision Restart Phase 9 completed work

- Read the Restart Phase 9 prompt, AGENTS instructions, project state,
  decision log, active task context, Phase 8 outputs, current manuscript PDFs
  and source, supplement source/PDF, current ledgers/manifests/numerical
  verification report, Phase 5 package materials, package manifests/checksums,
  package/release decision files, package source materials, and relevant
  results/figures/reports.
- Executed Restart Phase 9 only: final package synchronization, admin metadata
  readiness, and PI/coauthor review package creation.
- Added `scripts/revision_restart/phase9_sync_review_packages.py`, a bounded
  package synchronizer that stages the blinded, unblinded, and PI/coauthor
  packages; writes manifests; creates archives and SHA-256 sidecars; redacts
  blinded identifiers and local paths in staged copies; audits identifiers,
  local paths, package language, package consistency, figure-polish items, and
  protected hashes.
- Rebuilt `submission/reviewer_access_package/blinded_spine_review_package/`
  with 424 manifest rows and created
  `submission/reviewer_access_package/SPINE_blinded_reviewer_package_phase9.zip`
  with SHA-256
  `c91dc922c5a786dafca433dea4f845a2b1a9c9ff6bc859c18c51a002083958bf`.
- Rebuilt
  `submission/reviewer_access_package/unblinded_internal_release_candidate/`
  with 478 manifest rows and created
  `submission/reviewer_access_package/SPINE_unblinded_internal_release_candidate_phase9.zip`
  with SHA-256
  `74a9cebcdbd52d3989025f0d54feeb4e16efc6ef3ff20c843abf6504e5a254c3`.
- Created `submission/pi_coauthor_review_package/` with 22 manifest rows,
  required PI/coauthor forms, current PDFs, response/review summaries, package
  status summary, and created
  `submission/pi_coauthor_review_package/SPINE_PI_COAUTHOR_REVIEW_PACKAGE.zip`
  with SHA-256
  `a0f5f2ce25bd41b9ab49fd830b18a08c248b147ece670ca1c32672b1df28ec3f`.
- Generated Phase 9 QA outputs under `results/revision_restart/phase9/`,
  including package summary, checksum verification, manifest parse summary,
  identifier/local-path audits, package-document language audit,
  package-manuscript consistency audit, figure-polish audit, and protected
  hash comparisons.
- Wrote required Phase 9 reports under `manuscript/revision_restart/` and
  high-level report `reports/PHASE_RESTART_9_REPORT.md`.
- Final audit results: blinded package identifier hits 0, blinded local-path
  hits 0, unblinded local-path hits 0, PI/coauthor local-path hits 0, package
  document risky-language hits 0, and package consistency checks passed.
- Manifest and checksum validation passed for all three archives.
- Protected hash comparison checked 304 model/config/result/manuscript-source/
  figure paths and found 304 unchanged, 0 changed, 0 missing, and 0 added.
- Blinded package unittest discovery ran 57 tests and passed.
- A fresh extraction of the blinded Phase 9 archive ran
  `scripts/revision_restart/phase4_validation_runner.py` successfully, with
  NEURON unavailable and maximum independent-matrix trace difference
  `1.2490009027e-13` mV.
- Full repository unittest discovery ran 63 tests and passed.
- Created `checkpoints/SPINE_restart_phase_9_checkpoint.zip` with adjacent
  SHA-256 sidecar.
- Remaining before journal submission: corresponding author/contact metadata,
  final author/affiliation/ORCID/CRediT/funding/conflict/acknowledgment
  decisions, reviewer access approval, public release/archive/DOI/license
  route, preprint decision, journal target approval, and optional figure polish.
- Preserved the Phase 9 boundary: no validated model code, raw result CSVs,
  broad scientific analyses, public repository state, license state, DOI state,
  preprint state, or submission state were modified.

## Interruption rule

Before stopping or when nearing a usage/context limit:

1. Record completed work.
2. Record exact pending work.
3. Record the last test command and result.
4. Record modified/untracked files.
5. Do not advance the phase status without satisfying its completion criteria.
