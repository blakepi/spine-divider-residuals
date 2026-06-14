# Phase 0.1 Source Acquisition Ledger README

## Purpose

The Phase 0.1 ledgers document what Codex could acquire and extract without human digitization, manual transcription, or visual point-picking.

## `source_acquisition_ledger.csv`

Each row records one attempted acquisition route for a target source.

- `source_id`: stable short identifier used across Phase 0.1 tables.
- `citation_short`: human-readable citation label.
- `doi`: DOI for the target source.
- `role`: planned Route 1 role, such as gold anchor, low-isolation contrast, or interpretive review.
- `attempted_url_or_identifier`: DOI, PMCID, publisher URL, EuropePMC route, or other identifier that was attempted.
- `acquisition_route`: route category from the phase prompt, such as DOI landing page, PMC, publisher PDF, supplement, or metadata.
- `acquisition_status`: controlled status: acquired, metadata_only, blocked_network, blocked_paywall, not_found, failed, or skipped_out_of_scope.
- `local_path`: relative path to a local file when one was acquired.
- `content_type`: file or response type when known.
- `license_or_access_note`: short access/licensing note and checkpoint handling note.
- `sha256`: SHA-256 of the local acquired file when present.
- `acquired_datetime_local`: local timestamp for successful acquisition or metadata recording.
- `failure_reason`: exact failure reason for failed or blocked routes.
- `notes`: concise explanation of how the row affects feasibility.

## `extracted_value_ledger.csv`

Each row records one extracted value or one explicit not-recoverable value.

- `source_id`, `citation_short`: join keys back to the acquisition ledger.
- `dataset_role`: source role in the empirical pivot.
- `data_level`: per-spine, summary, model, reported range, contrast-only, qualitative-only, or unavailable.
- `figure_table_or_section`: source location for the extracted value.
- `page_or_location`: local text or source location cue.
- `field_name`: stable field name for the extracted quantity.
- `value_raw`: source-scale value as recorded for provenance.
- `value_numeric`: normalized numeric value when available.
- `unit`: normalized unit, usually MOhm, um, fold, or ratio.
- `statistic_type`: mean, SEM, range endpoint, n, qualitative, or not_applicable.
- `uncertainty_value`, `uncertainty_unit`: uncertainty when machine-readable.
- `n`: sample size or source n statement when available.
- `extraction_method`: controlled extraction label from the phase prompt.
- `extraction_script_or_command`: script or command used for the row.
- `source_local_path`: relative path to source text or source file when retained locally.
- `source_quote_short`: short numeric/source-context cue, kept brief to avoid copying long copyrighted text.
- `confidence`: high, medium, low, or rejected.
- `provenance_note`: why the row is or is not useful.
- `usable_for_route1`: true, false, or conditional.

## Raw-Source Policy

`raw_private/` contains local private feasibility copies and is not included in checkpoints. Checkpoints include only ledgers, reports, source README, scripts, docs updates, and hashes.
