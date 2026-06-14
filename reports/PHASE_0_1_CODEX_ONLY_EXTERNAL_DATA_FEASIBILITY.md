# Phase 0.1 Codex-Only External Data Feasibility

## Executive Verdict

Final classification: **GO_SUMMARY_ONLY**.

Route 1 can proceed under the Codex-only rule only as a conservative summary/contrast-pole overlay. It cannot proceed as a per-spine empirical sample in the current evidence state. No human digitization, manual transcription, or visual point-picking remains required for the summary-only next phase.

## One-Paragraph Rationale

Codex-only acquisition and machine-readable extraction recovered enough source-backed values for a summary-level feasibility dataset: Harnett provides an approximate/model high-isolation anchor with R_neck around 500 MOhm and a model Rdend load proxy of 125 MOhm, while Popovic provides a same-source measured summary contrast with R_neck = 27 +/- 6 MOhm, Zdendrite = 275 +/- 27 MOhm, and AR = 1.10 +/- 0.02 for n = 29 spines. The evidence is not sufficient for GO_PER_SPINE because Harnett native paired measured R_neck/R_d-EPSC rows and the exact expected headline statistics were not recovered from machine-readable sources without figure/table digitization.

## Source Acquisition Summary

- Harnett 2012: DOI/publisher landing HTML acquired; supplementary PDF acquired and converted to text; PMC metadata found; PMC OA package not retrievable.
- Popovic 2015: DOI/publisher HTML acquired; EuropePMC/PDF acquired; supplementary PDF acquired; PDF text provided the strongest numeric extraction.
- Kwon 2017: DOI/Crossref/EuropePMC metadata only; EuropePMC PDF render failed and direct publisher PDF was blocked, so no accepted numeric row.
- Cornejo 2022: DOI/Crossref/EuropePMC metadata only; Science/Unpaywall PDF retrieval was blocked, so this remains contrast-only.
- Zecevic 2023: EuropePMC PDF acquired and converted to text; used only for interpretive divider context.

Detailed acquisition rows are in `results/external_empirical/phase0_1_feasibility/source_acquisition_ledger.csv`.

## Extraction Summary By Source

### Harnett

Recovered machine-readable values:

- R_neck approximate/model value: 500 MOhm.
- Reported amplification range: 1.5 to 45 fold.
- Model load proxy: Rdend = 125 MOhm.
- Model R_neck paired with that proxy: 500 MOhm.
- Model-spine distance from soma: 213 um.
- Long-neck subset count: n = 8 spines from 4 cells.

Not recovered:

- Native paired measured Harnett per-spine R_neck and R_d-EPSC rows.
- Exact reported Harnett mean values expected by the phase prompt, including the around-514 MOhm mean, AR around 49, and around-223 um measured-spine summary.

Conclusion: usable only as a conditional Harnett summary/model load-proxy anchor.

### Popovic

Recovered machine-readable values:

- Measured summary R_neck = 27 +/- 6 MOhm.
- Same-source measured/calculated Zdendrite = 275 +/- 27 MOhm.
- AR = 1.10 +/- 0.02.
- Sample summary: n = 29 spines / 24 cells / 22 animals.
- Representative measured examples: 15/197 MOhm and 29/371 MOhm for R_neck/Zdendrite.
- Calibration-bound R_neck means: 22.5 +/- 4.8 MOhm and 43.7 +/- 9.7 MOhm.
- Model-fit example: R_neck = 40.5 MOhm and Zdendrite = 564 MOhm.

Conclusion: usable as the primary low-isolation summary contrast pole.

### Kwon

Recovered machine-readable values: none accepted for Route 1.

The scripted acquisition recovered metadata but not a primary full text/PDF or supplementary numeric table. Kwon is not plotted and is not used as a numeric rho_L row in this phase.

### Cornejo

Recovered machine-readable values: none accepted for Route 1.

Cornejo remains a voltage-compartmentalization contrast-only target. No paired R_neck or dendritic-load quantity was machine-recovered, so it must not be plotted as a rho_L coordinate.

### Zecevic

Recovered machine-readable context:

- Divider framing: EPSPspine/EPSPdendrite depends on 1 + R_neck/Zdendrite.
- Review-level diffusional R_neck context: 4 to 50 MOhm.

Conclusion: interpretive context only; not primary empirical data.

## Automated Digitization

No automated figure digitization was accepted or used. `automated_digitization_qc.csv` records one not-attempted/not-accepted row per source. The per-spine Harnett figure route remains excluded unless a future phase implements fully scripted axis calibration, point detection, marker-count validation, uncertainty estimation, and QC overlays.

## Measured Versus Assumed Or Imported Values

Measured/same-source summary values:

- Popovic R_neck = 27 +/- 6 MOhm.
- Popovic Zdendrite = 275 +/- 27 MOhm.
- Popovic AR = 1.10 +/- 0.02.

Assumed/model/proxy values:

- Harnett Rdend = 125 MOhm and R_neck = 500 MOhm from supplementary model framing.
- Popovic model-fit R_neck = 40.5 MOhm and Zdendrite = 564 MOhm.

Unavailable or not accepted:

- Harnett native paired measured load/neck rows.
- Kwon numeric R_neck/load rows.
- Cornejo paired R_neck/load rows.

## Load Quantities

- `Zdendrite` in Popovic is treated as a same-source dendritic impedance/load summary calculated from measured parameters.
- `Rdend` in Harnett is treated as a model load proxy, not a measured native R_d-EPSC value.
- Cornejo and Kwon have no accepted load values in Phase 0.1.

## Feasibility Of Later Load-Model Sensitivity

A later Phase 1 can build a summary-only external empirical schema and perform a clearly labeled load-model sensitivity setup. It must separate measured same-source Popovic rows from Harnett model/proxy rows and must not describe the dataset as a per-spine sample.

Preliminary sanity checks are in `preliminary_route1_sanity_checks.csv` and are marked `feasibility_only_not_manuscript_ready`:

- Harnett summary/model proxy: rho_L = 4, Gamma_div = 0.2.
- Popovic measured mean: rho_L = 0.0981818, Gamma_div = 0.910596.
- Popovic model fit: rho_L = 0.0718085, Gamma_div = 0.933002.

## Kill Criteria Checked

- Harnett load or load proxy unrecoverable: not triggered, because a model Rdend proxy was recovered.
- Harnett values require human figure digitization for per-spine analysis: triggered for GO_PER_SPINE only.
- Popovic/Kwon cannot be separated into measured R_neck versus borrowed/assumed load: not triggered for Popovic; Kwon excluded.
- Dataset too thin for summary load-sensitivity overlay: not triggered.
- Human manual extraction required: not triggered for summary-only next phase.
- Environment blocked: not triggered.

## Recommended Next Phase

Proceed to **Phase 1 external empirical schema plus extracted summary dataset**. Do not proceed to per-spine Route 1, final decision-gate plotting, manuscript integration, public release, DOI changes, or submission changes in Phase 0.1.

## Files Created

- `scripts/external_empirical/phase0_1_codex_feasibility.py`
- `data/external_empirical/phase0_1_sources/README.md`
- `data/external_empirical/phase0_1_sources/extracted_text/harnett_nature11554_html.txt`
- `data/external_empirical/phase0_1_sources/extracted_text/popovic_ncomms9436_html.txt`
- `results/external_empirical/phase0_1_feasibility/source_acquisition_ledger.csv`
- `results/external_empirical/phase0_1_feasibility/extracted_value_ledger.csv`
- `results/external_empirical/phase0_1_feasibility/candidate_external_spine_measurements.csv`
- `results/external_empirical/phase0_1_feasibility/dataset_feasibility_matrix.csv`
- `results/external_empirical/phase0_1_feasibility/automated_digitization_qc.csv`
- `results/external_empirical/phase0_1_feasibility/go_no_go_decision.json`
- `results/external_empirical/phase0_1_feasibility/preliminary_route1_sanity_checks.csv`
- `results/external_empirical/phase0_1_feasibility/protected_hashes_after.csv`
- `results/external_empirical/phase0_1_feasibility/protected_hash_comparison.csv`
- `results/external_empirical/phase0_1_feasibility/validation_summary.json`
- `reports/PHASE_0_1_CODEX_ONLY_EXTERNAL_DATA_FEASIBILITY.md`
- `reports/PHASE_0_1_SOURCE_ACQUISITION_LEDGER_README.md`
- `reports/PHASE_0_1_EXTRACTION_LIMITATIONS.md`
- `checkpoints/SPINE_phase_0_1_codex_only_feasibility_checkpoint_20260613_163947.zip`
- `checkpoints/SPINE_phase_0_1_codex_only_feasibility_checkpoint_20260613_163947.zip.sha256`

Pre-existing or acquisition-created raw private files under `data/external_empirical/phase0_1_sources/raw_private/` are deliberately excluded from checkpoint packaging.

## Validation Commands And Results

Commands run:

```powershell
python scripts\external_empirical\phase0_1_codex_feasibility.py --all
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONPATH=(Resolve-Path -LiteralPath 'src').Path; python -m pytest -q -p no:cacheprovider
python scripts\external_empirical\phase0_1_codex_feasibility.py --hash-after --compare-hashes --validate
```

Results:

- CSV parse validation passed for all generated CSVs.
- JSON parse validation passed for `go_no_go_decision.json`.
- Schema validation passed for all required columns.
- Row-level validation passed for extracted values, candidate load provenance, qualitative/contrast usability flags, and automated-digitization QC linkage.
- Protected hash comparison checked 1,630 protected files and found 0 changed/added/missing rows.
- Existing pytest suite passed with exit code 0.

## Protected Files Changed

No protected scientific files changed. The protected hash set excludes docs and includes `src/`, `configs/`, `tests/`, `manuscript/`, `figures/`, selected historical `results/` directories, `submission/nature_neuroscience/`, and `public_release/spine-divider-residuals/`.

The required docs updates are limited to `docs/PROJECT_STATE.md` and `docs/DECISION_LOG.md`.

## Git And Root Status

`C:\Research\SPINE_Codex_Starter` is still not a Git repository, so no Phase 0.1 branch or commit was created. The nested public-release repository under `public_release/spine-divider-residuals` remains dirty on `main` and was not used as the working root.
