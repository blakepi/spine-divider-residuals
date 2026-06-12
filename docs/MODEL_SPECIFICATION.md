# SPINE Model Specification

## Scope

This document specifies the implementation-ready equations and architecture. Phase 00 created the scaffold and unit audit. Phase 01 implemented the manuscript-faithful passive three-compartment core. Phase 01.1 added documentation alignment, validation guardrails, and metric/unit clarifications without changing the passive solver equations.

## Tracks

`manuscript_faithful` preserves the manuscript equations and values. `plausibility_revised` is separate and initially identical until evidence-based revisions are tested and documented.

## Geometry

For a cylindrical neck:

```text
R_neck = rho_i * L_n / (pi * r_n^2)
g_hd = 1 / R_neck
A_h = 4 * pi * r_h^2
```

All calculations use compatible units. Internally, resistance is ohms and conductance is siemens. Manuscript-facing neck geometry helpers accept intracellular resistivity in ohm-cm and micrometer geometry at the public boundary, then convert micrometer lengths/radii to centimeters before returning resistance in ohms. This is the deliberate exception to the otherwise SI-only `PassiveParameters` convention.

For a nonuniform neck:

```text
R_neck = integral_0^L rho_i / (pi * r(x)^2) dx
```

Phase 01 implements this as a lumped resistance quadrature helper only. It does not implement a distributed cable or generalized morphology.

## Passive three-compartment equations

Sign convention: outward leak and synaptic currents are represented as conductance times `(V - E)`, while axial terms add current from neighboring compartments as `g_kj * (V_j - V_k)`.

```text
C_h dV_h/dt =
  -g_L,h (V_h - E_L)
  -g_syn(t) (V_h - E_syn)
  +g_hd (V_d - V_h)

C_d dV_d/dt =
  -g_L,d (V_d - E_L)
  +g_hd (V_h - V_d)
  +g_DS (V_s - V_d)

C_s dV_s/dt =
  -g_L,s (V_s - E_L)
  +g_DS (V_d - V_s)
```

The Phase 01 solver must implement backward Euler directly as a linear solve at each time step.

## Passive matrix form

Let `V = [V_h, V_d, V_s]^T` and `C = diag(C_h, C_d, C_s)`. For a fixed synaptic conductance value `g_syn(t)`, the manuscript equations are written as:

```text
C dV/dt = -A(t) V + b(t)
```

The broader formulation may later include `I_ext(t)`, but the Phase 01 three-compartment simulator does not expose an external-current input path. External current is used only in the separate dendrite-soma input-resistance calculation.

where:

```text
A(t) =
[[g_L,h + g_syn(t) + g_hd,  -g_hd,                 0],
 [-g_hd,                     g_L,d + g_hd + g_DS, -g_DS],
 [0,                         -g_DS,                g_L,s + g_DS]]

b(t) =
[g_L,h E_L + g_syn(t) E_syn,
 g_L,d E_L,
 g_L,s E_L]^T
```

This matrix form preserves the sign convention in the manuscript. Leak and synaptic terms draw outward current as `g(V-E)`, so they appear as positive diagonal entries in `A` and reversal-weighted source terms in `b`. Axial coupling contributes equal and opposite currents to connected compartments; each edge adds `+g` to the two connected diagonals and `-g` to the symmetric off-diagonal entries.

Backward Euler evaluates `A` and `b` at `t[n+1]`:

```text
(C/dt + A[n+1]) V[n+1] = (C/dt) V[n] + b[n+1]
```

The independent Phase 01 cross-check is a project-implemented Crank-Nicolson/trapezoidal step:

```text
(C/dt + 0.5 A[n+1]) V[n+1]
  = (C/dt - 0.5 A[n]) V[n] + 0.5 (b[n] + b[n+1])
```

No prebuilt neuroscience simulator is used.

## Synapse

The head receives a conductance-based excitatory event:

```text
I_syn,h(t, V_h) = g_syn(t) * (V_h - E_syn)
g_syn(t; t0) = g_max * eta * [exp(-(t-t0)/tau_d) - exp(-(t-t0)/tau_r)] * 1[t >= t0]
t_peak = tau_r * tau_d / (tau_d - tau_r) * ln(tau_d / tau_r)
eta = 1 / [exp(-t_peak/tau_d) - exp(-t_peak/tau_r)]
```

Phase 01 must verify both continuous-time peak normalization and grid-sampled peak behavior for the configured `dt`.

## Input resistance and SMI

The baseline dendritic input resistance is measured from the dendrite-soma subcircuit with the stimulated spine omitted:

```text
R_in,d = Delta V_d / Delta I_d
SMI = R_neck / R_in,d
```

For the passive two-node load with the spine omitted, voltage displacements around `E_L` satisfy:

```text
[[g_L,d + g_DS, -g_DS],
 [-g_DS,         g_L,s + g_DS]] [Delta V_d, Delta V_s]^T
 = [Delta I_d, 0]^T
```

The time-domain check integrates only these two nodes. The stimulated spine head and `g_hd` are not present in either input-resistance method.

The limiting voltage-divider intuition is:

```text
Delta V_d / Delta V_h ~= 1 / (1 + SMI)
```

This is not an exact transient prediction.

## Output metrics for later phases

Required metrics include peak depolarizations `A_h`, `A_d`, `A_s`; attenuation ratios `Gamma_h_to_d` and `Gamma_h_to_s`; peak latencies; half-widths; voltage integrals; peak and integrated synaptic current; peak and integrated neck current; dendritic charge transfer; local driving force; and dendrite-to-soma transfer ratio.

Phase 01 defines the metric window as `T = 50 ms` after the configured synaptic event time. This is not tuned to reproduce any manuscript caption. It is a fixed audit choice because it spans more than 16 decay time constants for the manuscript `tau_d = 3 ms` while remaining short enough for scaffold tests.

Signed current convention for metrics:

- `peak_synaptic_current_A` is the minimum signed synaptic current in the metric window. For an excitatory event at a hyperpolarized head, this is negative because synaptic current is inward under the outward-current convention.
- `integrated_synaptic_current_C` is also signed; inward excitatory charge is negative.
- `peak_neck_current_A`, `integrated_neck_current_C`, and `dendritic_charge_from_neck_C` use `g_hd (V_h - V_d)`. Positive values indicate current/charge from the spine head into the dendrite.

Driving-force metrics:

- `peak_driving_force_V` is the maximum absolute `|V_h - E_syn|` in the metric window.
- `initial_abs_driving_force_V` is `|V_h - E_syn|` at the first metric-window sample.
- `minimum_abs_driving_force_V` is the smallest absolute driving force in the metric window.
- `driving_force_reduction_V = initial_abs_driving_force_V - minimum_abs_driving_force_V`.

Programmatic validation:

- `PassiveParameters` rejects nonpositive capacitances, conductances, intracellular resistivity, `dt_s`, `stop_s`, `metric_window_s`, and input-resistance current.
- `stop_s` must exceed the synaptic event time.
- the metric window must end at or before `stop_s`.
- the time-domain input-resistance check rejects durations shorter than 10 passive dendrite-soma load time constants.

## Result provenance format

Every result file should include machine-readable provenance with:

```text
project_version
phase
track
config_path
config_sha256
code_commit_or_status
command
utc_timestamp
python_version
platform
dependency_versions
random_seed_or_not_applicable
input_files
output_files
```

Phase 00 did not generate scientific results. Phase 01/01.1 smoke outputs are validation artifacts, not manuscript reproduction results.
