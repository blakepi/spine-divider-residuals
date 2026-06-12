# Installation

## Requirements

- Python `3.12` or newer
- A shell such as PowerShell, Command Prompt, bash, or zsh
- Optional: Git for version control and status review

## Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

Optional full dependency install:

```powershell
python -m pip install -r requirements.txt
```

## Unix Shell

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Optional full dependency install:

```bash
python -m pip install -r requirements.txt
```

## Verify Installation

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
```

Windows PowerShell:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -p 'test_*.py'
```

## CLI Smoke Test

```bash
PYTHONPATH=src python -m spine.cli load-config configs/manuscript_faithful/baseline.toml
PYTHONPATH=src python -m spine.cli smoke configs/manuscript_faithful/baseline.toml --output-csv results/phase01_smoke_trace.csv
```

Windows PowerShell:

```powershell
$env:PYTHONPATH='src'
python -m spine.cli load-config configs\manuscript_faithful\baseline.toml
python -m spine.cli smoke configs\manuscript_faithful\baseline.toml --output-csv results\phase01_smoke_trace.csv
```

## Notes

The validated Codex runtime used during development contained Python 3.12.13
and NumPy 2.3.5. It did not include every optional dependency in
`requirements.txt`, so the default scripts avoid requiring matplotlib for
figure generation and write SVG files directly.
