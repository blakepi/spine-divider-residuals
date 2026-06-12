# Manuscript Build Instructions

See `../LATEX_BUILD_INSTRUCTIONS.md` for repository-level production instructions. This file is the manuscript-local quickstart.

## Windows PowerShell

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1 all
```

Individual targets:

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1 unblinded
powershell -ExecutionPolicy Bypass -File build.ps1 blinded
powershell -ExecutionPolicy Bypass -File build.ps1 target
powershell -ExecutionPolicy Bypass -File build.ps1 supplement
```

Use `-NoLatexmk` to force the direct `pdflatex`/`bibtex` fallback. Use `-RenderFigureFallbacks` only if legacy SVG-to-PDF fallback figures must be regenerated.

## Unix Shell

```bash
chmod +x build.sh
./build.sh all
```

Use `./build.sh all --render-figures` only if SVG fallback PDFs must be regenerated.

## Output PDFs

Successful builds copy PDFs to:

```text
../submission/compiled_pdfs/
  main_unblinded_R7.pdf
  main_blinded_R7.pdf
  target_journal_R7.pdf
  supplement_R7.pdf
```

## Toolchain Notes

The wrappers use `latexmk` if available and otherwise fall back to:

```text
pdflatex
bibtex
pdflatex
pdflatex
```

The publication manuscript includes prebuilt PDFs from `figures_publication/`; ordinary compilation does not require Python. Python with `reportlab` is required only for the optional `render_figure_pdfs.py` fallback path.

The preamble disables microtype expansion with:

```latex
\usepackage[protrusion=true,expansion=false]{microtype}
```

This is the preferred MiKTeX-compatible workaround for pdfTeX font-expansion errors.
