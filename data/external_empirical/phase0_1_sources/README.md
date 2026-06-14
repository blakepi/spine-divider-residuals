# Phase 0.1 External Empirical Sources

This directory contains source materials and extracted text used only for the
Codex-only external data feasibility gate.

- `raw_private/` stores locally acquired publisher PDFs/HTML for private
  feasibility extraction. These files are excluded from checkpoints and should
  not be treated as public/reviewer artifacts.
- `extracted_text/` stores text derived programmatically from local HTML/PDF
  files, usually via `pdftotext` or the Phase 0.1 ledger script.
- `supplements/`, `model_repositories/`, and `automated_digitization_qc/` are
  reserved for source-specific supplemental or QC artifacts.

The public/reviewer-safe artifacts for this phase are the ledgers under
`results/external_empirical/phase0_1_feasibility/` and the reports under
`reports/`.
