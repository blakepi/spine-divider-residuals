# Phase 00 Unit Audit

## Canonical internal units

SPINE uses SI internally for solver state and equations: meter-compatible geometry after conversion, second, volt, ampere, siemens, farad, and ohm. Configuration files keep manuscript-facing electrophysiology units for readability. Conversion happens at API boundaries.

Phase 01.1 clarification: `PassiveParameters.intracellular_resistivity_ohm_cm` intentionally preserves the manuscript unit ohm-cm because the public geometry helpers accept micrometer morphology and perform the manuscript-specified conversion to centimeters internally before returning ohms. All solver matrices still receive resistance/conductance in ohms/siemens.

## Verified conversions

| Quantity | Manuscript unit | SI conversion |
|---|---:|---:|
| 1 um | length | 1e-6 m = 1e-4 cm |
| 1 pF | capacitance | 1e-12 F |
| 1 nS | conductance | 1e-9 S |
| 1 pA | current | 1e-12 A |
| 1 mV | voltage | 1e-3 V |
| 1 Mohm | resistance | 1e6 ohm |
| 1 ms | time | 1e-3 s |
| 100 ohm cm | resistivity | 1 ohm m |
| 0.01 pF/um2 | specific capacitance | 0.01 F/m2 |
| 3e-6 nS/um2 | specific conductance | 0.003 S/m2 |

## Manuscript parameter audit

| Parameter | Value | Conversion or derived value | Status |
|---|---:|---:|---|
| E_L | -70 mV | -0.070 V | preserved |
| E_syn | 0 mV | 0 V | preserved |
| c_m | 0.01 pF/um2 | 0.01 F/m2 | preserved |
| specific head leak | 3e-6 nS/um2 | 0.003 S/m2 | preserved |
| r_h | 0.35 um | A_h = 1.5393804003 um2 | preserved |
| head capacitance | derived | 0.0153938040 pF | derived, not separately configured |
| head leak | derived | 4.6181412e-6 nS | derived, very small versus g_max |
| C_d | 120 pF | 1.2e-10 F | preserved |
| C_s | 220 pF | 2.2e-10 F | preserved |
| g_L,d | 2.5 nS | 2.5e-9 S | preserved |
| g_L,s | 7.0 nS | 7.0e-9 S | preserved |
| g_DS | 12.0 nS | 1.2e-8 S | preserved |
| rho_i | 100 ohm cm | 1 ohm m | preserved; uncertain biologically |
| g_max | 1.4 nS | 1.4e-9 S | preserved; large relative to head leak |
| tau_r, tau_d | 0.3 ms, 3.0 ms | 3e-4 s, 3e-3 s | preserved |
| t0 | 20 ms | 0.020 s | preserved |
| dt | 0.01 ms | 1e-5 s | preserved |
| Delta I_d | 10 pA | 1e-11 A | preserved |
| L_n sweep | 0.10-2.00 um | 1e-7-2e-6 m | preserved |
| r_n sweep | 0.035-0.25 um | 3.5e-8-2.5e-7 m | preserved |
| matched R_neck | 100 Mohm | 1e8 ohm | preserved |
| g_L,d validation | 0.1-30 nS | 1e-10-3e-8 S | preserved |

## Neck resistance checks

Using rho_i = 100 ohm cm:

| L_n (um) | r_n (um) | R_neck (Mohm) |
|---:|---:|---:|
| 1.0 | 0.10 | 31.830989 |
| 0.25 | 0.25 | 1.273240 |
| 0.75 | 0.12 | 16.578640 |
| 1.50 | 0.05 | 190.985932 |

The square dependence on radius is the dominant uncertainty amplifier: halving neck radius quadruples R_neck at fixed length and resistivity.

## Anomalies and uncertainties

1. The manuscript uses lumped dendrite and soma capacitances/conductances without deriving them from morphology. This is acceptable for the proof-of-principle track but limits cell-type interpretation.
2. The derived head leak conductance is orders of magnitude smaller than the peak synaptic conductance. This may be intentional for a compact event-driven proof of principle, but it should be sensitivity-tested before biological claims.
3. Intracellular resistivity and neck radius are uncertain enough that the same morphology may produce materially different R_neck estimates.
4. The metric window T is defined symbolically but no numeric value appears in Table 1. Phase 01/02 must choose a reproduction value, document it, and avoid silent tuning.

## Phase 01 enforcement in code

Phase 01 enforces conversions at the configuration boundary in `spine.passive.parameters_from_config`. Manuscript-facing TOML values are converted to SI before entering the solver:

- mV to V for reversal potentials;
- pF to F for dendrite, soma, and derived head capacitance;
- nS to S for dendrite, soma, dendrite-soma coupling, derived head leak, and synaptic peak conductance;
- ms to s for time step, event time, synaptic kinetics, simulation stop, and metric window;
- pA to A for dendritic input-resistance current;
- micrometer geometry to centimeter geometry inside neck-resistance helpers before ohm calculation.

The solver, input-resistance methods, SMI, and metrics operate on SI values after geometry-derived neck resistance has been returned in ohms.

## Phase 01.1 validation clarifications

- Programmatically constructed `PassiveParameters` now reject nonpositive time step, simulation stop time, metric window, capacitances, conductances, intracellular resistivity, and input-resistance current.
- Simulation stop time must exceed the configured synaptic event time.
- The metric window must fit within the simulated interval.
- The time-domain dendrite-soma input-resistance check now validates its duration against the slowest passive dendrite-soma load time constant and requires at least 10 time constants.

## Phase 04 active/nonlinear unit audit

Phase 04 keeps SI solver units and stores readable active-extension values in
`configs/active_extension/baseline.toml`.

| Quantity | Config/report unit | Internal use |
|---|---:|---:|
| active conductance | nS | S |
| reversal potential | mV | V |
| synaptic time constants | ms | s |
| current pulse amplitude | nA | A |
| voltage-clamp conductance | nS | S |
| voltage-clamp command | mV | V |
| gates | dimensionless | dimensionless |
| magnesium concentration | mM | mM in NMDA block boundary equation |
| NMDA gamma | per mV | applied after converting V to mV |

Active currents use the same outward-positive sign convention:

```text
I_x = g_x(V, gates, t) (V - E_x)
```

Therefore Na, Ca, AMPA, and NMDA currents are inward/negative below their
positive reversal potentials, K currents are outward/positive above `E_K`, and
HCN is inward/negative at `-70 mV` when open because `E_HCN = -30 mV`.

Phase 04 validation checks:

- nS-to-S, mV-to-V, and Mohm-to-ohm conversions;
- AMPA peak normalization in S;
- NMDA magnesium-block voltage handling in V-to-mV;
- gate bounds as dimensionless probabilities;
- active current signs in amperes.
