# Final Submission QA Report

Date: 2026-06-12

## Build and package status

- Nature package directory: `submission/nature_neuroscience/`
- Public release staging directory: `public_release/spine-divider-residuals/`
- Local staging commit: recorded in final response and in `submission/final/LOCAL_STAGING_COMMIT.txt`
- Public release manifest: see `PUBLIC_RELEASE_MANIFEST.csv`; the root final report records exact observed counts at completion.
- Main manuscript DOCX: not created: pandoc not available on PATH
- Cover letter DOCX: created
- Cover letter PDF: created
- Title page DOCX: created
- Pandoc: not available on PATH
- LibreOffice/soffice DOCX render QA: not available on PATH

## Nature audit

- Abstract word count: 139 / 150.
- Main text word count: 2471 / 4,500 target by static TeX stripping.
- Online Methods word count: 1060.
- Display items: 8 total (7 figures, 1 table).
- Author metadata: present.
- Funding: "This work received no external funding."
- Competing interests: "The authors declare no competing interests."
- Ethics: mathematical/computational modeling only; no new human or animal experiments.
- Data availability: present.
- Code availability: present.
- ORCID: present for both authors.
- Corresponding author: Alberto Musto, MD, PhD.
- AI-use disclosure: present.
- Acknowledgments placeholder: absent from unblinded main manuscript.

## Scientific claim audit

- No NEURON validation is claimed.
- Deterministic fractions are not presented as biological prevalence.
- N=768 high-SMI uncertainty limitation remains explicit.
- SMI is framed as an author-defined compact coordinate, not a field-standard universal descriptor.

## Remote release status

- Repository URL: https://github.com/blakepi/spine-divider-residuals
- GitHub release: https://github.com/blakepi/spine-divider-residuals/releases/tag/v1.0.0-submission
- Zenodo version DOI: https://doi.org/10.5281/zenodo.20672333
- Zenodo concept DOI: https://doi.org/10.5281/zenodo.20672356
