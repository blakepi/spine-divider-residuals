param(
  [ValidateSet("all","unblinded","blinded","target","supplement")]
  [string]$Target = "all",
  [switch]$RenderFigureFallbacks,
  [switch]$NoLatexmk
)

$ErrorActionPreference = "Stop"

if ((Split-Path $PSScriptRoot -Leaf) -eq "jcns_source_package") {
  $OutputDir = Join-Path $PSScriptRoot "compiled_pdfs"
} else {
  $OutputDir = Join-Path (Split-Path $PSScriptRoot -Parent) "submission\compiled_pdfs"
}

function Get-PythonCommand {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($python) { return $python.Source }
  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py) { return $py.Source }
  return $null
}

function Invoke-FigureRender {
  if (-not $RenderFigureFallbacks) { return }
  $python = Get-PythonCommand
  if (-not $python) {
    throw "Python was not found. Re-run without -RenderFigureFallbacks or install Python with reportlab."
  }
  & $python (Join-Path $PSScriptRoot "render_figure_pdfs.py")
}

function Invoke-PdfLatexFallback($Main, $WorkDir) {
  if (-not (Get-Command pdflatex -ErrorAction SilentlyContinue)) {
    throw "pdflatex is not available on PATH."
  }
  if (-not (Get-Command bibtex -ErrorAction SilentlyContinue)) {
    throw "bibtex is not available on PATH."
  }
  Push-Location $WorkDir
  try {
    $base = [System.IO.Path]::GetFileNameWithoutExtension($Main)
    & pdflatex -interaction=nonstopmode -halt-on-error $Main
    & bibtex $base
    & pdflatex -interaction=nonstopmode -halt-on-error $Main
    & pdflatex -interaction=nonstopmode -halt-on-error $Main
  } finally {
    Pop-Location
  }
}

function Invoke-OneBuild($Main, $WorkDir, $OutName) {
  New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
  $built = $false
  if (-not $NoLatexmk) {
    $latexmk = Get-Command latexmk -ErrorAction SilentlyContinue
    if ($latexmk) {
      Push-Location $WorkDir
      try {
        & $latexmk.Source -pdf -interaction=nonstopmode -halt-on-error $Main
        if ($LASTEXITCODE -eq 0) { $built = $true }
      } finally {
        Pop-Location
      }
    }
  }
  if (-not $built) {
    Invoke-PdfLatexFallback $Main $WorkDir
  }
  $pdf = Join-Path $WorkDir ([System.IO.Path]::ChangeExtension($Main, ".pdf"))
  if (-not (Test-Path $pdf)) {
    throw "Expected PDF was not created: $pdf"
  }
  Copy-Item -Force -LiteralPath $pdf -Destination (Join-Path $OutputDir $OutName)
}

Push-Location $PSScriptRoot
try {
  Invoke-FigureRender
  if ($Target -eq "all" -or $Target -eq "unblinded") {
    Invoke-OneBuild "main_unblinded.tex" $PSScriptRoot "main_unblinded_R7.pdf"
  }
  if ($Target -eq "all" -or $Target -eq "blinded") {
    Invoke-OneBuild "main_blinded.tex" $PSScriptRoot "main_blinded_R7.pdf"
  }
  if ($Target -eq "all" -or $Target -eq "target") {
    Invoke-OneBuild "target_journal.tex" $PSScriptRoot "target_journal_R7.pdf"
  }
  if ($Target -eq "all" -or $Target -eq "supplement") {
    Invoke-OneBuild "supplement.tex" (Join-Path $PSScriptRoot "supplement") "supplement_R7.pdf"
  }
} finally {
  Pop-Location
}
