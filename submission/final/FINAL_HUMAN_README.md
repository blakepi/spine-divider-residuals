# Final Human README

This finalization created a Nature Neuroscience unblinded submission package, a clean public-release staging repository, and final QA/release audit reports.

## Review first

- Manuscript PDF: `submission/nature_neuroscience/main_unblinded.pdf`
- Source ZIP: `submission/nature_neuroscience/source_files.zip`
- Cover letter: `submission/nature_neuroscience/cover_letter.docx` and `.pdf`
- Supplement: `submission/nature_neuroscience/supplement.pdf`
- Final QA: `submission/final/FINAL_SUBMISSION_QA_REPORT.md`
- Release audit: `submission/final/RELEASE_AUDIT.md`

## Manual actions

- GitHub CLI was not available on PATH; push `public_release/spine-divider-residuals` manually or install/authenticate `gh`.
- Local staging commit: run `git rev-parse HEAD` in `public_release/spine-divider-residuals` after any final manual metadata update. The final response records the hash observed at completion.
- Zenodo DOI was not minted. Follow `submission/final/ZENODO_DOI_ACTION_REQUIRED.md`.
- After a real public GitHub URL and Zenodo DOI exist, update `README.md`, `CITATION.cff`, `.zenodo.json`, manuscript Data/Code Availability, and the portal field guide.
