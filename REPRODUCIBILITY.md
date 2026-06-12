# Reproducibility

This release is built around existing machine-readable outputs and bounded validation scripts. It does not rerun broad primary ensembles during final submission cleanup.

## Tested local environment

- Operating system: Windows, PowerShell
- Python package requirement: Python >=3.12
- LaTeX: MiKTeX `pdflatex` detected during finalization
- GitHub CLI: not detected on PATH during finalization
- Pandoc: not detected on PATH during finalization
- LibreOffice/soffice: not detected on PATH during finalization

## Core checks

```powershell
$env:PYTHONPATH="src"
python -m unittest discover -s tests
python scripts/revision_restart/phase4_validation_runner.py
```

## Manuscript build

```powershell
cd manuscript
pdflatex -interaction=nonstopmode main_unblinded.tex
bibtex main_unblinded
pdflatex -interaction=nonstopmode main_unblinded.tex
pdflatex -interaction=nonstopmode main_unblinded.tex
```

## Expected validation highlights

- Independent matrix benchmark rows: 3.
- Maximum all-trace voltage difference: 1.249000902703301e-13 mV.
- Maximum head-amplitude difference: 1.4210854715202004e-14 mV.
- Maximum local-transfer difference: 7.549516567451064e-15.
- NEURON unavailable; no NEURON validation claimed.
