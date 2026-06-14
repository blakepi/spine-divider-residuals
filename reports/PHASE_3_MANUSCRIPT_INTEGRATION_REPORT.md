# Phase 3 Manuscript Integration Report

## Results Integration

Inserted a compact paragraph after the fixed-load and matched-neck load-normalization result in `manuscript/sections/results.tex`. The paragraph states the Codex-only gate, the three summary-usable rows, the source-native separation, the bounded common-load separation, the Popovic uncertainty envelope, and the transfer-proxy limitation.

## Methods Integration

Inserted `External summary-anchor decision gate` in `manuscript/sections/methods.tex`. The subsection documents the locked Phase 1 dataset, the no-manual/no-digitization/no-new-source rule, row eligibility, source-native formulas, load models, class thresholds, threshold-load formulas, uncertainty propagation, Kwon/Cornejo exclusion status, and proxy-only transfer handling.

## Discussion/Limitations Integration

Inserted one limitation paragraph in `manuscript/sections/discussion.tex`. It frames the external anchors as motivation for reporting dendritic load with neck resistance, while explicitly rejecting per-spine inference, biological validation, prevalence estimation, controversy resolution, and SPINE residuals from transfer proxies.

## Abstract/Conclusion Decision

The abstract and conclusion were left unchanged. The Phase 3 add-on is deliberately narrow and supplemental; changing the abstract risked overstating the external-data result.

## Figure/Table Placement

Figure S10 was integrated in the supplement using `manuscript/supplement/sections/external_summary_anchors.tex`. The Phase 2b figure was copied under a new manuscript name rather than overwriting any existing figure. No table was integrated.

## Citation Changes

No new bibliography entries were added. Existing citations were sufficient:

- `Harnett2012SpineAmplification`
- `Popovic2015`
- `Kwon2017`
- `Cornejo2022`
- `Zecevic2023`

The citation audit passed in `results/external_empirical/phase3_manuscript_addon/phase3_citation_audit.csv`.

## Ledger/Manifest Updates

- `manuscript/CLAIM_TO_SOURCE_LEDGER.csv` gained eight Phase 3 claim/caveat rows.
- `manuscript/FIGURE_SOURCE_MANIFEST.csv` gained the Figure S10 provenance row.
- `results/external_empirical/phase3_manuscript_addon/phase3_manifest_updates.csv` records manuscript text, figure asset, claim ledger, and figure manifest updates.

## Rationale For Omitted Candidate Text From Phase 2b

The Phase 2b draft contained fuller explanatory language and optional table logic. Phase 3 omitted the longer draft language to keep the manuscript add-on compact, avoid a validation-strength tone, avoid repeating existing divider/residual framing, and prevent the summary-only external data from dominating the main manuscript. The diagnostic grid details were kept in Figure S10 and the methods paragraph rather than expanded into a separate main-text subsection.
