# Zenodo DOI Action Required

A Zenodo DOI was not minted because this local environment had no authenticated GitHub CLI on PATH and no verified Zenodo integration/token. No DOI has been invented.

## Manual steps

1. Push `public_release/spine-divider-residuals` to a public GitHub repository named `spine-divider-residuals`.
2. Confirm `README.md`, `LICENSE`, `DATA_LICENSE.md`, `CITATION.cff`, `.zenodo.json`, `REPRODUCIBILITY.md`, and `PUBLIC_RELEASE_MANIFEST.csv` are present.
3. In Zenodo, enable GitHub archiving for the repository.
4. Create GitHub release `v1.0.0-submission`.
5. Wait for Zenodo to archive the release and mint a DOI.
6. Record the exact DOI, Zenodo URL, release tag, commit hash, and archive checksum.
7. Update `README.md`, `CITATION.cff`, `.zenodo.json`, manuscript Data Availability, manuscript Code Availability, `submission/final/RELEASE_AUDIT.md`, and `submission/final/SUBMISSION_PORTAL_FIELD_GUIDE.md`.
8. Commit and push the DOI metadata update.
