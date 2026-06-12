# Final Scientific Synthesis

Date: 2026-06-10

## 1. Manuscript Reproduction

Phase 02 reproduced the manuscript-faithful passive model using
`configs/manuscript_faithful/baseline.toml`, backward Euler integration,
`dt = 0.01 ms`, and a fixed `50 ms` post-event metric window.

All nine Figure 2 caption targets for SMI, `Gamma_h_to_d`, and
`Gamma_h_to_s` reproduced exactly under predefined tolerances. The fixed-load
geometry sweep reproduced the expected monotonic behavior, but it also
confirmed a key limitation: at fixed dendritic load, SMI and `R_neck` have
identical rank ordering.

## 2. Passive Findings

Phase 03 extended the model to passive compartment trees, branch points,
spatial discretization, multiple neck models, distributed necks, impedance,
and SMI challenge suites.

Robust passive result:

- SMI is a strong local descriptor for `Gamma_h_to_d`
  (`abs(Spearman) = 0.942342` in Phase 03).

Passive limitations:

- SMI is weak for somatic transfer in broad morphology challenges.
- SMI is weak for head amplitude.
- Equal SMI does not imply equal transient behavior.
- Frequency-dependent and downstream filtering require impedance descriptors.

## 3. Active Findings

Phase 04 added opt-in active-extension mechanisms: AMPA, NMDA with magnesium
block, Na, KDR, HCN, A-type potassium, and restrained electrical-only calcium.
These mechanisms remain disabled in `manuscript_faithful`.

Active validation passed all 12 active validation rows. Active results
preserved the local SMI conclusion:

- active `Gamma_h_to_d`: SMI `abs(Spearman) = 0.924906`.

Active mechanisms also strengthened SMI limitations:

- active `A_h_mV`: SMI `abs(Spearman) = 0.236404`;
- AMPA+NMDA/full restrained iso-SMI `A_h_mV` spread: `0.856685`;
- AMPA+NMDA/full restrained iso-SMI `Gamma_h_to_d` spread: `0.345269`.

## 4. Uncertainty Findings

Phase 05 introduced deterministic uncertainty, sensitivity, identifiability,
predictor comparison, and claim robustness.

Phase 05.1 then audited convergence at N=96, 192, 384, and 768. The original
Phase 05 SMI convergence failure was a real small-sample warning, not a solver
defect. By N=768, SMI median convergence passed:

- final 384-to-768 SMI median relative change: `0.012091`;
- final maximum median relative change across tracked outputs: `0.029154`.

The strongest uncertainty result is radius sensitivity:

- `R_neck` and SMI scale approximately as `1/r^2`;
- N=768 radius-induced SMI class flip fraction: `0.239583`;
- intermediate-class flip fraction: `1.000000`.

## 5. Epilepsy Exploratory Findings

Phase 06 implemented a separated `epilepsy_exploratory` module. It is
hypothesis-generating only and makes no clinical, diagnostic, prognostic, or
therapeutic claims.

Exploratory results:

- morphology-dominant perturbations increased SMI and reduced local transfer;
- increased synaptic strength left SMI fixed at `0.053492` while isolated
  head amplitude increased from `13.9256 mV` to `19.4177 mV`;
- clustered synchronous activation produced threshold-like behavior not
  present in isolated matched baseline simulations;
- Phase 06 uncertainty uses `N=8` per scenario and is a sensitivity screen,
  not a biological confidence interval.

## 6. Strongest Positive Results

1. Manuscript passive caption values reproduce under predefined tolerances.
2. SMI is consistently useful for local spine-head to parent-dendrite
   isolation.
3. The passive and active numerical frameworks pass direct validation tests.
4. Deterministic uncertainty and convergence audits are reproducible.
5. Radius uncertainty is quantitatively important and transparently reported.

## 7. Strongest Counterexamples

1. Passive iso-SMI `A_h` spread: `0.614340`.
2. Active AMPA+NMDA/full restrained iso-SMI `A_h_mV` spread: `0.856685`.
3. Phase 05.1 passive iso-SMI amplitude failure prevalence: `0.645428`.
4. Same-SMI synaptic-strength Phase 06 scenario changed head amplitude by a
   large amount while leaving SMI unchanged.
5. Similar local transfer can arise from substantially different SMI values.

## 8. Strongest Limitations

- SMI is not a universal predictor.
- SMI does not reliably predict head amplitude.
- Somatic transfer is ensemble-dependent and requires downstream context.
- SMI class labels are fragile near thresholds under radius uncertainty.
- Active-extension conductances are restrained generic mechanisms, not
  cell-type-calibrated densities.
- Phase 06 disease-associated scenarios are exploratory sensitivity probes.
- No posterior inference or experimental calibration has been performed.

## 9. Revised Interpretation Of SMI

The most defensible interpretation is:

```text
SMI is a compact low-frequency coordinate for local spine-to-dendrite
electrical isolation. It should be interpreted alongside absolute neck
resistance, dendritic input resistance, local and transfer impedance,
synaptic conductance, active state, and measurement uncertainty. It is not a
universal predictor of amplitude, somatic impact, nonlinear threshold
behavior, or electrical equivalence.
```

## Finding Classes

Robust findings:

- manuscript passive reproduction;
- local SMI usefulness;
- amplitude non-predictiveness;
- equal-SMI non-equivalence;
- radius-driven class fragility.

Ensemble-dependent findings:

- somatic transfer predictor rankings;
- exact top-predictor labels;
- active-state predictor ordering.

Exploratory findings:

- epilepsy-associated perturbation scenarios;
- active frozen-gate impedance interpretations;
- clustered and asynchronous Phase 06 scenario outcomes.

Unsupported hypotheses:

- SMI as a universal predictor;
- SMI as a head-amplitude predictor;
- SMI classes as stable biological categories;
- Phase 06 scenarios as calibrated epilepsy mechanisms.
