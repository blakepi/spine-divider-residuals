# Release Audit

Date: 2026-06-12

- Public repo URL: manual action required; not invented.
- Public/private status: local public-release staging prepared; remote public status not verifiable without authenticated GitHub upload.
- Branch: `main` in local staging repository.
- Commit hash: report from `git rev-parse HEAD` in `public_release/spine-divider-residuals` after final local staging commit or after any manual URL/DOI metadata update. The root final report records the hash observed at completion.
- Release tag: intended `v1.0.0-submission`.
- Release URL: manual action required.
- Zenodo DOI: manual action required; no DOI minted or claimed.
- Code license: MIT (`LICENSE`).
- Data/docs license: CC BY 4.0 (`DATA_LICENSE.md`).
- Manifest: `public_release/spine-divider-residuals/PUBLIC_RELEASE_MANIFEST.csv`.
- Files staged: 478.
- Excluded rationale: raw prompts, `.codex/`, tasks, checkpoints, backups, old reviewer packages, generated caches, temporary files, local logs, and historical planning artifacts not needed for reproducibility were excluded from the clean public staging repo.
- Sensitive scan: `.env`, credential, token, and secret path patterns excluded by `.gitignore`; final grep scan should be run before manual push.
- AI/scratch cleanup: public staging keeps concise AI-use disclosure and excludes raw chat/prompt attachments.
