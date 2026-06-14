# Phase 3 Build And Validation Report

## Script Validation

`scripts/external_empirical/phase3_integrate_summary_manuscript_addon.py` was used to capture hashes, copy the selected Figure S10 assets, compare before/after hashes, generate Phase 3 audit CSV/JSON files, and write validation summaries.

Primary script commands:

```powershell
python scripts\external_empirical\phase3_integrate_summary_manuscript_addon.py --hash-before
python scripts\external_empirical\phase3_integrate_summary_manuscript_addon.py --integrate --hash-after --compare-hashes --validate
```

Final status: `passed`.

## CSV/JSON Parse Validation

Phase 3 CSV/JSON artifacts were written under `results/external_empirical/phase3_manuscript_addon/`. The validation summary JSON reports `overall_status = passed`. The gate, claim, manifest, static-language, citation, LaTeX, changed-file, protected-core hash, and manuscript-hash audit files were generated and parsed during validation.

## Manuscript Source Validation

The changed-files manifest classified all expected manuscript changes:

- results text
- methods text
- discussion limitation text
- supplemental include update
- supplemental Figure S10 section
- supplemental/publication Figure S10 assets
- claim ledger update
- figure manifest update

No abstract, title, equation, parameter, model-code, config, or raw-result changes were made.

## Citation Validation

Existing bibliography entries were used for Harnett, Popovic, Kwon, Cornejo, and Zecevic. `phase3_citation_audit.csv` passed with both bibliography entries and manuscript citations present. No new source acquisition or bibliography expansion was required.

## LaTeX Build/Static Validation

The bundled LaTeX helper was attempted first from `C:\Users\gbp34\.codex\plugins\cache\openai-bundled\latex\0.2.2`, but local MiKTeX `latexmk` requires a Perl script engine that is not installed. The exact attempted helper commands were:

```powershell
python scripts\compile_latex.py C:\Research\SPINE_Codex_Starter\manuscript\main_unblinded.tex --json
python scripts\compile_latex.py C:\Research\SPINE_Codex_Starter\manuscript\main_blinded.tex --json
python scripts\compile_latex.py C:\Research\SPINE_Codex_Starter\manuscript\supplement\supplement.tex --json
```

The project was then built with the following exact fallback command block from `C:\Research\SPINE_Codex_Starter`:

```powershell
$ErrorActionPreference='Stop'
$env:MIKTEX_ASSUME_YES='1'
function Build-Tex($dir, $name) {
  Push-Location $dir
  try {
    pdflatex -interaction=nonstopmode -halt-on-error $name
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $base = [System.IO.Path]::GetFileNameWithoutExtension($name)
    bibtex $base
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    pdflatex -interaction=nonstopmode -halt-on-error $name
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    pdflatex -interaction=nonstopmode -halt-on-error $name
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  } finally {
    Pop-Location
  }
}
Build-Tex 'C:\Research\SPINE_Codex_Starter\manuscript' 'main_unblinded.tex'
Build-Tex 'C:\Research\SPINE_Codex_Starter\manuscript' 'main_blinded.tex'
Build-Tex 'C:\Research\SPINE_Codex_Starter\manuscript\supplement' 'supplement.tex'
```

After adding `\FloatBarrier` to keep Figure S10 attached to its supplemental section, the supplement was rebuilt with:

```powershell
$ErrorActionPreference='Stop'
$env:MIKTEX_ASSUME_YES='1'
Push-Location 'C:\Research\SPINE_Codex_Starter\manuscript\supplement'
try {
  pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  bibtex supplement
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {
  Pop-Location
}
```

The target-journal variant was built with:

```powershell
$ErrorActionPreference='Stop'
$env:MIKTEX_ASSUME_YES='1'
Push-Location 'C:\Research\SPINE_Codex_Starter\manuscript'
try {
  pdflatex -interaction=nonstopmode -halt-on-error target_journal.tex
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  bibtex target_journal
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  pdflatex -interaction=nonstopmode -halt-on-error target_journal.tex
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  pdflatex -interaction=nonstopmode -halt-on-error target_journal.tex
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally {
  Pop-Location
}
```

Final LaTeX audit status:

- `main_unblinded`: passed
- `main_blinded`: passed
- `target_journal`: passed
- `supplement`: passed

Final logs had no unresolved citation/reference markers. Existing overfull table/figure warnings remain present and were not introduced as scientific changes.

## Test Suite Result

Command:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONPATH=(Resolve-Path -LiteralPath 'src').Path
python -m pytest -q -p no:cacheprovider
```

Result: passed with exit code 0 after correcting a comma in the Figure S10 manifest row.

## Protected Core Hash Result

Protected core comparison: `unchanged = 1325`, `changed = 0`, `added = 0`, `removed = 0`.

## Submission/Package/Release Non-Mutation Result

No `submission/nature_neuroscience` package rebuild, public-release sync, GitHub release, Zenodo update, DOI metadata update, preprint action, or journal submission action was performed.
