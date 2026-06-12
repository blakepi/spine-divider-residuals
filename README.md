# SPINE: load-normalized spine-neck ratio residuals

SPINE is a reproducible Python compartmental-modeling project analyzing the limits of a load-normalized spine-neck ratio in dendritic spine electrical isolation. The ratio `SMI = R_neck/R_in,d` defines the classical DC local voltage-divider expectation `Gamma_div = 1/(1+SMI)`. The manuscript and repository focus on residuals from that divider in transient conductance-based simulations, showing where component resistances, impedance/dynamic descriptors, synaptic conductance scale, active state, downstream filtering, and measurement uncertainty make a single scalar incomplete. SMI is not a universal predictor; it is a scoped local-divider coordinate.

## Repository contents

- `src/spine/`: transparent first-principles Python implementation.
- `configs/`: baseline, plausibility-revised, and active-extension configuration tracks.
- `configs/epilepsy_exploratory/`: separated exploratory epilepsy stress-test configuration; it is not part of the primary physiological baseline and does not support clinical claims.
- `scripts/`: bounded reproduction, validation, and manuscript-support scripts.
- `results/`: selected machine-readable derived outputs used by the manuscript.
- `manuscript/`: unblinded manuscript source, figure/table manifests, and provenance ledgers.
- `submission/nature_neuroscience/`: Nature Neuroscience submission package.
- `submission/final/`: final QA, release, and portal-entry audit reports.

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

Unix-like shells can use `source .venv/bin/activate` instead.

## Reproducibility commands

```powershell
$env:PYTHONPATH="src"
python -m unittest discover -s tests
python scripts/revision_restart/phase4_validation_runner.py
python scripts/revision_restart/phase8_final_qa_audit.py
```

The broad primary ensembles are not rerun during final submission cleanup. The release includes selected derived CSVs, claim-to-source ledgers, figure/table manifests, and validation outputs needed to verify manuscript-facing claims.

## Validation summary

The passive baseline was cross-checked with an independently assembled direct-matrix benchmark and DC analytic limits. The maximum all-trace voltage difference in the independent passive baseline benchmark was `1.249000902703301e-13` mV, and the maximum local-transfer difference was `7.549516567451064e-15`. NEURON was unavailable in the execution environment; no NEURON validation is claimed.

## Citation

Pierpoint, G., and Musto, A. (2026). *Residual Limits of a Load-Normalized Spine-Neck Ratio in Compartmental Models*. Submission release `v1.0.0-submission`.

Public GitHub upload and Zenodo DOI minting require authenticated manual steps in this environment. Do not cite a DOI until it appears in `submission/final/ZENODO_DOI_ACTION_REQUIRED.md` as completed and verified.

## Licenses

Code is released under the MIT License (`LICENSE`). Manuscript-facing derived data, figures, tables, and documentation are released under Creative Commons Attribution 4.0 International (`DATA_LICENSE.md`) unless otherwise stated.

## Contact

Correspondence: Alberto Musto, MD, PhD, `mustoae@odu.edu`. First author/contact: Gregory Pierpoint, `pierpogb@odu.edu`.
