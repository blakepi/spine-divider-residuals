# Quickstart

Run these commands from the repository root after installation.

## 1. Run The Full Test Suite

PowerShell:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -p 'test_*.py'
```

Unix:

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
```

## 2. Reproduce The Manuscript Baseline

```bash
PYTHONPATH=src python scripts/reproduce_manuscript.py
```

Outputs:

- `results/phase02/`
- `figures/phase02/`
- `reports/MANUSCRIPT_REPRODUCTION.md`

## 3. Run Phase 03 Passive Morphology And Impedance

```bash
PYTHONPATH=src python scripts/run_phase03.py
```

Outputs:

- `results/phase03/`
- `figures/phase03/`
- `reports/PHASE03_IMPEDANCE_REPORT.md`
- `reports/PHASE03_SMI_CHALLENGE_REPORT.md`
- `reports/PHASE03_PREDICTOR_COMPARISON.md`

## 4. Run Phase 04 Active And Nonlinear Analyses

```bash
PYTHONPATH=src python scripts/run_phase04.py
```

Outputs:

- `results/phase04/`
- `figures/phase04/`
- `reports/PHASE04_ACTIVE_VALIDATION.md`
- `reports/PHASE04_ACTIVE_SMI_REPORT.md`
- `reports/PHASE04_PROTOCOL_REPORT.md`

## 5. Run Phase 05 Uncertainty And Predictors

```bash
PYTHONPATH=src python scripts/run_phase05.py
```

Outputs:

- `results/phase05/`
- `figures/phase05/`
- `reports/PHASE05_UNCERTAINTY_REPORT.md`
- `reports/PHASE05_PREDICTOR_REPORT.md`
- `reports/PHASE05_CLAIM_ROBUSTNESS.md`

## 6. Run Phase 05.1 Convergence Audit

```bash
PYTHONPATH=src python scripts/run_phase05_1.py
```

Outputs:

- `results/phase05_1/`
- `figures/phase05_1/`
- `reports/PHASE05_1_CONVERGENCE_REPORT.md`
- `reports/PHASE05_1_RADIUS_UNCERTAINTY.md`
- `reports/PHASE05_1_PREDICTOR_STABILITY.md`

## 7. Run Phase 06 Exploratory Scenarios

```bash
PYTHONPATH=src python scripts/run_phase06.py
```

Outputs:

- `results/phase06/`
- `figures/phase06/`
- `reports/PHASE06_SCENARIO_RESULTS.md`
- `reports/PHASE06_UNCERTAINTY_AND_LIMITATIONS.md`
- `reports/PHASE06_SMI_EPILEPSY_PREDICTIONS.md`

Phase 06 is exploratory and makes no clinical or disease-calibration claims.

## 8. Create A Checkpoint

```bash
PYTHONPATH=src python scripts/make_checkpoint.py 7
```

The archive and SHA256 sidecar are written to `checkpoints/`.
