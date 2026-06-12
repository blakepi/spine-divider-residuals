# Phase 00 Limitations

1. Phase 00 does not implement the passive simulator, synaptic waveform, input-resistance solve, SMI computation, sweeps, or figures.
2. The manuscript-faithful model is a lumped three-compartment proof of principle, not a calibrated cell-type-specific reconstruction.
3. Neck resistance depends strongly on neck radius and intracellular resistivity, both of which are experimentally uncertain.
4. A cylindrical neck is a simplifying approximation. Nonuniform necks require integration over radius along the neck.
5. DC input resistance is a low-frequency descriptor and does not replace frequency-dependent impedance.
6. SMI normalizes neck resistance by dendritic load but does not include downstream dendrite-to-soma filtering.
7. Conductance-based synaptic transients depend on local driving force, capacitance, time step, and waveform kinetics; they cannot be inferred from SMI alone.
8. Active dendritic conductances, NMDA nonlinearities, calcium dynamics, and epilepsy-oriented extensions are out of scope for Phase 00 and must remain separate until their phases.
9. Literature evidence for electrical spine compartmentalization is context-dependent; SPINE should represent and test multiple regimes rather than assuming one universal answer.
