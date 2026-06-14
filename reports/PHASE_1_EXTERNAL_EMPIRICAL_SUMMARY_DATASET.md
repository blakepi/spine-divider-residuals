# Phase 1 External Empirical Summary Dataset

## Executive Summary

Phase 1 completed the external empirical summary dataset and schema lock. The governing Phase 0.1 result is `GO_SUMMARY_ONLY`, so this phase curated source-reported summary/model/context rows only. It did not create a final decision-gate figure, run a load-model sensitivity sweep, rewrite manuscript source, or change validated model code/configs/results/figures/submission materials.

The curated dataset contains 7 rows. Three rows are usable for a later summary Route 1 overlay:

- `harnett_2012_summary_model_anchor`
- `popovic_2015_measured_summary_anchor`
- `popovic_2015_model_fit_reference`

No row is usable for per-spine Route 1.

## GO_SUMMARY_ONLY Constraint

Phase 0.1 found that Codex-only acquisition/extraction supports a conservative summary/contrast-pole empirical overlay, not a per-spine empirical reanalysis. Phase 1 therefore blocks claims of measured Harnett paired per-spine rows, population prevalence, controversy resolution, or biological validation of SPINE.

## What Phase 1 Curated

Created:

- `data/external_empirical/schema/external_summary_measurements_schema.json`
- `data/external_empirical/schema/external_summary_measurements_data_dictionary.csv`
- `data/external_empirical/external_summary_measurements.csv`
- `data/external_empirical/external_summary_source_ledger.csv`
- `data/external_empirical/external_summary_exclusion_ledger.csv`
- `results/external_empirical/phase1_summary_dataset/phase1_native_summary_calculations.csv`
- `results/external_empirical/phase1_summary_dataset/phase1_dataset_validation.csv`
- `results/external_empirical/phase1_summary_dataset/phase1_dataset_summary.json`

The dataset is built only from Phase 0.1 candidate/extraction/acquisition ledgers.

## What Phase 1 Did Not Do

- Did not create the final decision-gate figure.
- Did not run the full load-model sensitivity sweep.
- Did not add a common-reference SPINE baseline load.
- Did not pool measured and model rows.
- Did not infer missing loads.
- Did not perform human or automated figure digitization.
- Did not add per-spine rows.
- Did not update manuscript source, public-release metadata, DOI records, or Nature submission packages.

## Source-By-Source Curated Rows

### Harnett 2012

Rows:

- `harnett_2012_summary_model_anchor`: summary/model high-isolation anchor with `R_neck = 500 MOhm` and model `Rdend = 125 MOhm`.
- `harnett_2012_long_neck_subset_context`: context-only row for long-neck subset `n_spines = 8`, `n_cells = 4`; not plotted.

The Harnett numeric row is explicitly model/proxy, not native measured paired load/neck data.

### Popovic 2015

Rows:

- `popovic_2015_measured_summary_anchor`: measured summary anchor with `R_neck = 27 +/- 6 MOhm`, `Zdendrite = 275 +/- 27 MOhm`, `AR = 1.10 +/- 0.02`, `n = 29 spines / 24 cells / 22 animals`.
- `popovic_2015_model_fit_reference`: model-fit reference with `R_neck = 40.5 MOhm` and `Zdendrite = 564 MOhm`.

Measured summary and model-fit rows are intentionally separate.

### Kwon 2017

Row:

- `kwon_2017_excluded_no_numeric_row`: excluded/context row. No accepted numeric Route 1 row was available from Phase 0.1.

### Cornejo 2022

Row:

- `cornejo_2022_contrast_only_no_rho_coordinate`: contrast-only row. No paired `R_neck`/load values were recovered, so it has no rho_L coordinate.

### Zecevic 2023

Row:

- `zecevic_2023_interpretive_context`: interpretive context row only. It is not primary empirical Route 1 data.

## Source-By-Source Exclusions

Exclusion ledger rows:

- Harnett native per-spine paired measured `R_neck/R_d-EPSC` rows: excluded because Phase 0.1 did not machine-recover them.
- Kwon numeric Route 1 row: excluded because Phase 0.1 was metadata-only/blocked and accepted no numeric row.
- Cornejo rho_L coordinate: excluded because no paired `R_neck`/load was recovered.
- Figure-digitized rows: excluded because Phase 0.1 accepted no automated digitization with QC.

## Native rho_L / Gamma_div Calculations

These are source-native feasibility calculations only:

| row_id | rho_L_source_native | Gamma_div_source_native | class |
|---|---:|---:|---|
| `harnett_2012_summary_model_anchor` | 4 | 0.2 | `high_gte_0p75` |
| `popovic_2015_measured_summary_anchor` | 0.0981818182 | 0.910596026 | `low_lt_0p25` |
| `popovic_2015_model_fit_reference` | 0.0718085106 | 0.933002481 | `low_lt_0p25` |

Rows lacking both `R_neck_MOhm` and `load_value_MOhm` are marked `not_calculated`.

## Measured, Model, Context Separation

- Measured summary: Popovic measured summary row only.
- Model/proxy summary: Harnett model/proxy anchor and Popovic model-fit reference.
- Context/excluded: Harnett long-neck subset count, Kwon, Cornejo, and Zecevic rows.

This separation is encoded in `measured_or_model`, `load_assumed`, `load_provenance`, `recommended_plot_role`, and `usable_for_summary_route1`.

## Why This Remains Summary-Only

The dataset has no per-spine rows, no accepted figure-digitized rows, and no Harnett native paired measured load/neck rows. All rows have `usable_for_per_spine_route1 = false`.

## Readiness For Phase 2a

Phase 2a may ingest `external_summary_measurements.csv` and build a summary/contrast-pole decision-gate overlay. It should plot Harnett model/summary and Popovic measured/model rows separately and keep Kwon/Cornejo as excluded/contextual unless future machine-readable numeric rows are accepted.

## Remaining Scientific Limits

- Harnett load is a model/proxy load, not native measured `R_d-EPSC`.
- Popovic is summary-level, not per-spine table data.
- Kwon and Cornejo have no accepted numeric Route 1 coordinates.
- No source supports population prevalence inference in this dataset.
- The source-native rho_L values are feasibility calculations, not inferential statistics.

## Files Created

- `scripts/external_empirical/phase1_build_summary_dataset.py`
- `data/external_empirical/schema/external_summary_measurements_schema.json`
- `data/external_empirical/schema/external_summary_measurements_data_dictionary.csv`
- `data/external_empirical/external_summary_measurements.csv`
- `data/external_empirical/external_summary_source_ledger.csv`
- `data/external_empirical/external_summary_exclusion_ledger.csv`
- `results/external_empirical/phase1_summary_dataset/phase1_native_summary_calculations.csv`
- `results/external_empirical/phase1_summary_dataset/phase1_dataset_validation.csv`
- `results/external_empirical/phase1_summary_dataset/phase1_dataset_summary.json`
- `results/external_empirical/phase1_summary_dataset/protected_hashes_before.csv`
- `results/external_empirical/phase1_summary_dataset/protected_hashes_after.csv`
- `results/external_empirical/phase1_summary_dataset/protected_hash_comparison.csv`
- `reports/PHASE_1_EXTERNAL_EMPIRICAL_SUMMARY_DATASET.md`
- `reports/PHASE_1_EXTERNAL_EMPIRICAL_SCHEMA_REPORT.md`
- `reports/PHASE_1_NEXT_PHASE_HANDOFF.md`

## Validation Commands And Results

Commands run:

```powershell
python scripts\external_empirical\phase1_build_summary_dataset.py --build
python scripts\external_empirical\phase1_build_summary_dataset.py --hash-after --compare-hashes --validate
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONPATH=(Resolve-Path -LiteralPath 'src').Path; python -m pytest -q -p no:cacheprovider
python scripts\external_empirical\phase1_build_summary_dataset.py --hash-after --compare-hashes --validate
```

Results:

- Phase 0.1 gate validation passed.
- Schema JSON parsed and contained all 54 required columns.
- Data dictionary covered all 54 curated dataset columns.
- Controlled-vocabulary checks passed.
- Row-level checks passed, including no per-spine data levels and `usable_for_per_spine_route1 = false` for every row.
- Native rho_L/Gamma calculation checks passed.
- Existing pytest suite passed with exit code 0.

## Protected Hash Comparison

Protected hash comparison checked 1,630 files and found 0 changed/added/missing rows after the test suite.

## Git / Root Status

The workspace root remains not a Git repository, so no branch or commit was created. The nested public-release mirror under `public_release/spine-divider-residuals` remains dirty and was not used as the working root.

## Checkpoint

Checkpoint path:

`checkpoints/SPINE_phase_1_external_empirical_summary_dataset_checkpoint_20260613_165522.zip`

The exact SHA-256 is written in the adjacent `.sha256` sidecar after archive creation.
