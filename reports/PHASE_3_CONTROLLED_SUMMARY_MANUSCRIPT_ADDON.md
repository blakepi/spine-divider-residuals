# Phase 3 Controlled Summary-Level Manuscript Add-On

## Executive Verdict

Phase 3 status: `passed`.

The manuscript source now contains a compact external empirical add-on. The add-on is summary-level only: machine-recoverable Harnett and Popovic summary anchors occupy distinct load-normalized regimes under source-native and bounded common-load calculations. This supports a load-normalization hypothesis for part of the apparent high- versus low-isolation contrast, but it is not a per-spine reanalysis, biological validation, population estimate, or field-controversy resolution.

## Phase 2b Decision Carried Forward

Phase 2b final recommendation was `PROCEED_TO_CONTROLLED_MANUSCRIPT_ADDON`. Phase 3 carried forward the Phase 2b gate without acquiring new sources, digitizing figures, adding rows, broadening simulations, or mutating submission/public-release state.

## Summary-Only Manuscript Scope

The add-on uses only three locked summary-usable rows:

- `harnett_2012_summary_model_anchor`
- `popovic_2015_measured_summary_anchor`
- `popovic_2015_model_fit_reference`

Every Phase 1 row remains `usable_for_per_spine_route1 = false`.

## Manuscript Files Edited

- `manuscript/sections/results.tex`
- `manuscript/sections/methods.tex`
- `manuscript/sections/discussion.tex`
- `manuscript/supplement/supplement.tex`
- `manuscript/supplement/sections/external_summary_anchors.tex`
- `manuscript/CLAIM_TO_SOURCE_LEDGER.csv`
- `manuscript/FIGURE_SOURCE_MANIFEST.csv`

The title and abstract were left unchanged.

## Figure/Table Integration Decision

One supplemental figure was integrated as Figure S10. A main-text figure was not added because the main manuscript already has a full figure set. A table was not added because the Phase 2b figure more compactly displays the divider placement, class grid, and threshold-load logic while the caption preserves the required caveats.

## Exact Claims Added

- Summary-level external anchors occupy distinct `rho_L` regimes under source-native calculations.
- Harnett model/summary anchor remains high under fixed/recovered common loads.
- Popovic measured summary remains low under fixed/recovered common loads and its source-reported uncertainty envelope remains low.
- Popovic model-fit remains low or intermediate and never high under bounded common-load calculations.
- External transfer ratios are proxy-only compatibility checks and not SPINE residuals.

## Exact Caveats Added

- The add-on uses summary-level external data, not paired per-spine Harnett measured rows.
- Harnett is a model/summary anchor, not recovered paired measured per-spine data.
- Popovic measured and Popovic model-fit rows are kept separate.
- Kwon and Cornejo remain context/exclusion rows without accepted paired `R_neck`/load coordinates.
- Transfer ratios are compatibility proxies only and not SPINE residuals.
- The add-on is not a per-spine reanalysis, not biological validation, not a prevalence estimate, and not a controversy resolution.

## What Was Not Claimed

Phase 3 did not claim per-spine empirical validation, population prevalence, biological validation of SPINE, recovery of native paired Harnett measured rows, resolution of the Harnett/Popovic/Kwon/Cornejo controversy, or exact external residual analysis.

## Kwon/Cornejo Handling

Kwon and Cornejo remain context/exclusion rows. They are cited only to preserve the existing mixed-literature framing and are not plotted as numeric `rho_L` coordinates.

## Transfer-Proxy/Residual Handling

Popovic transfer ratios were treated only as proxy compatibility checks. No external transfer proxy was converted into a SPINE residual, and all transfer rows retain `residual_allowed = false`.

## Files Created

- `scripts/external_empirical/phase3_integrate_summary_manuscript_addon.py`
- `results/external_empirical/phase3_manuscript_addon/*`
- `manuscript/supplement/sections/external_summary_anchors.tex`
- `manuscript/supplement/figures/FigS10_external_summary_load_sensitivity.svg`
- `manuscript/supplement/figures_pdf/FigS10_external_summary_load_sensitivity.pdf`
- `manuscript/figures_publication/FigS10_external_summary_load_sensitivity.svg`
- `manuscript/figures_publication/FigS10_external_summary_load_sensitivity.png`
- `manuscript/figures_publication/FigS10_external_summary_load_sensitivity.pdf`
- `reports/PHASE_3_CONTROLLED_SUMMARY_MANUSCRIPT_ADDON.md`
- `reports/PHASE_3_MANUSCRIPT_INTEGRATION_REPORT.md`
- `reports/PHASE_3_STATIC_LANGUAGE_AUDIT.md`
- `reports/PHASE_3_CLAIM_LEDGER_AND_MANIFEST_AUDIT.md`
- `reports/PHASE_3_BUILD_AND_VALIDATION_REPORT.md`
- `reports/PHASE_3_NEXT_PHASE_HANDOFF.md`

## Validation Commands And Results

- `python scripts\external_empirical\phase3_integrate_summary_manuscript_addon.py --hash-before`
- `python scripts\external_empirical\phase3_integrate_summary_manuscript_addon.py --integrate --hash-after --compare-hashes --validate`
- Exact fallback LaTeX build commands are recorded in `reports/PHASE_3_BUILD_AND_VALIDATION_REPORT.md` and `results/external_empirical/phase3_manuscript_addon/phase3_latex_build_audit.csv`.
- `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src`, `python -m pytest -q -p no:cacheprovider` passed with exit code 0.

## Protected Core Hash Comparison

Protected core comparison checked 1,325 files and found `unchanged = 1325`, with zero changed, added, or removed protected-core files.

## Manuscript Changed-Files Audit

The manuscript hash comparison recorded `unchanged = 303`, `changed = 6`, and `added = 6`. All changed/added manuscript files are classified in `results/external_empirical/phase3_manuscript_addon/phase3_changed_files_manifest.csv`.

## Git/Root Status

`git status --short --branch` failed at `C:\Research\SPINE_Codex_Starter` because the workspace root is not a Git repository. The nested public-release repository remains dirty on `main` and was not used as the working root. No commit was possible.

## Checkpoint Path And SHA-256

Checkpoint path: `checkpoints/SPINE_phase_3_controlled_summary_manuscript_addon_checkpoint_20260613_180700.zip`.

Checkpoint SHA-256: `734CC69378C1EB57A8FE575CFB95A69142F1A11B2F9B8178AD96C2238B8B8A15`.

Report-completeness checkpoint path: `checkpoints/SPINE_phase_3_controlled_summary_manuscript_addon_checkpoint_20260613_181500.zip`.

Report-completeness checkpoint SHA-256: `8D1574B8DFD75244BD36C3C874C9796239F42F8E69D64D42C7D837632B32F7E8`.
