# Phase 1 External Empirical Schema Report

## Schema Purpose

`external_summary_measurements_schema.json` locks the shape and controlled vocabulary for the summary-only external empirical dataset. It is designed for a later Route 1 summary/contrast-pole overlay, not for per-spine inference.

## Column Definitions

The full per-column definitions are in:

`data/external_empirical/schema/external_summary_measurements_data_dictionary.csv`

The curated dataset has 54 required columns grouped as:

- Identity/provenance: `row_id`, `source_id`, `citation_short`, `doi`, `dataset_role`, `route1_status`, `data_level`, `extraction_method`, source/provenance references, and `provenance_note`.
- Biological/source metadata: species, preparation, region, cell type, compartment, distance, n fields, and measured/model classification.
- Neck resistance: `R_neck_MOhm`, uncertainty, statistic, and method fields.
- Load/impedance: load value, uncertainty, statistic, method, definition, assumption, and provenance fields.
- Transfer/amplification: attenuation or AR fields and definitions.
- Geometry: neck length/radius/diameter and source fields.
- Route 1 eligibility: summary/per-spine usability, exclusion reason, plot role, and marker group.
- Derived feasibility-only values: source-native `rho_L`, `Gamma_div`, class, and calculation note.

## Controlled Vocabularies

Controlled vocabularies are encoded in the schema JSON for:

- `dataset_role`
- `route1_status`
- `data_level`
- `measured_or_model`
- `R_neck_method`
- `load_method`
- `load_definition`
- `load_provenance`
- `attenuation_definition`
- `recommended_plot_role`
- `recommended_marker_group`
- `rho_L_class_source_native`

No new controlled-vocabulary values were added beyond the Phase 1 prompt.

## Required Versus Optional Columns

All 54 columns are required to exist in `external_summary_measurements.csv`. Individual cell values may be blank when not applicable, but row validation requires core provenance fields and enforces calculation/eligibility rules.

## Data Provenance Rules

- Every curated row must trace to Phase 0.1 source-acquisition and/or extracted-value ledger rows.
- New literature values are not permitted in Phase 1.
- User-prompt-only values are not admitted unless they are present in Phase 0.1 output files.
- Kwon and Cornejo remain nonnumeric unless accepted Phase 0.1 numeric rows exist.

## Load-Provenance Rules

- Popovic measured summary uses `load_provenance = measured_same_source` and `load_definition = Popovic_Zdendrite`.
- Harnett uses `load_provenance = model_reported_same_source` and `load_definition = Harnett_model_Rdend`.
- Assumed/model/proxy loads must not be labeled `measured_same_source`.
- The common-reference SPINE baseline load is not used in Phase 1.

## Per-Spine Claim Blockers

Phase 1 blocks per-spine claims because:

- Phase 0.1 did not machine-recover Harnett native paired measured `R_neck/R_d-EPSC` rows.
- No automated digitization was accepted.
- No row has `data_level = per_spine_measured` or `per_spine_model`.
- Every row has `usable_for_per_spine_route1 = false`.

## Phase 2a Ingestion

Phase 2a should read `data/external_empirical/external_summary_measurements.csv`, filter `usable_for_summary_route1 = true`, and preserve `recommended_marker_group` and `measured_or_model` distinctions. It may recompute source-native rho_L/Gamma as a check, but it should not overwrite provenance labels or silently impute loads.
