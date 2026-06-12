#!/usr/bin/env bash
set -euo pipefail

target="${1:-all}"
render_figures="${2:-}"

script_dir="$(cd "$(dirname "$0")" && pwd)"
if [[ "$(basename "$script_dir")" == "jcns_source_package" ]]; then
  out_dir="$script_dir/compiled_pdfs"
else
  repo_root="$(cd "$script_dir/.." && pwd)"
  out_dir="$repo_root/submission/compiled_pdfs"
fi

render_fallbacks() {
  if [[ "$render_figures" != "--render-figures" ]]; then
    return 0
  fi
  command -v python >/dev/null || {
    echo "python is required only when --render-figures is requested" >&2
    exit 1
  }
  (cd "$script_dir" && python render_figure_pdfs.py)
}

pdflatex_fallback() {
  local workdir="$1"
  local main="$2"
  local base="${main%.tex}"
  command -v pdflatex >/dev/null || { echo "pdflatex is not available on PATH" >&2; exit 1; }
  command -v bibtex >/dev/null || { echo "bibtex is not available on PATH" >&2; exit 1; }
  (
    cd "$workdir"
    pdflatex -interaction=nonstopmode -halt-on-error "$main"
    bibtex "$base"
    pdflatex -interaction=nonstopmode -halt-on-error "$main"
    pdflatex -interaction=nonstopmode -halt-on-error "$main"
  )
}

build_one() {
  local workdir="$1"
  local main="$2"
  local outname="$3"
  mkdir -p "$out_dir"
  if command -v latexmk >/dev/null; then
    if ! (cd "$workdir" && latexmk -pdf -interaction=nonstopmode -halt-on-error "$main"); then
      pdflatex_fallback "$workdir" "$main"
    fi
  else
    pdflatex_fallback "$workdir" "$main"
  fi
  cp "$workdir/${main%.tex}.pdf" "$out_dir/$outname"
}

render_fallbacks

case "$target" in
  all)
    build_one "$script_dir" main_unblinded.tex main_unblinded_R7.pdf
    build_one "$script_dir" main_blinded.tex main_blinded_R7.pdf
    build_one "$script_dir" target_journal.tex target_journal_R7.pdf
    build_one "$script_dir/supplement" supplement.tex supplement_R7.pdf
    ;;
  unblinded) build_one "$script_dir" main_unblinded.tex main_unblinded_R7.pdf ;;
  blinded) build_one "$script_dir" main_blinded.tex main_blinded_R7.pdf ;;
  target) build_one "$script_dir" target_journal.tex target_journal_R7.pdf ;;
  supplement) build_one "$script_dir/supplement" supplement.tex supplement_R7.pdf ;;
  *) echo "Usage: $0 [all|unblinded|blinded|target|supplement] [--render-figures]" >&2; exit 2 ;;
esac
