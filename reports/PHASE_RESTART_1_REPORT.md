# Revision Restart Phase 1 Report

## Objective

Restart Phase 1 derived the analytic local voltage-divider relation for SMI
and quantified residuals between existing simulated peak `Gamma_h_to_d` values
and the divider prediction `1/(1+SMI)`.

This phase intentionally did not modify validated model code, raw simulation
outputs, primary ensembles, manuscript scientific source, manuscript tables,
publication figures, release state, DOI state, license state, or submission
state.

## Inputs Read

- `AGENTS.md`
- `docs/PROJECT_STATE.md`
- `manuscript/revision_restart/PHASE0_NEXT_PHASE_HANDOFF.md`
- `reports/PHASE_RESTART_0_REPORT.md`
- Phase 0 restart artifacts in `manuscript/revision_restart/`
- Current manuscript entry points, sections, tables, supplement, claim ledger,
  numerical verification report, and final synthesis/audit context
- Existing result CSVs under `results/phase02/`, `results/phase03/`,
  `results/phase04/`, `results/phase05/`, `results/phase05_1/`,
  `results/phase06/`, `results/revision_v2/r3/`, and
  `results/revision_v2/r4/`

## Implementation

Added deterministic post-processing script:

```text
scripts/revision_restart/phase1_divider_residual_analysis.py
```

The script:

1. inventories candidate CSV files;
2. identifies rows containing SMI and observed `Gamma_h_to_d`;
3. computes `Gamma_h_to_d,divider = 1/(1+SMI)`;
4. computes signed, absolute, and relative residuals;
5. summarizes by dataset, regime, and active/passive label;
6. writes outlier tables and a source manifest;
7. creates diagnostic-only SVG figures.

The script uses `pandas` and `numpy` only. It does not call solver code or
modify source datasets.

## Outputs Created

Restart Phase 1 reports:

- `manuscript/revision_restart/PHASE1_ANALYTIC_DIVIDER_DERIVATION.md`
- `manuscript/revision_restart/PHASE1_DATA_INVENTORY.md`
- `manuscript/revision_restart/PHASE1_RESIDUAL_ANALYSIS_REPORT.md`
- `manuscript/revision_restart/PHASE1_CLAIM_REASSESSMENT.md`
- `manuscript/revision_restart/PHASE1_MANUSCRIPT_INSERT_DRAFT.md`
- `manuscript/revision_restart/PHASE1_DIAGNOSTIC_FIGURE_NOTES.md`
- `manuscript/revision_restart/PHASE1_STATIC_LANGUAGE_AUDIT.md`
- `manuscript/revision_restart/PHASE1_NEXT_PHASE_HANDOFF.md`
- `reports/PHASE_RESTART_1_REPORT.md`

Derived data:

- `results/revision_restart/phase1/phase1_divider_residual_rows.csv`
- `results/revision_restart/phase1/phase1_divider_residual_summary_by_dataset.csv`
- `results/revision_restart/phase1/phase1_divider_residual_summary_by_regime.csv`
- `results/revision_restart/phase1/phase1_baseline_target_residuals.csv`
- `results/revision_restart/phase1/phase1_active_passive_residual_comparison.csv`
- `results/revision_restart/phase1/phase1_residual_outlier_cases.csv`
- `results/revision_restart/phase1/phase1_data_inventory.csv`
- `results/revision_restart/phase1/phase1_source_manifest.csv`
- `results/revision_restart/phase1/phase1_protected_hashes_before.csv`
- `results/revision_restart/phase1/phase1_protected_hashes_after.csv`
- `results/revision_restart/phase1/phase1_protected_hash_comparison.csv`
- `manuscript/revision_restart/PHASE1_STATIC_LANGUAGE_RAW_HITS.csv`

Diagnostic figures:

- `results/revision_restart/phase1/diagnostic_figures/phase1_observed_gamma_vs_smi.svg`
- `results/revision_restart/phase1/diagnostic_figures/phase1_residual_vs_smi.svg`
- `results/revision_restart/phase1/diagnostic_figures/phase1_absolute_residual_vs_smi.svg`
- `results/revision_restart/phase1/diagnostic_figures/phase1_observed_vs_divider.svg`

Checkpoint:

- `checkpoints/SPINE_restart_phase_1_checkpoint.zip`
- `checkpoints/SPINE_restart_phase_1_checkpoint.zip.sha256`

## Main Results

Analytic relation:

```text
Gamma_h_to_d,divider = R_in,d/(R_neck + R_in,d) = 1/(1+SMI)
```

Residual definition:

```text
residual = observed Gamma_h_to_d - Gamma_h_to_d,divider
```

Data inventory:

- Candidate CSVs scanned: 104
- Residual-capable CSVs: 24
- Primary residual source CSVs used: 16
- R4 figure snapshot duplicates skipped: 8

Residual analysis:

- Total residual rows: 3718
- Non-exploratory rows: 3584
- Overall median absolute residual: 0.054751694
- Overall mean absolute residual: 0.073401014
- Overall RMSE: 0.103138355
- Maximum absolute residual: 0.492427929
- Negative residual rows: 3680
- Positive residual rows: 38

Baseline target residuals:

| Condition | SMI | Observed Gamma_h_to_d | Divider | Residual |
|---|---:|---:|---:|---:|
| Low | 0.0088121579 | 0.9839703152 | 0.9912648179 | -0.0072945027 |
| Intermediate | 0.1147416393 | 0.7512821309 | 0.8970688496 | -0.1457867187 |
| High | 1.3218236853 | 0.1021324462 | 0.4306959251 | -0.3285634789 |

Largest absolute residual:

```text
dataset = phase02_matched_neck_load_sweep
SMI = 0.4521052632
observed Gamma_h_to_d = 0.1962273812
divider = 0.6886553099
residual = -0.4924279287
```

## Scientific Interpretation

Phase 1 supports a revised framing:

```text
SMI is a low-frequency local divider descriptor. Its main validated role is to
organize head-to-dendrite isolation. The residual from 1/(1+SMI) is the
scientifically informative quantity in transient, conductance-based,
morphologically extended, active, and uncertainty-tested regimes.
```

The analysis does not support an unqualified claim that SMI exactly predicts
peak `Gamma_h_to_d` across tested regimes.

## Static Language Audit

The static language audit searched manuscript-facing TeX files only and wrote:

```text
manuscript/revision_restart/PHASE1_STATIC_LANGUAGE_RAW_HITS.csv
```

It found 116 hits across targeted terms. Notable counts:

- `strongly associated`: 1
- `predicts`: 2
- `predictor`: 24
- `universal`: 8
- `voltage-divider`: 3

The audit recommends later manuscript softening from unqualified prediction
language to divider-limit ordering plus residual-domain language.

## Exact Command Record

Primary script syntax check:

```powershell
& 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m py_compile scripts\revision_restart\phase1_divider_residual_analysis.py
```

Primary script run:

```powershell
& 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' scripts\revision_restart\phase1_divider_residual_analysis.py
```

Result:

```text
datasets_used=16
residual_rows=3718
inventory_rows=104
baseline_rows=3
outlier_rows=48
overall_median_absolute_residual=0.054751694
overall_max_absolute_residual=0.492427929
diagnostic_figures=4
```

Static language audit command:

```powershell
$patterns = @('strongly associated','strong association','strongly predicts','predicts','predictor','local isolation','local descriptor','empirical','discovered','near-identity','voltage-divider','voltage divider','1/(1+SMI)','1/(1 + SMI)','Spine Morphology Index','universal','robust','active mechanisms','amplitude predictor','transfer predictor','electrical equivalence','ratio')
$files = Get-ChildItem -Path manuscript\main_*.tex, manuscript\target_journal.tex, manuscript\sections\*.tex, manuscript\tables\*.tex, manuscript\supplement\*.tex, manuscript\supplement\sections\*.tex -File
$root = (Get-Location).Path
$hits = foreach ($p in $patterns) { Select-String -Path $files.FullName -Pattern $p -SimpleMatch -CaseSensitive:$false | ForEach-Object { [pscustomobject]@{pattern=$p; file=$_.Path.Substring($root.Length + 1); line=$_.LineNumber; text=$_.Line.Trim()} } }
$hits | Export-Csv -LiteralPath manuscript\revision_restart\PHASE1_STATIC_LANGUAGE_RAW_HITS.csv -NoTypeInformation
$hits | Group-Object pattern | Select-Object Name,Count | Sort-Object Name | Format-Table -AutoSize
```

Generated-file and CSV parse check:

```powershell
& 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -c "<inline required-file and CSV-parse validation>"
```

Result:

```text
missing_required=0
phase1_divider_residual_rows.csv: rows=3718 cols=34
phase1_divider_residual_summary_by_dataset.csv: rows=21 cols=15
phase1_divider_residual_summary_by_regime.csv: rows=21 cols=16
phase1_baseline_target_residuals.csv: rows=3 cols=34
phase1_active_passive_residual_comparison.csv: rows=4 cols=15
phase1_residual_outlier_cases.csv: rows=48 cols=35
phase1_data_inventory.csv: rows=104 cols=9
phase1_source_manifest.csv: rows=128 cols=6
PHASE1_STATIC_LANGUAGE_RAW_HITS.csv: rows=116 cols=4
residual_rows=3718
datasets=16
negative_residuals=3680
positive_residuals=38
```

Protected-file hash comparison:

```powershell
& 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -c "<inline hash recomputation from phase1_protected_hashes_before.csv>"
```

Result:

```text
protected_files_checked=157
changed=0
missing=0
```

Repository tests:

```powershell
& 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests
```

Result: failed with `ModuleNotFoundError: No module named 'spine'` because
`PYTHONPATH` was not set.

Rerun with source path:

```powershell
$env:PYTHONPATH='src'; & 'C:\Users\gbp34\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s tests
```

Result:

```text
Ran 63 tests in 3.563s
OK
```

Git status:

```powershell
git status --short
```

Result: `git` is not recognized in this environment, so Git status could not
be reviewed with the Git executable.

Checkpoint creation:

```powershell
$archive = 'checkpoints\SPINE_restart_phase_1_checkpoint.zip'
$items = Get-ChildItem -Force | Where-Object { $_.Name -notin @('.git','checkpoints') }
$items | Compress-Archive -DestinationPath $archive -Force
$hash = Get-FileHash -Algorithm SHA256 -LiteralPath $archive
$hash.Hash | Set-Content -NoNewline -LiteralPath ($archive + '.sha256')
Get-Item -LiteralPath $archive, ($archive + '.sha256') | Select-Object Name,Length,LastWriteTime
```

Result:

```text
SPINE_restart_phase_1_checkpoint.zip        12164642 bytes
SPINE_restart_phase_1_checkpoint.zip.sha256       64 bytes
```

## Boundary

Restart Phase 1 stopped at the analytic-divider and residual-domain boundary.
It did not begin Restart Phase 2 ratio-versus-components analysis.
