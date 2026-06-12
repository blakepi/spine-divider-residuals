# Release Audit

Date: 2026-06-12

- Public repo URL: https://github.com/blakepi/spine-divider-residuals
- Public/private status: public repository URL verified by user for metadata lock.
- Branch: `main` in local staging repository.
- Commit hash: report from `git rev-parse HEAD` in `public_release/spine-divider-residuals` after final local staging commit or after any manual URL/DOI metadata update. The root final report records the hash observed at completion.
- Release tag: `v1.0.0-submission`.
- Release URL: https://github.com/blakepi/spine-divider-residuals/releases/tag/v1.0.0-submission
- Zenodo version DOI: https://doi.org/10.5281/zenodo.20672333
- Zenodo concept DOI: https://doi.org/10.5281/zenodo.20672356
- Code license: MIT (`LICENSE`).
- Data/docs license: CC BY 4.0 (`DATA_LICENSE.md`).
- Manifest: `public_release/spine-divider-residuals/PUBLIC_RELEASE_MANIFEST.csv`.
- Files staged: see `PUBLIC_RELEASE_MANIFEST.csv`; the root final report records exact observed counts at completion.
- Excluded rationale: raw prompts, `.codex/`, tasks, checkpoints, backups, old reviewer packages, generated caches, temporary files, local logs, and historical planning artifacts not needed for reproducibility were excluded from the clean public staging repo.
- Sensitive scan: `.env`, credential, token, and secret path patterns excluded by `.gitignore`; final grep scan should be run before manual push.
- AI/scratch cleanup: public staging keeps concise AI-use disclosure and excludes raw chat/prompt attachments.
