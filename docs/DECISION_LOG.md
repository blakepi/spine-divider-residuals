# Scientific and Software Decision Log

Add one entry for every important decision.

## Template

### YYYY-MM-DD - Decision

- **Phase:**
- **Status:** proposed / accepted / superseded
- **Question:**
- **Decision:**
- **Alternatives:**
- **Evidence:**
- **Scientific implications:**
- **Software implications:**
- **Validation required:**
- **Files affected:**

## Decisions

### 2026-06-09 - Use bounded Codex phases

- **Phase:** Project setup
- **Status:** accepted
- **Question:** How should a long, multidisciplinary build be executed reliably?
- **Decision:** Use one phase per Codex task/thread, persistent `AGENTS.md` guidance, Git checkpoints, tests, and phase ZIPs.
- **Alternatives:** One-shot chat build; one unbounded Codex task.
- **Evidence:** Earlier single-run attempts were interrupted and exhausted usage.
- **Scientific implications:** None directly.
- **Software implications:** Requires explicit project state and handoff artifacts.
- **Validation required:** Each phase must leave a runnable, documented checkpoint.
- **Files affected:** `AGENTS.md`, `tasks/`, `docs/PROJECT_STATE.md`.

### 2026-06-09 - Use Python 3.12+ with a small scientific stack

- **Phase:** 00
- **Status:** accepted
- **Question:** What language and base dependencies should the platform use?
- **Decision:** Use Python 3.12+ with NumPy, SciPy, pandas, matplotlib, and pytest. Keep any acceleration optional.
- **Alternatives:** MATLAB, Julia, prebuilt neuroscience simulators, broader Python stacks.
- **Evidence:** The master specification prefers Python 3.12+ for accessibility and reproducibility; NumPy/SciPy are verified general-purpose scientific dependencies; prohibited neuroscience simulators are excluded.
- **Scientific implications:** Supports transparent first-principles implementation while retaining sparse linear algebra for later phases.
- **Software implications:** Package uses `pyproject.toml` and `src/spine/` layout.
- **Validation required:** Run scaffold tests now; solver validation begins in Phase 01.
- **Files affected:** `pyproject.toml`, `src/spine/`, `docs/SCIENTIFIC_DECISIONS.md`.

### 2026-06-09 - Use SI internally and manuscript-facing TOML at boundaries

- **Phase:** 00
- **Status:** accepted
- **Question:** How should units be represented?
- **Decision:** Use SI internally, with explicit helpers converting manuscript-facing electrophysiology units at boundaries.
- **Alternatives:** Store all values in manuscript units internally; use an external unit package.
- **Evidence:** The master specification requires explicit unit checks; SI minimizes ambiguity; Phase 00 needs only lightweight conversion helpers.
- **Scientific implications:** Reduces risk of hidden conversion errors, especially for radius-squared neck resistance.
- **Software implications:** Added `spine.units` and TOML configs with explicit unit suffixes.
- **Validation required:** Unit conversion tests must pass; solver equations must continue to enforce units in later phases.
- **Files affected:** `src/spine/units.py`, `tests/test_units.py`, `docs/UNIT_AUDIT.md`.

### 2026-06-09 - Keep revised track initially unchanged

- **Phase:** 00
- **Status:** accepted
- **Question:** Should anomalous parameters be revised immediately?
- **Decision:** Preserve all manuscript values in `manuscript_faithful`; create `plausibility_revised` as a separate initially identical track until evidence-based revisions are tested.
- **Alternatives:** Revise likely questionable values immediately; maintain only one config.
- **Evidence:** Project instructions prohibit silent manuscript changes and require track separation.
- **Scientific implications:** Reproduction and later plausibility analyses remain distinguishable.
- **Software implications:** Two config directories exist with separate track metadata.
- **Validation required:** Later phases must compare tracks whenever revisions are introduced.
- **Files affected:** `configs/manuscript_faithful/baseline.toml`, `configs/plausibility_revised/baseline.toml`, `docs/SCIENTIFIC_DECISIONS.md`.

### 2026-06-09 - Assemble passive dynamics as C dV/dt = -A V + b

- **Phase:** 01
- **Status:** accepted
- **Question:** How should leak, synaptic, and axial signs be represented in code?
- **Decision:** Assemble `A` with positive diagonal conductance terms and negative off-diagonal axial couplings; assemble `b` from reversal-weighted leak/synaptic sources.
- **Alternatives:** Code each differential equation separately; use an opposite current sign convention.
- **Evidence:** This exactly matches the manuscript equations and gives correct behavior: rest remains at `E_L`, excitatory conductance depolarizes the head, and axial edge currents are equal and opposite.
- **Scientific implications:** The solver preserves manuscript sign conventions and supports current-balance tests.
- **Software implications:** Implemented in `spine.passive.assemble_passive_matrix`.
- **Validation required:** Rest equilibrium, excitatory depolarization, and backward-Euler residual tests.
- **Files affected:** `src/spine/passive.py`, `tests/test_phase01_passive_core.py`, `docs/MODEL_SPECIFICATION.md`.

### 2026-06-09 - Define Phase 01 metric window as 50 ms

- **Phase:** 01
- **Status:** accepted
- **Question:** What post-stimulus metric window should be used when the manuscript defines `T` symbolically?
- **Decision:** Use `T = 50 ms` after `t0` for Phase 01 metrics.
- **Alternatives:** Infer a window from figure captions; use the whole simulation; leave metrics undefined.
- **Evidence:** `50 ms` spans more than 16 manuscript decay time constants (`tau_d = 3 ms`) and was chosen before reproduction, so it is not tuned to match figures.
- **Scientific implications:** Metrics are deterministic and documented while reproduction discrepancies remain meaningful.
- **Software implications:** Added `numerics.metric_window_ms` to both configs and implemented metrics against that field.
- **Validation required:** Metric tests and Phase 02 reproduction audit.
- **Files affected:** `configs/manuscript_faithful/baseline.toml`, `configs/plausibility_revised/baseline.toml`, `src/spine/metrics.py`, `docs/MODEL_SPECIFICATION.md`.

### 2026-06-09 - Compute R_in,d in a separate spine-omitted two-node circuit

- **Phase:** 01
- **Status:** accepted
- **Question:** How should dendritic input resistance avoid circular dependence on the stimulated spine?
- **Decision:** Compute `R_in,d` from only the dendrite and soma nodes; the spine head and `g_hd` are absent in both steady-state and time-domain methods.
- **Alternatives:** Keep the spine attached but unstimulated; set neck conductance to zero in the three-node system.
- **Evidence:** Project instructions and manuscript specify the stimulated spine must be omitted.
- **Scientific implications:** Baseline SMI is `R_neck / R_in,d` where the load is independent of the same neck being normalized.
- **Software implications:** Implemented in `spine.impedance`.
- **Validation required:** Analytical two-node resistance and time-domain convergence tests.
- **Files affected:** `src/spine/impedance.py`, `tests/test_phase01_passive_core.py`.

### 2026-06-09 - Preserve ohm-cm resistivity at the geometry boundary

- **Phase:** 01.1
- **Status:** accepted
- **Question:** Should intracellular resistivity be stored only in SI inside `PassiveParameters`?
- **Decision:** Keep the manuscript-facing field `intracellular_resistivity_ohm_cm` and document it as a deliberate geometry-boundary exception. Geometry helpers convert micrometer morphology to centimeters and return resistance in ohms before solver use.
- **Alternatives:** Rename and convert the stored value to ohm-m; add a full units package.
- **Evidence:** The manuscript explicitly describes converting micrometer geometry to centimeters for resistance in ohms, and current code already centralizes this conversion.
- **Scientific implications:** Preserves faithful manuscript parameter expression while keeping solver matrices in ohms/siemens.
- **Software implications:** Documentation clarification only for resistivity storage; no solver-equation change.
- **Validation required:** Existing neck-resistance unit tests and Phase 01.1 tests.
- **Files affected:** `docs/UNIT_AUDIT.md`, `docs/MODEL_SPECIFICATION.md`, `reports/PHASE_01_1_REPORT.md`.

### 2026-06-09 - Clarify signed current and driving-force metrics

- **Phase:** 01.1
- **Status:** accepted
- **Question:** How should Phase 02 interpret synaptic current, neck current, and driving-force metrics?
- **Decision:** Document inward excitatory synaptic current as negative under the outward-current convention, positive neck current as head-to-dendrite, and add explicit absolute driving-force reduction metrics.
- **Alternatives:** Leave `peak_driving_force_V` as the only driving-force metric; convert all currents to positive magnitudes.
- **Evidence:** The Phase 01 audit found that signed currents were correct but underdocumented, and that peak absolute driving force did not directly capture reduction.
- **Scientific implications:** Prevents Phase 02 reports from confusing signed inward current with magnitude and avoids overinterpreting `peak_driving_force_V`.
- **Software implications:** Adds metric fields without changing solver dynamics.
- **Validation required:** Tests check positive driving-force reduction for the manuscript event.
- **Files affected:** `src/spine/metrics.py`, `tests/test_phase01_passive_core.py`, `docs/MODEL_SPECIFICATION.md`, `docs/TRACEABILITY_MATRIX.csv`.

### 2026-06-09 - Add programmatic validation guardrails

- **Phase:** 01.1
- **Status:** accepted
- **Question:** What parameter validity checks should exist before Phase 02 constructs parameter objects programmatically?
- **Decision:** Reject nonpositive passive parameters and invalid time windows; require time-domain `R_in,d` duration to span at least 10 dendrite-soma load time constants.
- **Alternatives:** Rely on TOML config validity and indirect numerical failures.
- **Evidence:** The Phase 01 audit identified implicit failure modes for invalid `dt_s`, `stop_s`, and short input-resistance duration.
- **Scientific implications:** Reduces risk of silent invalid Phase 02 reproductions.
- **Software implications:** Adds validation only; no change to valid manuscript baseline behavior.
- **Validation required:** Phase 01.1 unit tests for invalid time parameters and duration checks.
- **Files affected:** `src/spine/passive.py`, `src/spine/impedance.py`, `tests/test_phase01_passive_core.py`.

### 2026-06-09 - Use SVG-only scripted figures for Phase 02 in bundled runtime

- **Phase:** 02
- **Status:** accepted
- **Question:** How should manuscript reproduction figures be generated when matplotlib is unavailable in the bundled runtime?
- **Decision:** Generate editable SVG figures directly from scripted source data using standard-library file writing and NumPy-generated results.
- **Alternatives:** Require matplotlib installation; skip figures; generate only CSV.
- **Evidence:** The bundled runtime has NumPy but not matplotlib. The user required figures and source data, and editable vector output satisfies the scientific audit need.
- **Scientific implications:** Figures are generated from exact source data and remain inspectable, though they are not styled as final publication art.
- **Software implications:** Phase 02 reproduction does not require optional plotting dependencies.
- **Validation required:** Phase 02 tests verify expected figure/source-data files exist.
- **Files affected:** `src/spine/protocols.py`, `scripts/reproduce_manuscript.py`, `figures/phase02/`, `results/phase02/`.

### 2026-06-09 - Classify reproduction by explicit discrepancy thresholds

- **Phase:** 02
- **Status:** accepted
- **Question:** How should exact, approximate, and failed reproduction be distinguished?
- **Decision:** Use exact reproduction for absolute error <= 0.005 or relative error <= 2%; approximate for absolute error <= 0.05 or relative error <= 20%; otherwise failed reproduction.
- **Alternatives:** Use narrative-only classification; tune tolerances per figure.
- **Evidence:** Captioned values are reported to limited decimal precision, so fixed thresholds prevent post hoc tuning.
- **Scientific implications:** Disagreements would be retained as results rather than tuned away.
- **Software implications:** Classification is written into `caption_discrepancy_table.csv`.
- **Validation required:** Phase 02 tests ensure classifications are present and from the allowed set.
- **Files affected:** `src/spine/protocols.py`, `results/phase02/caption_discrepancy_table.csv`, `reports/MANUSCRIPT_REPRODUCTION.md`.

### 2026-06-09 - Fix Phase 03 SMI criteria before running challenge experiments

- **Phase:** 03
- **Status:** accepted
- **Question:** How should the project avoid tuning SMI challenge experiments after seeing results?
- **Decision:** Write `reports/PHASE03_HYPOTHESES.md` before implementation, including expected SMI successes, expected failures, competing predictors, success/failure thresholds, and falsification criteria.
- **Alternatives:** Define criteria narratively after the challenge suite; tune thresholds per outcome.
- **Evidence:** Phase 02 showed that fixed-load SMI is a scaled neck resistance, so Phase 03 needed predeclared counterexample criteria.
- **Scientific implications:** Negative SMI findings are preserved as valid scientific outcomes.
- **Software implications:** Phase 03 result tables include explicit falsification summaries.
- **Validation required:** Reports must compare observed outcomes against the predeclared criteria.
- **Files affected:** `reports/PHASE03_HYPOTHESES.md`, `src/spine/phase03.py`, `results/phase03/falsification_summary.csv`.

### 2026-06-09 - Use a first-principles passive graph engine for Phase 03

- **Phase:** 03
- **Status:** accepted
- **Question:** How should generalized passive morphologies be represented without using a prebuilt neuroscience simulator?
- **Decision:** Represent passive morphology as compartments plus axial edges, assemble a first-principles admittance matrix, and provide lightweight COO sparse storage with dense NumPy solves for the small Phase 03 networks.
- **Alternatives:** Use NEURON/Brian2/Arbor or another simulator; require SciPy sparse solvers immediately; keep only the three-compartment architecture.
- **Evidence:** Project instructions prohibit prebuilt neuroscience simulator foundations, and the bundled runtime does not provide the full optional scientific plotting/testing stack.
- **Scientific implications:** The matrix equations remain inspectable and equivalent to the passive circuit equations.
- **Software implications:** Adds `PassiveNetwork`, `SparseCOOMatrix`, procedural morphology builders, and SWC parsing.
- **Validation required:** Sparse/dense equivalence, SWC parser tests, spatial convergence checks.
- **Files affected:** `src/spine/compartments.py`, `src/spine/network.py`, `src/spine/morphology.py`, `tests/test_phase03_morphology_impedance.py`.

### 2026-06-09 - Treat DC SMI as local and test impedance alternatives

- **Phase:** 03
- **Status:** accepted
- **Question:** Should SMI be treated as a universal predictor outside the manuscript architecture?
- **Decision:** Treat DC SMI as a local low-frequency load-normalized descriptor, then compare it against `R_neck`, `R_in,d`, input/transfer impedance, transfer gain, electrotonic distance, area, capacitance, path length, and branch order.
- **Alternatives:** Assume SMI generalizes; evaluate only manuscript-like fixed-load sweeps.
- **Evidence:** Phase 02 fixed-load reproduction showed SMI and `R_neck` have identical rank order under fixed load.
- **Scientific implications:** Separates spine-to-dendrite coupling from downstream dendrite-to-soma filtering and makes counterexamples scientifically useful.
- **Software implications:** Adds predictor comparison tables and SMI challenge datasets.
- **Validation required:** Predictor correlations, iso-SMI falsification tests, source-data review.
- **Files affected:** `src/spine/phase03.py`, `reports/PHASE03_SMI_CHALLENGE_REPORT.md`, `reports/PHASE03_PREDICTOR_COMPARISON.md`.

### 2026-06-09 - Validate impedance with both sinusoidal and chirp time-domain checks

- **Phase:** 03
- **Status:** accepted
- **Question:** How should frequency-domain impedance calculations be cross-checked?
- **Decision:** Validate direct frequency-domain solves against steady-state sinusoidal simulations and a continuous logarithmic chirp with FFT-based transfer estimation.
- **Alternatives:** Use frequency-domain calculations without time-domain checks; use only independent single-tone simulations.
- **Evidence:** The Phase 03 task requires chirp and sinusoidal validation, and the first helper implementation was corrected from a tone sweep to a true logarithmic chirp before reporting.
- **Scientific implications:** Frequency-domain impedance metrics are supported by independent time-domain simulations within predeclared error limits.
- **Software implications:** Adds `sinusoidal_impedance_validation` and `chirp_impedance_validation`.
- **Validation required:** Amplitude/phase error thresholds in unit tests and reports.
- **Files affected:** `src/spine/impedance.py`, `src/spine/phase03.py`, `results/phase03/chirp_validation.csv`, `results/phase03/sinusoidal_validation.csv`, `reports/PHASE03_IMPEDANCE_REPORT.md`.

### 2026-06-09 - Keep Phase 04 active mechanisms opt-in

- **Phase:** 04
- **Status:** accepted
- **Question:** How should active mechanisms be added without altering the manuscript-faithful baseline?
- **Decision:** Add `configs/active_extension/baseline.toml` and require Phase 04 generation to run from an `active_extension` track. The manuscript-faithful TOML remains without active-channel sections.
- **Alternatives:** Add disabled active sections to `manuscript_faithful`; silently reuse the plausibility-revised track.
- **Evidence:** Project instructions require manuscript-faithful and revised/extension tracks to remain separate and active mechanisms to remain disabled in the manuscript baseline.
- **Scientific implications:** Passive reproduction remains unchanged and active results are explicitly extension results.
- **Software implications:** Active mechanisms are placed programmatically or via the active-extension config only.
- **Validation required:** Tests verify the active config is separate and manuscript-faithful lacks `active_channels`.
- **Files affected:** `configs/active_extension/baseline.toml`, `tests/test_phase04_active_nonlinear.py`, `reports/PHASE04_ACTIVE_VALIDATION.md`.

### 2026-06-09 - Use semi-implicit active integration with exponential gate updates

- **Phase:** 04
- **Status:** accepted
- **Question:** What nonlinear integration scheme is robust enough for tiny spine-head capacitance and active conductances?
- **Decision:** Use exponential Euler for gating variables and a semi-implicit voltage solve for conductances evaluated from the previous voltage/updated gates. Keep explicit Euler only as an independent limiting-case cross-check.
- **Alternatives:** Fully explicit Euler for all simulations; Newton iteration; external stiff-solver dependency.
- **Evidence:** Explicit Euler is unstable for low neck resistance and tiny head capacitance unless sub-microsecond steps are used. The semi-implicit path passed timestep refinement, rest stability, and strong-drive tests.
- **Scientific implications:** Active results are numerical simulations, not analytic reductions; explicit solver limitations are reported rather than hidden.
- **Software implications:** Adds `spine.active.simulate_active_network`.
- **Validation required:** Timestep refinement, independent solver cross-check, gate-bound audit, and strong-drive stability.
- **Files affected:** `src/spine/active.py`, `src/spine/phase04.py`, `reports/PHASE04_ACTIVE_VALIDATION.md`.

### 2026-06-09 - Treat Phase 04 active parameters as restrained generic mechanisms

- **Phase:** 04
- **Status:** accepted
- **Question:** Should Phase 04 active conductance densities be interpreted as calibrated biological values?
- **Decision:** Use restrained generic conductance settings to test how nonlinear mechanisms alter SMI conclusions, and document provenance without claiming cell-type calibration.
- **Alternatives:** Fit active densities to published cells; omit A-type/calcium until a full calibration phase; tune mechanisms to maximize SMI agreement.
- **Evidence:** Phase 04 asks how active mechanisms alter passive conclusions, while Phase 05 uncertainty/statistical work is explicitly out of scope.
- **Scientific implications:** Mechanism directionality and numerical behavior are validated, but biological amplitude claims remain limited.
- **Software implications:** Adds source/provenance strings to channel definitions and active validation reports.
- **Validation required:** Equation/unit tests and reports must distinguish validated, exploratory, and speculative quantities.
- **Files affected:** `src/spine/channels.py`, `references/references.bib`, `reports/PHASE04_ACTIVE_VALIDATION.md`.

### 2026-06-09 - Use frozen-gate active impedance only as exploratory

- **Phase:** 04
- **Status:** accepted
- **Question:** How should active impedance be explored without overclaiming a full linearized active system?
- **Decision:** Compute frozen-gate operating-point impedance as an exploratory diagnostic and label it as such. Do not include dynamic gate derivatives or fitted active impedance summaries in Phase 04.
- **Alternatives:** Implement full Jacobian/frequency-dependent gating linearization now; skip active impedance entirely.
- **Evidence:** The master specification allows operating-point impedance where mathematically defensible, and Phase 04 requires active impedance exploration but not Phase 05-style ranking/statistics.
- **Scientific implications:** Frozen-gate impedance can be compared with passive metrics but is not a complete active small-signal theory.
- **Software implications:** Adds `frozen_gate_impedance` and exports `active_impedance_operating_point.csv`.
- **Validation required:** Reports must label frozen-gate impedance as exploratory.
- **Files affected:** `src/spine/active.py`, `src/spine/phase04.py`, `reports/PHASE04_ACTIVE_VALIDATION.md`, `reports/PHASE04_ACTIVE_SMI_REPORT.md`.

### 2026-06-10 - Use a compact deterministic Phase 05 uncertainty audit

- **Phase:** 05
- **Status:** accepted
- **Question:** How should uncertainty and identifiability be added while prioritizing rigor over feature count?
- **Decision:** Use a predefined `96`-sample deterministic Latin-hypercube ensemble with fixed seeds, focused local sensitivities, radius-uncertainty propagation, practical degeneracy screens, predictor comparisons, and residual audits. Do not expand or retune the ensemble after seeing results.
- **Alternatives:** Run a larger but less validated sweep; add Sobol, posterior inference, or disease modules immediately; tune distributions to stabilize claims.
- **Evidence:** The Phase 05 task explicitly prioritizes robust uncertainty/statistical reliability, and the user requested scientific rigor over feature count.
- **Scientific implications:** Results are interpretable as a compact uncertainty audit, not a calibrated biological posterior.
- **Software implications:** Adds `src/spine/phase05.py`, `scripts/run_phase05.py`, `tests/test_phase05_sensitivity_statistics.py`, and Phase 05 source tables/figures.
- **Validation required:** Deterministic sampling, analytic sensitivity checks, bootstrap/CV seed checks, convergence check, and full unit test suite.
- **Files affected:** `src/spine/phase05.py`, `scripts/run_phase05.py`, `tests/test_phase05_sensitivity_statistics.py`, `results/phase05/`, `figures/phase05/`, `reports/PHASE05_*.md`.

### 2026-06-10 - Preserve failed SMI uncertainty convergence as a result

- **Phase:** 05
- **Status:** accepted
- **Question:** What should happen when the predefined global uncertainty convergence check fails?
- **Decision:** Report the failure directly and do not increase sample size, change distributions, or tune parameters after seeing the result.
- **Alternatives:** Increase `N` until all checks pass; change the convergence metric; omit the failed check from reports.
- **Evidence:** The 48-vs-96 median convergence check failed with value `0.18885434806962575` against threshold `0.10`, driven by SMI median shift. Most voltage-response medians were more stable.
- **Scientific implications:** Global SMI percentile summaries remain sample-size limited; this supports caution about SMI class and uncertainty claims.
- **Software implications:** `phase05_validation.csv` intentionally contains one failed validation row; tests verify the failure is visible.
- **Validation required:** Full reports must identify the failure and its driver.
- **Files affected:** `results/phase05/phase05_validation.csv`, `reports/PHASE05_UNCERTAINTY_REPORT.md`, `reports/PHASE_05_REPORT.md`, `tests/test_phase05_sensitivity_statistics.py`.

### 2026-06-10 - Treat Phase 05 somatic-transfer rankings as ensemble-dependent

- **Phase:** 05
- **Status:** accepted
- **Question:** How should Phase 05 handle the conflict between Phase 03-04 somatic-transfer rankings and the compact uncertainty ensemble?
- **Decision:** Classify broad somatic-transfer and impedance-outperformance claims as uncertain. Phase 05 found SMI to be the top univariate predictor for passive and active `Gamma_h_to_s`, while Phase 03-04 challenge suites favored impedance/transfer predictors.
- **Alternatives:** Force Phase 05 interpretation to match Phase 03-04; declare SMI generally rescued for somatic transfer.
- **Evidence:** Phase 05 `Gamma_h_to_s` SMI abs(Spearman) was `0.6442078133478025`; active `Gamma_h_to_s` SMI abs(Spearman) was `0.6964324470971243`. Residuals still carried strong capacitance/load structure and multivariable predictors improved CV error.
- **Scientific implications:** SMI is not a universal somatic predictor, but neither is "impedance always outperforms SMI" supported across every uncertainty ensemble.
- **Software implications:** Claim classification logic records these claims as `uncertain`.
- **Validation required:** Predictor report and claim robustness report must state the conflict explicitly.
- **Files affected:** `src/spine/phase05.py`, `results/phase05/claim_robustness.csv`, `reports/PHASE05_PREDICTOR_REPORT.md`, `reports/PHASE05_CLAIM_ROBUSTNESS.md`, `reports/PHASE05_MANUSCRIPT_GUIDANCE.md`.

### 2026-06-10 - Audit Phase 05 convergence with progressive deterministic ensembles

- **Phase:** 05.1
- **Status:** accepted
- **Question:** Was the Phase 05 `uncertainty_convergence_48_vs_96` failure an implementation error or a real sample-size limitation?
- **Decision:** Run a separate robustness audit at N=96, 192, 384, and 768 using the existing Phase 05 distributions and a deterministic seed convention. Preserve the original threshold and report any failures.
- **Alternatives:** Retune the Phase 05 threshold; replace the uncertainty model; ignore the failed validation; begin Phase 06.
- **Evidence:** Final 384-to-768 SMI median relative change was `0.012090835475659055`, and maximum final median change across tracked outputs was `0.029154415501181967`, both below `0.10`. LHS reproducibility, bootstrap reproducibility, and CV reproducibility passed.
- **Scientific implications:** The original Phase 05 failure was a real small-sample/partition warning for a skewed SMI distribution, not a solver defect. SMI uncertainty summaries are more defensible at N=768.
- **Software implications:** Adds a Phase 05.1 audit layer and cache-aware progressive sample outputs under `results/phase05_1/`.
- **Validation required:** Progressive convergence validation, reproducibility validation, ranking stability checks, counterexample prevalence stability, and full test suite.
- **Files affected:** `src/spine/phase05_1.py`, `scripts/run_phase05_1.py`, `tests/test_phase05_1_convergence_audit.py`, `results/phase05_1/`, `figures/phase05_1/`, `reports/PHASE05_1_*.md`.

### 2026-06-10 - Treat exact predictor ranking instability as a preserved negative result

- **Phase:** 05.1
- **Status:** accepted
- **Question:** How should Phase 05.1 handle a failed final predictor-ranking stability validation?
- **Decision:** Preserve the failure and interpret it narrowly. The best active local predictor changed between near-tied dynamic-SMI variants, so exact rank labels should not be overclaimed even though major conclusions remain stable.
- **Alternatives:** Collapse near-tied predictors into one family before validation; change the stability criterion; hide the failed validation row.
- **Evidence:** `final_ranking_stability_vs_previous_n` failed, while counterexample prevalence stability passed and final median convergence passed. At N=768, passive local transfer was led by `dynamic_SMI_abs_50Hz` with DC SMI still strong at abs(Spearman) `0.9384077670334999`.
- **Scientific implications:** Publication claims should emphasize predictor families and mechanistic interpretation, not exact top-rank labels.
- **Software implications:** Tests assert that the ranking instability remains visible in `phase05_1_validation.csv`.
- **Validation required:** Predictor stability report and claim reassessment must explicitly describe the failure.
- **Files affected:** `results/phase05_1/phase05_1_validation.csv`, `reports/PHASE05_1_PREDICTOR_STABILITY.md`, `reports/PHASE05_1_CLAIM_REASSESSMENT.md`, `tests/test_phase05_1_convergence_audit.py`.

### 2026-06-10 - Report SMI class labels as radius-sensitive threshold annotations

- **Phase:** 05.1
- **Status:** accepted
- **Question:** Are SMI class assignments stable enough for strong manuscript claims?
- **Decision:** Treat class labels as radius-sensitive threshold annotations, not robust biological categories.
- **Alternatives:** Use class labels without uncertainty; move thresholds after seeing flips; remove SMI class analysis.
- **Evidence:** At N=768, radius-induced class flip fraction was `0.23958333333333334`; intermediate-class flip fraction was `1.0`; flipped samples were closer to the low/intermediate boundary than the full population.
- **Scientific implications:** Continuous SMI is more stable than thresholded SMI classes. Manuscript class language must disclose measurement and threshold sensitivity.
- **Software implications:** Phase 05.1 exports radius-only uncertainty, class-flip prevalence, and boundary examples.
- **Validation required:** Radius report and manuscript impact report must preserve the class-instability result.
- **Files affected:** `results/phase05_1/radius_uncertainty_by_n.csv`, `results/phase05_1/radius_boundary_examples.csv`, `results/phase05_1/radius_only_uncertainty.csv`, `reports/PHASE05_1_RADIUS_UNCERTAINTY.md`, `reports/PHASE05_1_MANUSCRIPT_IMPACT.md`.

### 2026-06-10 - Keep epilepsy perturbations exploratory and separated

- **Phase:** 06
- **Status:** accepted
- **Question:** How should epilepsy/epileptogenesis-associated perturbations be represented without overclaiming disease relevance?
- **Decision:** Add a separate `epilepsy_exploratory` configuration family and a Phase 06 runner that uses literature-grounded, evidence-graded, restrained perturbation scenarios. Treat all results as model-level hypothesis generation and explicitly prohibit clinical, diagnostic, prognostic, therapeutic, and calibrated disease-parameter claims.
- **Alternatives:** Fold disease perturbations into `manuscript_faithful` or `active_extension`; add many broad biological mechanisms; tune multipliers to produce larger effects; claim disease mechanisms from scenario outputs.
- **Evidence:** The Phase 06 task required separation, literature support, uncertainty propagation, active/nonlinear perturbations, and no clinical or therapeutic claims. Phase 03-05.1 already showed SMI is a local descriptor with important amplitude, transfer, class-boundary, and active-regime limitations.
- **Scientific implications:** Phase 06 can generate falsifiable hypotheses about how morphology, HCN, potassium, AMPA/NMDA, and clustering might stress SMI, but it cannot establish epilepsy mechanisms or prevalence. Same-SMI active/channel/synaptic counterexamples are preserved as limitations.
- **Software implications:** Adds `configs/epilepsy_exploratory/`, `src/spine/phase06.py`, `scripts/run_phase06.py`, `tests/test_phase06_epilepsy_exploratory.py`, Phase 06 results/figures, and Phase 06 reports. Validated baseline/passive/active/Phase 05/Phase 05.1 behavior was not modified.
- **Validation required:** Scenario coverage, deterministic uncertainty design, finite active solutions, gating bounds, positive SI-derived resistances, no clinical-claim fields, focused Phase 06 tests, and the full unittest suite.
- **Files affected:** `configs/epilepsy_exploratory/`, `src/spine/phase06.py`, `scripts/run_phase06.py`, `tests/test_phase06_epilepsy_exploratory.py`, `results/phase06/`, `figures/phase06/`, `reports/PHASE06_*.md`, `reports/PHASE_06_REPORT.md`, `docs/PROJECT_STATE.md`, `docs/RESEARCH_LEDGER.csv`, `references/references.bib`.

### 2026-06-10 - Use a small deterministic Phase 06 uncertainty screen

- **Phase:** 06
- **Status:** accepted
- **Question:** How should Phase 06 balance uncertainty propagation with runtime-bounded active simulations?
- **Decision:** Use `N=8` deterministic Latin-hypercube samples per scenario as an explicit sensitivity screen after an initial `N=32` active-simulation generation attempt timed out at 120 seconds. Preserve the runtime limitation in reports and do not interpret the intervals as biological confidence intervals.
- **Alternatives:** Keep `N=32` and leave the phase unable to complete in the normal local runtime; reduce scenario/protocol coverage; replace active uncertainty with passive-only uncertainty; tune thresholds after seeing results.
- **Evidence:** The first full Phase 06 run with `N=32` timed out before completion. The `N=8` run completed, produced 99 finite active simulations, and passed all Phase 06 validation checks.
- **Scientific implications:** Phase 06 uncertainty results are adequate for screening mechanism sensitivity and same-SMI counterexamples, but not for rare-tail inference or stable fine-grained predictor ranking.
- **Software implications:** `configs/epilepsy_exploratory/baseline.toml` and `src/spine/phase06.py` record `uncertainty_samples_per_scenario = 8`; reports disclose this limit.
- **Validation required:** Deterministic reproducibility, finite solutions, gating bounds, and explicit limitation language.
- **Files affected:** `configs/epilepsy_exploratory/baseline.toml`, `src/spine/phase06.py`, `reports/PHASE06_UNCERTAINTY_AND_LIMITATIONS.md`, `reports/PHASE_06_REPORT.md`, `results/phase06/scenario_uncertainty_*.csv`.

### 2026-06-10 - Make Phase 07 a release and claim-control phase

- **Phase:** 07
- **Status:** accepted
- **Question:** What should the final build phase prioritize before scientific dissemination?
- **Decision:** Treat Phase 07 as a documentation, audit, traceability, reproducibility, and publication-packaging phase only. Do not add biological mechanisms or alter validated passive, active, uncertainty, or exploratory model behavior. Close stale documentation and release-readiness gaps instead.
- **Alternatives:** Add more analyses before release; rewrite scientific conclusions; tune release outputs to make SMI look stronger; begin future disease or posterior-inference work.
- **Evidence:** The Phase 07 task explicitly prioritizes reproducibility, documentation quality, scientific transparency, and final packaging over additional functionality. Phase 03-06 reports already contain enough scientific evidence for a restrained final claim set.
- **Scientific implications:** The final public claim is narrower and more defensible: SMI is a local low-frequency isolation descriptor, not a universal predictor of amplitude, somatic transfer, nonlinear response, or electrical equivalence.
- **Software implications:** Adds final audit, reproducibility, synthesis, publication, figure-index, claim-audit, future-work, and release documentation files; updates traceability and package readme metadata; adds release-package validation tests.
- **Validation required:** Complete unittest suite, release-package tests, configuration isolation checks, CLI smoke checks, checkpoint creation, and Git status review where available.
- **Files affected:** `reports/PHASE07_*.md`, `reports/FINAL_SCIENTIFIC_SYNTHESIS.md`, `reports/PUBLICATION_GUIDE.md`, `reports/FIGURE_INDEX.md`, `reports/FINAL_CLAIM_AUDIT.md`, `reports/FUTURE_WORK.md`, `README.md`, `INSTALL.md`, `QUICKSTART.md`, `CHANGELOG.md`, `docs/TRACEABILITY_MATRIX.csv`, `docs/PROJECT_STATE.md`, `docs/RESEARCH_LEDGER.csv`, `pyproject.toml`, `tests/test_phase07_release_package.py`.

### 2026-06-10 - Curate SMI claims by evidence class rather than optimism

- **Phase:** 07
- **Status:** accepted
- **Question:** How should final SMI claims be stated across contradictory and ensemble-dependent evidence?
- **Decision:** Use explicit claim classes: strongly supported, supported, ensemble-dependent, exploratory, uncertain, and contradicted. Preserve SMI local support, amplitude failure, equal-SMI non-equivalence, radius class fragility, and exploratory-only epilepsy boundaries.
- **Alternatives:** Present a single positive SMI narrative; demote negative findings to supplemental only; call somatic transfer universally failed or universally supported.
- **Evidence:** Phase 03-04 challenge suites, Phase 05 uncertainty, Phase 05.1 convergence, and Phase 06 exploratory scenarios all show different target- and ensemble-dependent behavior.
- **Scientific implications:** Final dissemination should foreground the domain of validity of SMI, not merely reproduce manuscript figures.
- **Software implications:** Adds `reports/FINAL_CLAIM_AUDIT.md` and cross-links claim language in README and publication guidance.
- **Validation required:** Release tests assert core claim classifications remain present.
- **Files affected:** `reports/FINAL_CLAIM_AUDIT.md`, `reports/FINAL_SCIENTIFIC_SYNTHESIS.md`, `reports/PUBLICATION_GUIDE.md`, `README.md`, `tests/test_phase07_release_package.py`.

### 2026-06-10 - Support top-level release config track metadata

- **Phase:** 07
- **Status:** accepted
- **Question:** Should release validation require all TOML config files to self-identify their track through the generic loader?
- **Decision:** Yes. Preserve the original `[meta].track` lookup and add a fallback to top-level `track` metadata, then add `track = "epilepsy_exploratory"` to the Phase 06 scenario TOML. This is a release/config-system repair, not a scientific model change.
- **Alternatives:** Leave Phase 06 TOML files reporting `unknown`; force Phase 06 configs into the older `[meta]` schema; special-case the CLI.
- **Evidence:** Phase 07 config-load audit initially reported `unknown` for Phase 06 TOML files, which would confuse a new researcher following release instructions.
- **Scientific implications:** None for validated simulation behavior. The change only improves configuration provenance and reproducibility.
- **Software implications:** `spine.config.load_config` now reads either `[meta].track` or top-level `track`.
- **Validation required:** Load every TOML file under `configs/`; run release-package tests and the full unittest suite.
- **Files affected:** `src/spine/config.py`, `configs/epilepsy_exploratory/scenarios.toml`, `tests/test_phase07_release_package.py`, `reports/PHASE07_REPRODUCIBILITY.md`, `reports/PHASE_07_REPORT.md`.

### 2026-06-10 - Target Journal of Computational Neuroscience first

- **Phase:** 08
- **Status:** accepted
- **Question:** Which journal best fits the final SPINE manuscript package?
- **Decision:** Use Journal of Computational Neuroscience as the primary target, eNeuro as the strong alternative, and Frontiers in Computational Neuroscience as the fallback.
- **Alternatives:** Submit first to eNeuro, Journal of Neuroscience, or Frontiers in Computational Neuroscience.
- **Evidence:** Official author pages showed that JCNS directly fits computational, theoretical, mathematical, software, and modeling neuroscience work and supports LaTeX submissions. eNeuro strongly supports methods/tools and negative results but has a code-package requirement at initial submission that intersects with the invention-disclosure boundary. JNeurosci is credible but would require more aggressive compression of the methodological contribution. Frontiers has strong computational fit but higher APC exposure.
- **Scientific implications:** The final manuscript can preserve enough methods, validation, and negative findings for the domain-of-validity argument.
- **Software implications:** Added a JCNS target variant while keeping a journal-neutral numbered master and eNeuro/Frontiers alternatives documented.
- **Validation required:** Journal compliance report and manuscript package tests.
- **Files affected:** `manuscript/JOURNAL_TARGET_ASSESSMENT.md`, `manuscript/target_journal.tex`, `reports/PHASE08_JOURNAL_COMPLIANCE.md`.

### 2026-06-10 - Frame the manuscript around SMI domain of validity

- **Phase:** 08
- **Status:** accepted
- **Question:** What central scientific thesis should organize the paper?
- **Decision:** Use the restrained claim that SMI is a useful low-frequency coordinate of local spine electrical isolation, but not a universal predictor of synaptic impact, and equal SMI does not imply electrical equivalence.
- **Alternatives:** Present SMI as a broadly predictive morphology index; emphasize only counterexamples; split passive, active, uncertainty, and exploratory work into disconnected papers immediately.
- **Evidence:** Phase 02-07 results consistently support local SMI usefulness while showing amplitude failure, somatic-transfer context dependence, radius class fragility, active/nonlinear counterexamples, and exploratory-only Phase 06 boundaries.
- **Scientific implications:** Positive, negative, ensemble-dependent, and exploratory findings are all preserved without unsupported novelty, disease, or clinical claims.
- **Software implications:** Manuscript prose, claim ledger, numerical verification, figures, tables, and reports all cross-reference validated source data.
- **Validation required:** Claim-to-source ledger checks, numerical verification report, and Phase 08 tests.
- **Files affected:** `manuscript/main_unblinded.tex`, `manuscript/main_blinded.tex`, `manuscript/CLAIM_TO_SOURCE_LEDGER.csv`, `manuscript/NUMERICAL_VERIFICATION_REPORT.md`, `reports/PHASE08_MANUSCRIPT_REPORT.md`.

### 2026-06-10 - Prepare blinded and unblinded packages without assuming review mode

- **Phase:** 08
- **Status:** accepted
- **Question:** Should a blinded package be created if JCNS does not visibly require double-anonymous review?
- **Decision:** Prepare both blinded and unblinded packages. Use the unblinded JCNS-target manuscript as the primary submission variant unless final journal instructions require blinding.
- **Alternatives:** Prepare only unblinded files; choose eNeuro first to force double-blind formatting; omit author placeholders until later.
- **Evidence:** The Phase 08 task explicitly requested blinded and unblinded variants, and eNeuro uses double-blind review. Blinded-source tests passed and no author-identifying strings are present in the blinded source checked by tests.
- **Scientific implications:** No change to scientific claims.
- **Software implications:** Maintains parallel manuscript entry points and package-content checklists.
- **Validation required:** Blinded-source hygiene test and author-confirmation checklist.
- **Files affected:** `manuscript/main_blinded.tex`, `manuscript/main_unblinded.tex`, `submission/BLINDED_PACKAGE_CONTENTS.md`, `submission/UNBLINDED_INTERNAL_PACKAGE_CONTENTS.md`, `tests/test_phase08_manuscript_package.py`.

### 2026-06-10 - Keep repository release private and license pending

- **Phase:** 08
- **Status:** accepted
- **Question:** Should Phase 08 create a public repository, push to GitHub, publish a DOI, or select a license?
- **Decision:** No. Prepare repository-release materials and archives only. Public release, preprint posting, repository visibility, DOI minting, and license selection require explicit author, PI, and institutional technology-transfer/intellectual-property approval.
- **Alternatives:** Choose an open-source license now; create a public GitHub repository; publish a Zenodo archive; omit release materials entirely.
- **Evidence:** The Phase 08 prompt explicitly prohibits public release, preprint posting, and license selection without approval, and the project has an invention-disclosure boundary.
- **Scientific implications:** The manuscript can describe intended reproducibility while avoiding unauthorized dissemination.
- **Software implications:** Added release-plan, repository-structure, citation, Zenodo-template, license-options, contributing, reproducibility, and checklist files without creating a remote or selecting a license.
- **Validation required:** Repository-release package tests, archive checksums, and Git/GitHub CLI status review.
- **Files affected:** `repository/`, `submission/DATA_AND_CODE_AVAILABILITY.md`, `reports/PHASE08_REPOSITORY_REPORT.md`, `checkpoints/`.

### 2026-06-10 - Record LaTeX compilation as pending when TeX is unavailable

- **Phase:** 08
- **Status:** accepted
- **Question:** How should build validation be reported when no TeX toolchain is visible in the current shell?
- **Decision:** Do not claim PDF compilation success. Provide build scripts, exact commands, and programmatic source validation; mark compilation as pending.
- **Alternatives:** Claim compile readiness without running TeX; remove LaTeX build requirements; install tools outside the managed environment.
- **Evidence:** `latexmk`, `pdflatex`, `bibtex`, `biber`, `tectonic`, and `make` were not visible on PATH. Phase 08 manuscript validation tests passed, but they are not a substitute for PDF compilation.
- **Scientific implications:** No scientific result depends on unverified PDF rendering.
- **Software implications:** Adds explicit build wrappers and a LaTeX validation report with pending compilation status.
- **Validation required:** Run the build scripts in an author environment with TeX installed before submission.
- **Files affected:** `manuscript/Makefile`, `manuscript/build.ps1`, `manuscript/build.sh`, `manuscript/BUILD_INSTRUCTIONS.md`, `manuscript/LATEX_VALIDATION_REPORT.md`.

### 2026-06-10 - Embed manuscript figures through generated PDF fallbacks

- **Phase:** Post-Phase-08 production/proof pass
- **Status:** accepted
- **Question:** How should placeholder figure boxes be replaced without requiring journal-side SVG compilation?
- **Decision:** Preserve curated SVG sources, generate manuscript-local PDF fallbacks from those SVGs with a small reportlab renderer, and embed the PDF assets using `\includegraphics`.
- **Alternatives:** Require LaTeX SVG support; generate raster-only PNGs; leave placeholders; install external conversion tools.
- **Evidence:** The production prompt requested real `\includegraphics` figures and preferred PDF conversion. Local CairoSVG, Inkscape, ImageMagick, and TeX tools were unavailable, but bundled Python provided reportlab and the repository SVGs used simple supported primitives.
- **Scientific implications:** No scientific data or claims changed; figure visuals are rendered from the already curated SVG sources.
- **Software implications:** Adds `manuscript/render_figure_pdfs.py`, `manuscript/figures_pdf/`, and `manuscript/supplement/figures_pdf/`; updates build wrappers and figure manifest paths.
- **Validation required:** Static includegraphics path validation, one-page PDF asset checks, focused manuscript-package tests, and final TeX rebuild in an author environment.
- **Files affected:** `manuscript/render_figure_pdfs.py`, `manuscript/preamble.tex`, `manuscript/sections/results.tex`, `manuscript/supplement/sections/*.tex`, `manuscript/FIGURE_SOURCE_MANIFEST.csv`, `manuscript/build.ps1`, `manuscript/build.sh`, `manuscript/Makefile`, `manuscript/BUILD_INSTRUCTIONS.md`.

### 2026-06-10 - Treat existing compiled PDFs as stale after production edits

- **Phase:** Post-Phase-08 production/proof pass
- **Status:** accepted
- **Question:** How should compiled PDFs be reported when TeX is unavailable after source edits?
- **Decision:** Do not claim post-edit compilation. Mark existing PDFs as stale pre-production outputs and require rebuild before circulation or submission.
- **Alternatives:** Leave PDFs unqualified; delete existing PDFs; claim source-level readiness as equivalent to PDF compilation.
- **Evidence:** Existing logs and PDFs predated replacement of `\sourcebox` placeholders. `powershell -ExecutionPolicy Bypass -File manuscript\build.ps1 all` failed because `pdflatex` is not available on PATH.
- **Scientific implications:** No scientific interpretation changes; submission readiness remains contingent on final TeX compilation.
- **Software implications:** Reports and project state identify the exact remaining build requirement.
- **Validation required:** Rebuild `main_unblinded`, `main_blinded`, `target_journal`, and `supplement` in a TeX-enabled environment and inspect logs/PDFs.
- **Files affected:** `manuscript/LATEX_VALIDATION_REPORT.md`, `manuscript/LATEX_PRODUCTION_AUDIT.md`, `manuscript/FORMATTING_FIX_REPORT.md`, `manuscript/PUBLISHER_PROOF_REPORT.md`, `docs/PROJECT_STATE.md`.

### 2026-06-10 - Treat revision R0 as planning only

- **Phase:** Revision R0
- **Status:** accepted
- **Question:** Should editorial-review triage directly revise manuscript prose, figures, analyses, or code?
- **Decision:** No. R0 is an audit and planning boundary only. It preserves the editorial review source, classifies issues, assigns later revision phases, records static-search findings, and updates state/decision logs without changing scientific results, validated code, manuscript prose, figure assets, citations, licenses, repository visibility, or submissions.
- **Alternatives:** Start rewriting the manuscript immediately; rebuild figures before reframing provenance; add literature before clarifying novelty and prior-manuscript terminology.
- **Evidence:** The R0 prompt explicitly prohibited manuscript revisions, code/results changes, analysis regeneration, figure rebuilds, citation additions, public repository creation, license selection, and submission.
- **Scientific implications:** Validated scientific conclusions remain unchanged while the revision risks are made explicit and auditable.
- **Software implications:** Adds `manuscript/revision_v2/` planning artifacts only.
- **Validation required:** Required R0 files exist; CSV parses; static searches are recorded; no journal-facing manuscript/source-data/figure/code edits are made during R0.
- **Files affected:** `manuscript/revision_v2/*`, `docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`.

### 2026-06-10 - Remove prior-manuscript framing in the next revision

- **Phase:** Revision R0
- **Status:** accepted
- **Question:** How should the revised manuscript describe the earlier manuscript and manuscript-faithful terminology?
- **Decision:** The earlier manuscript is hypothetical/internal only and must not be treated as a prior published, external, or citable manuscript. Future revision phases should replace terms such as `manuscript-faithful`, `reported caption values`, `prior manuscript`, and `reproduction of manuscript findings` with baseline reference configuration and pre-specified target-case verification language.
- **Alternatives:** Cite or describe the earlier manuscript as an external source; retain reproduction language; remove all baseline verification discussion without replacement.
- **Evidence:** The author provided an explicit instruction in the R0 prompt, and static searches found current journal-facing occurrences that require later cleanup.
- **Scientific implications:** The scientific contribution should be framed as domain-of-validity testing, counterexamples, uncertainty, active/nonlinear extensions, and predictor comparison built on classical neck-resistance/load concepts.
- **Software implications:** Legacy config/file identifiers may remain internally if changing them would risk validated code, but submitted prose should avoid the misleading frame.
- **Validation required:** R1 static search closure for prior-manuscript/reproduction terminology.
- **Files affected:** `manuscript/revision_v2/MANUSCRIPT_TERMINOLOGY_MAP.md`, `manuscript/revision_v2/EDITORIAL_REVIEW_RESPONSE_MATRIX.csv`.

### 2026-06-10 - Defer figure rebuild, literature additions, statistics repair, and administrative approvals to bounded revision phases

- **Phase:** Revision R0
- **Status:** accepted
- **Question:** How should the editorial review's figure, literature, statistics, methods, and submission-readiness requests be sequenced?
- **Decision:** Assign provenance/novelty reframing to R1, literature and bibliography repair to R2, statistical/methods specification to R3, figure reconstruction to R4, manuscript compression to R5, administrative/submission readiness to R6, LaTeX production to R7, and final hostile reviewer simulation to R8.
- **Alternatives:** Combine all revision work in one pass; prioritize visual polish before conceptual framing; perform broad new analyses before identifying exact statistical gaps.
- **Evidence:** The review spans distinct risk classes, and the R0 prompt requested phase-bounded planning.
- **Scientific implications:** This sequencing protects scientific rigor by resolving conceptual framing before citation, statistical, figure, and formatting changes.
- **Software implications:** No new biological mechanisms or analysis pipelines are introduced by R0.
- **Validation required:** Later phases must close assigned issues in `EDITORIAL_REVIEW_RESPONSE_MATRIX.csv` without crossing their boundaries.
- **Files affected:** `manuscript/revision_v2/REVISION_ACTION_PLAN.md`, `manuscript/revision_v2/FIGURE_REVISION_REQUIREMENTS.md`, `manuscript/revision_v2/STATISTICS_AND_METHODS_GAP_LIST.md`, `manuscript/revision_v2/LITERATURE_REVISION_QUEUE.md`, `manuscript/revision_v2/REVISION_RISK_REGISTER.md`.

### 2026-06-10 - Reframe manuscript around baseline target-case validation rather than external reproduction

- **Phase:** Revision R1
- **Status:** accepted
- **Question:** How should the manuscript describe the prior internal scaffold and the baseline passive cases?
- **Decision:** Remove the implication that a prior published or external manuscript was reproduced. Use baseline reference configuration, pre-specified reference target cases, and target-case validation language in the manuscript narrative and manuscript-adjacent ledgers.
- **Alternatives:** Retain reproduction/manuscript-faithful language; cite the internal scaffold as prior work; remove baseline validation entirely.
- **Evidence:** The R1 prompt and R0 fatal issue R0-F01 require removing prior-manuscript/reproduction framing. Static searches after R1 show `manuscript-faithful`, `reproduction`, `reproduced`, `reported caption`, and `caption targets` no longer occur in the comparable manuscript/supplement source scope, except technical legacy filenames/paths documented in R1 reports.
- **Scientific implications:** Baseline target cases remain scientifically useful as validation cases, but no longer imply an external source manuscript.
- **Software implications:** Legacy config/script/report paths remain unchanged to avoid code/config churn; descriptive manuscript prose now uses the revised terminology.
- **Validation required:** R1 terminology audit and future R2/R3 claim/citation/statistical review.
- **Files affected:** `manuscript/metadata.tex`, `manuscript/main_blinded.tex`, `manuscript/sections/*.tex`, `manuscript/tables/*.tex`, `manuscript/supplement/sections/*.tex`, `manuscript/CLAIM_TO_SOURCE_LEDGER.csv`, `manuscript/FIGURE_SOURCE_MANIFEST.csv`, `manuscript/TABLE_SOURCE_MANIFEST.csv`, `manuscript/NUMERICAL_VERIFICATION_REPORT.md`, `manuscript/revision_v2/R1_*`.

### 2026-06-10 - Present SMI as an operational load-normalized spine-neck descriptor

- **Phase:** Revision R1
- **Status:** accepted
- **Question:** Should SMI be framed as a novel biophysical law or as an operational descriptor grounded in classical cable/load logic?
- **Decision:** Frame SMI as an operational low-frequency load-normalized spine-neck descriptor, `R_neck / R_in,d`, grounded in classical voltage-divider/cable-theory reasoning. The contribution is the spine-omitted `R_in,d` definition, reproducible implementation, and systematic domain-of-validity/falsification analysis.
- **Alternatives:** Present SMI as a fundamentally new principle; avoid SMI terminology entirely; defer novelty framing to the literature phase.
- **Evidence:** R0 issue R0-M01 and R1 author decisions require distinguishing classical foundations from new contributions. Phase 02-05.1 results support local utility while contradicting universal amplitude/equivalence claims.
- **Scientific implications:** The manuscript is more defensible: SMI remains useful locally but is explicitly insufficient for head amplitude, universal somatic transfer, nonlinear response, and electrical equivalence.
- **Software implications:** No model behavior or scientific result changed.
- **Validation required:** R2 literature grounding and R3 statistical/methods specificity.
- **Files affected:** `manuscript/sections/abstract.tex`, `manuscript/sections/introduction.tex`, `manuscript/sections/discussion.tex`, `manuscript/sections/conclusions.tex`.

### 2026-06-10 - Keep exploratory perturbation scenarios supplemental and non-disease-validating

- **Phase:** Revision R1
- **Status:** accepted
- **Question:** How much exploratory Phase 06/epilepsy framing should remain in the main narrative during R1?
- **Decision:** Demote disease-adjacent framing in the main manuscript. Treat the separated exploratory perturbation scenarios as supplemental stress tests showing same-index/non-equivalent responses, not as disease validation, clinical inference, or mechanism ranking.
- **Alternatives:** Keep Phase 06 as a main narrative section; remove all exploratory perturbation material; expand disease claims.
- **Evidence:** R1 prompt explicitly requested minimizing Phase 06/epilepsy content in the main narrative. Phase 06 reports use N=8 sensitivity screens and explicitly make no clinical, diagnostic, prognostic, or therapeutic claims.
- **Scientific implications:** The main paper remains a general computational neuroscience domain-of-validity study.
- **Software implications:** No exploratory code or data changed.
- **Validation required:** R5 compression and R6 administrative cleanup.
- **Files affected:** `manuscript/sections/results.tex`, `manuscript/sections/discussion.tex`, `manuscript/tables/claim_summary.tex`, `manuscript/supplement/sections/exploratory_phase06.tex`.

### 2026-06-11 - Add requested Magee references without duplicating HCN/Ih entries

- **Phase:** Revision R2
- **Status:** accepted
- **Question:** How should the author-requested Magee references be incorporated without creating duplicates or overstating novelty?
- **Decision:** Add verified `Magee2000Review` and `MageeCook2000` to the manuscript bibliography and cite them where dendritic integration, classical neck/load logic, somatic EPSP location dependence, and downstream transfer are discussed. Keep existing `Magee1998` and `Magee1999` as the single HCN/Ih entries after verifying their DOI metadata.
- **Alternatives:** Add all four as new entries regardless of existing keys; leave Magee and Cook 2000 only in the broader reference library; cite the 1998/1999 entries only in the supplement.
- **Evidence:** Crossref verified DOI metadata for `10.1038/35044552`, `10.1038/78800`, `10.1523/JNEUROSCI.18-19-07613.1998`, and `10.1038/9158`. Static citation checks after R2 found all four requested Magee references present and cited.
- **Scientific implications:** The manuscript's dendritic-integration, somatic-transfer, and HCN/Ih framing is better supported while SMI remains framed as classical and operational rather than as a new biophysical law.
- **Software implications:** Bibliography and manuscript prose only; no code or model behavior changed.
- **Validation required:** Static BibTeX/citation check, manuscript-package tests, and later R7 LaTeX compilation.
- **Files affected:** `manuscript/references.bib`, `references/references.bib`, `manuscript/sections/introduction.tex`, `manuscript/sections/discussion.tex`, `manuscript/supplement/sections/active_mechanisms.tex`, `manuscript/revision_v2/R2_*`.

### 2026-06-11 - Correct the suspicious Major dendritic-spikes reference

- **Phase:** Revision R2
- **Status:** accepted
- **Question:** How should the bibliography handle the entry listed as Guy Major et al. with DOI `10.1038/nn1599`?
- **Decision:** Replace `Major2008DendriticSpikes` with `Jarsky2005DendriticSpikePropagation`, using the verified author list, year, volume, issue, pages, and DOI. Update the supplement citation to use the corrected key.
- **Alternatives:** Keep the old key but change only the author field; mark the entry pending author verification; remove the citation entirely.
- **Evidence:** Crossref verified DOI `10.1038/nn1599` as Jarsky, Roxin, Kath, and Spruston, "Conditional dendritic spike propagation following distal synaptic activation of hippocampal CA1 pyramidal neurons," Nature Neuroscience 8(12):1667-1676, 2005.
- **Scientific implications:** The separated exploratory supplement keeps dendritic active-threshold context while removing a bibliographic error that could undermine trust.
- **Software implications:** Bibliography and supplement citation only.
- **Validation required:** Static scan must show no remaining `Major2008DendriticSpikes` citation and no undefined citation keys.
- **Files affected:** `manuscript/references.bib`, `references/references.bib`, `manuscript/supplement/sections/exploratory_phase06.tex`, `manuscript/revision_v2/R2_*`.

### 2026-06-11 - Keep disease-related references supplement-only during R2

- **Phase:** Revision R2
- **Status:** accepted
- **Question:** Should exploratory epilepsy/disease references be added to or removed from the main manuscript during the literature repair phase?
- **Decision:** Do not add epilepsy-specific citations to the main text. Retain existing disease-related references only in the separated exploratory supplement while recording that R5 may compress or remove them if the exploratory module is further reduced.
- **Alternatives:** Move disease references into the main Discussion; remove all exploratory disease references immediately; expand disease literature coverage.
- **Evidence:** R1 intentionally minimized disease framing, and R2 static searches showed no epilepsy-specific main-text citation cluster. The supplement still cites the references for the separated exploratory perturbation context.
- **Scientific implications:** The manuscript remains a general computational neuroscience domain-of-validity study and does not drift toward unsupported disease validation.
- **Software implications:** No code or data impact.
- **Validation required:** Main-text citation audit and supplement citation audit.
- **Files affected:** `manuscript/supplement/sections/exploratory_phase06.tex`, `manuscript/revision_v2/R2_SUPPLEMENT_CITATION_AUDIT.md`, `manuscript/revision_v2/R2_MAIN_TEXT_CITATION_AUDIT.md`.

### 2026-06-11 - Treat unchanged legacy bibliography metadata as not fully reverified in R2

- **Phase:** Revision R2
- **Status:** accepted
- **Question:** Should R2 claim online verification of every pre-existing bibliography entry?
- **Decision:** No. R2 verifies the added, corrected, and author-requested references online and marks unchanged legacy references as `existing_unverified` in the verification table unless they were explicitly checked in R2.
- **Alternatives:** Claim all references were verified based only on prior repository state; spend R2 revalidating every historical DOI; remove unchanged references until verified.
- **Evidence:** R2's primary risk was missing Magee context, the suspicious Major/Jarsky entry, author-field placeholders, and targeted literature gaps. Static checks verified formatting, duplicate keys, DOI format, and citation coverage for all entries, but online metadata checks were focused on the R2 repair set.
- **Scientific implications:** The manuscript avoids inventing verification certainty while still repairing the bibliography issues that mattered for R2.
- **Software implications:** No code impact.
- **Validation required:** R2 verification table and cleanup report must distinguish verified from existing-unverified entries.
- **Files affected:** `manuscript/revision_v2/R2_REFERENCE_VERIFICATION_TABLE.csv`, `manuscript/revision_v2/R2_BIBLIOGRAPHY_CLEANUP_REPORT.md`.

### 2026-06-11 - Report manuscript-facing statistics with intervals and rounded display precision

- **Phase:** Revision R3
- **Status:** accepted
- **Question:** How should quantitative manuscript claims be reported after the statistical/methods audit?
- **Decision:** Keep exact values in source CSVs and ledgers, but report manuscript-facing values with rounded display precision and intervals where supported. Predictor rows now include Pearson, Spearman, deterministic bootstrap intervals, and cross-validated RMSE in the R3 audit tables. Prevalence rows now include Wilson intervals.
- **Alternatives:** Leave all high-precision source values in prose; report only point estimates; rerun primary simulations to create new statistical summaries.
- **Evidence:** `STATISTICS_AND_METHODS_GAP_LIST.md` identified excessive precision, missing intervals, and over-reliance on single ranking metrics. R3 derived summaries from existing Phase 03-05.1 outputs without modifying raw source data.
- **Scientific implications:** The manuscript more clearly separates exact source data from readable claims and reduces overconfidence in small-suite predictor rankings.
- **Software implications:** Adds `scripts/revision_v2/r3_statistical_summaries.py` and derived R3 result tables only; no validated solver behavior changed.
- **Validation required:** R3 CSV parse checks, precision scans, focused manuscript tests, and full unittest suite.
- **Files affected:** `manuscript/sections/*.tex`, `manuscript/tables/*.tex`, `manuscript/supplement/sections/*.tex`, `manuscript/revision_v2/R3_*`, `results/revision_v2/r3/*`, `manuscript/CLAIM_TO_SOURCE_LEDGER.csv`, `manuscript/TABLE_SOURCE_MANIFEST.csv`, `manuscript/NUMERICAL_VERIFICATION_REPORT.md`.

### 2026-06-11 - Treat target-case exact reproduction as a tolerance class, not bitwise identity

- **Phase:** Revision R3
- **Status:** accepted
- **Question:** How should the baseline target-case validation labels be described?
- **Decision:** Preserve the existing Phase 02 classification labels in source CSVs, but revise manuscript language to say the target cases passed a predefined tolerance-class rule. The rule is absolute error `<=0.005` or relative error `<=0.02` for the exact-reproduction class, absolute error `<=0.05` or relative error `<=0.20` for approximate reproduction, and failure otherwise.
- **Alternatives:** Continue using "exact" in prose without defining the tolerance; remove the validation classification labels; redefine thresholds after the fact.
- **Evidence:** `src/spine/protocols.py::_classification` defines the tolerance rule, and R3 precision review found "exact" wording could imply bitwise equality.
- **Scientific implications:** Baseline validation remains strong while avoiding overstated numerical precision.
- **Software implications:** Documentation and table wording only; no validation thresholds or solver outputs changed.
- **Validation required:** Static text review and R3 validation audit.
- **Files affected:** `manuscript/sections/results.tex`, `manuscript/tables/validation_summary.tex`, `manuscript/supplement/sections/numerical_validation.tex`, `manuscript/revision_v2/R3_BE_CN_AND_VALIDATION_AUDIT.md`.

### 2026-06-11 - Exclude target-derived leakage predictors from R3 active predictor summary

- **Phase:** Revision R3
- **Status:** accepted
- **Question:** Should `local_voltage_isolation` be allowed as a predictor for active `Gamma_h_to_d` in the R3 predictor audit?
- **Decision:** No. `local_voltage_isolation` is target-derived for local transfer and was removed from the active nonlinear suite predictor set before regenerating R3 audit tables.
- **Alternatives:** Keep the leakage predictor and report a perfect association; remove all active predictor re-analysis; rely only on pre-existing point-estimate tables.
- **Evidence:** Initial R3 derived audit showed `local_voltage_isolation` as a perfect active local-transfer predictor, revealing target leakage. Regenerated tables restored SMI as the best active local predictor with abs(Spearman) `0.924906`.
- **Scientific implications:** Predictor comparisons remain conservative and do not flatter circular descriptors.
- **Software implications:** R3 post-processing script changed only; primary model and raw outputs unchanged.
- **Validation required:** Regenerate R3 derived tables and inspect `R3_PREDICTOR_COMPARISON_AUDIT.csv`.
- **Files affected:** `scripts/revision_v2/r3_statistical_summaries.py`, `manuscript/revision_v2/R3_PREDICTOR_COMPARISON_AUDIT.csv`, `results/revision_v2/r3/r3_predictor_comparison_intervals.csv`.

### 2026-06-11 - Route figure provenance through manifests instead of printed captions

- **Phase:** Revision R4
- **Status:** accepted
- **Question:** How should journal-facing figures preserve reproducibility without cluttering captions with source paths?
- **Decision:** Rebuild all main and supplemental figures into `manuscript/figures_publication/` and remove source-path footers from printed captions. Keep source data, scripts, and asset provenance in `manuscript/FIGURE_SOURCE_MANIFEST.csv`, `manuscript/revision_v2/R4_FIGURE_QUALITY_AUDIT.csv`, and R4 reports.
- **Alternatives:** Leave source paths in captions; keep the old fragmented panel PDFs; regenerate primary simulations for new plots; defer figure reconstruction to a later production phase.
- **Evidence:** The editorial review and R0/R4 requirements identified unlabeled/low-quality figures and source-path caption clutter as submission risks. R4 static validation found 8 main publication includes, 9 supplement publication includes, non-empty SVG/PDF/PNG assets, and no source-path text in figure captions or SVG text.
- **Scientific implications:** Figure presentation improved while preserving negative findings, R3 intervals, radius class instability, and the passive/active domain-of-validity conclusions.
- **Software implications:** Added a deterministic R4 figure script and generated assets only; validated model code and raw simulation outputs were not modified.
- **Validation required:** R4 static asset/include/caption checks passed. Full TeX compilation remains pending because no TeX engine is available on PATH.
- **Files affected:** `scripts/revision_v2/r4_generate_publication_figures.py`, `manuscript/figures_publication/*`, `results/revision_v2/r4/figure_data_snapshots/*`, `manuscript/sections/results.tex`, `manuscript/supplement/sections/*.tex`, `manuscript/FIGURE_SOURCE_MANIFEST.csv`, `manuscript/revision_v2/R4_*`, `reports/PHASE_R4_REPORT.md`.

### 2026-06-11 - Compress the manuscript around SMI domain of validity

- **Phase:** Revision R5
- **Status:** accepted
- **Question:** How should the revised manuscript be shortened without weakening the science or turning it into a feature-count software report?
- **Decision:** Reorganize the paper as a compact computational neuroscience domain-of-validity article: six Methods subsections, seven science-first Results subsections, and four synthetic Discussion subsections. Retain all eight R4 main figures and four main tables, but remove development-phase narration, repeated Discussion claims, and file-index prose from journal-facing text. Keep detailed validation, uncertainty, active-parameter, and exploratory perturbation material in the supplement and traceability files.
- **Alternatives:** Preserve the comprehensive project-report manuscript; cut aggressively and risk underspecifying methods; move all exploratory material out of the package; start R6 administrative cleanup during R5.
- **Evidence:** R5 word-count audit reduced the main narrative from 6663 to 4459 conservative LaTeX-stripped words and reduced Discussion from 11 to 4 subsections. Static search showed the main scientific narrative is clean for phase/reproduction/internal-memo/disease terms. Focused manuscript tests and full unittest discovery passed.
- **Scientific implications:** The manuscript now emphasizes the central scientific contribution: SMI is a useful local low-frequency descriptor whose failures for amplitude, somatic transfer, active nonlinear response, thresholded classes, and equal-index equivalence define its domain of validity.
- **Software implications:** No validated model code, raw source data, primary analyses, or figure assets changed. Edits were limited to manuscript prose, table/caption wording, supplement terminology, manifest notes, reports, project state, and decision log.
- **Validation required:** Static search audit, word/structure audit, citation consistency check, figure include audit, focused manuscript-package tests, full unittest discovery, TeX/Git tool discovery, checkpoint creation.
- **Files affected:** `manuscript/sections/*.tex`, `manuscript/tables/*.tex`, `manuscript/supplement/sections/uncertainty_identifiability.tex`, `manuscript/supplement/sections/numerical_validation.tex`, `manuscript/FIGURE_SOURCE_MANIFEST.csv`, `manuscript/TABLE_SOURCE_MANIFEST.csv`, `manuscript/revision_v2/R5_*`, `reports/PHASE_R5_REPORT.md`, `docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`.

### 2026-06-11 - Move unresolved submission decisions out of manuscript body

- **Phase:** Revision R6
- **Status:** accepted
- **Question:** How should missing author, funding, conflict, ethics, repository, license, DOI, and institutional approval details be handled without inventing information or leaving internal scaffolding in the submitted manuscript?
- **Decision:** Remove raw bracketed placeholders and institutional action-item prose from the manuscript body. Use neutral manuscript draft language for pending administrative statements, and move unresolved decisions into explicit submission and repository checklists. Prepare private reviewer-access and disclosure options without publishing, selecting a license, creating a DOI, or submitting anything.
- **Alternatives:** Leave bracketed placeholders in the manuscript; invent no-funding/no-conflict/corresponding-author/repository statements; remove disclosure areas entirely; create a public repository or DOI during cleanup.
- **Evidence:** R0 and R5 identified administrative placeholders and IP/repository release language as submission blockers. R6 static search found no remaining placeholder/action-item hits in manuscript or supplement source files after cleanup, and focused/full tests passed.
- **Scientific implications:** The manuscript can circulate for author and institutional review without obscuring the scientific domain-of-validity message or implying unapproved release decisions.
- **Software implications:** No model code, source data, analyses, figures, or numerical claims changed. Submission and repository planning files now hold decision checklists and private-review plans.
- **Validation required:** Static placeholder audit, blinded-source identifier search, focused manuscript-package tests, full unittest discovery, TeX/Git tool discovery, checkpoint creation.
- **Files affected:** `manuscript/metadata.tex`, `manuscript/main_blinded.tex`, `manuscript/sections/acknowledgments.tex`, `manuscript/sections/disclosures.tex`, `manuscript/sections/data_code_availability.tex`, `submission/*`, `repository/PRIVATE_REVIEW_REPOSITORY_PLAN.md`, `manuscript/revision_v2/R6_*`, `reports/PHASE_R6_REPORT.md`, `docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`.

### 2026-06-11 - Treat R7 as source-package production when TeX is unavailable

- **Phase:** Revision R7
- **Status:** accepted
- **Question:** How should the LaTeX production phase proceed when no TeX engine or BibTeX tool is available in the execution environment?
- **Decision:** Harden the LaTeX sources and build wrappers, create build instructions and the JCNS source package, run static source/package validation, create required archives, and explicitly mark fresh compiled R7 PDFs and visual PDF QC as pending. Do not use stale pre-R7 PDFs as production outputs.
- **Alternatives:** Claim stale PDFs as R7 outputs; modify scientific content to simplify compilation; install a TeX distribution during R7; stop without packaging sources.
- **Evidence:** `pdflatex`, `bibtex`, `latexmk`, `tectonic`, `xelatex`, `lualatex`, and Perl were not visible on PATH or in common program directories. `powershell -ExecutionPolicy Bypass -File manuscript\build.ps1 all` failed cleanly with `pdflatex is not available on PATH.` Static validation found 27 TeX files, 34 used citations, 34 bibliography keys, 51 source-package files, and 0 errors; focused and full unittest suites passed.
- **Scientific implications:** None. R7 preserved model code, raw data, analyses, numerical results, figure scientific content, and scientific conclusions.
- **Software implications:** Build wrappers, LaTeX formatting safeguards, build documentation, submission package files, reports, and checkpoint archives were updated. TeX-enabled compilation and PDF visual inspection remain pending outside this environment.
- **Validation required:** TeX-enabled compile of `main_unblinded`, `main_blinded`, `target_journal`, and `supplement`; overfull/underfull log review; visual PDF QA; final source-package recheck if files change.
- **Files affected:** `manuscript/preamble.tex`, `manuscript/metadata.tex`, `manuscript/target_journal.tex`, `manuscript/sections/data_code_availability.tex`, `manuscript/supplement/supplement.tex`, `manuscript/supplement/sections/numerical_validation.tex`, `manuscript/supplement/sections/uncertainty_identifiability.tex`, `manuscript/build.ps1`, `manuscript/build.sh`, `manuscript/Makefile`, `LATEX_BUILD_INSTRUCTIONS.md`, `manuscript/BUILD_INSTRUCTIONS.md`, `submission/compiled_pdfs/README.txt`, `submission/jcns_source_package/README_BUILD.txt`, `manuscript/revision_v2/R7_*`, `reports/PHASE_R7_REPORT.md`, `docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`.

### 2026-06-11 - Restart revision sequence around analytic-divider residual framing

- **Phase:** Revision Restart Phase 0
- **Status:** accepted
- **Question:** How should the external pre-submission review be handled after completion of the old R0-R7 internal revision sequence?
- **Decision:** Close the old R0-R7 nomenclature and start a new `revision_restart` sequence. Phase 0 is planning only: preserve the external review, extract and classify every substantive critique, recommend an analytic-divider/residual-domain thesis, design Restart Phases 1-8, create decision queues and analysis requirements, run static searches, and stop before manuscript/code/analysis changes.
- **Alternatives:** Continue the old R8 reviewer simulation; immediately rewrite the manuscript; jump directly into Phase 1 residual analysis without triage; ignore the external review and proceed to submission.
- **Evidence:** The external review identifies a deeper organizing issue: the local SMI-transfer association is close to the classical divider relation `1/(1+SMI)`, so the paper should focus on residuals/departures, ratio-versus-components value, statistical reframing, external validation, and release readiness. Phase 0 extracted 30 issues and found publication-visible internal Fig. 1 text plus Wilson/bootstrap/prevalence and naming inconsistencies.
- **Scientific implications:** The next manuscript should treat the divider relation as the expected first-order behavior and make departures, limitations, and residual regimes the scientific contribution.
- **Software implications:** None to solver behavior. New planning artifacts live under `manuscript/revision_restart/`; no validated code, raw results, primary analyses, manuscript source, tables, bibliography, or figures were modified.
- **Validation required:** Phase 1 must derive the divider relation and compute residuals from existing data before broad manuscript rewriting; Phase 2 must compare ratio versus components; Phase 3 must fix statistical framing; Phase 4 must add external validation; Phase 5 must resolve release/reviewer-access approvals.
- **Files affected:** `manuscript/revision_restart/PHASE0_*`, `reports/PHASE_RESTART_0_REPORT.md`, `docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`.

### 2026-06-11 - Treat SMI local transfer as divider-limit ordering plus residuals

- **Phase:** Revision Restart Phase 1
- **Status:** accepted
- **Question:** How should the manuscript interpret the observed local SMI-to-`Gamma_h_to_d` relation after acknowledging the analytic voltage-divider identity?
- **Decision:** Treat `Gamma_h_to_d,divider = 1/(1+SMI)` as the first-order low-frequency local null expectation and make residuals from that divider the scientific object of interest. Retain SMI as a local isolation descriptor only with target, regime, and limitation qualifiers.
- **Alternatives:** Present the SMI association as a novel empirical prediction; remove the local SMI claim entirely; tune parameters or metric windows to make peak transfer match the divider; begin ratio-versus-components analysis immediately.
- **Evidence:** Restart Phase 1 generated 3718 residual rows from existing CSVs. Overall median absolute residual was 0.054751694, maximum absolute residual was 0.492427929, and 3680 of 3718 residuals were negative. Baseline residuals were -0.0072945027 (low), -0.1457867187 (intermediate), and -0.3285634789 (high). The largest departures came from the matched-neck heterogeneous-load sweep.
- **Scientific implications:** The revised manuscript should emphasize that SMI recovers expected local divider ordering while residuals expose transient conductance, morphology, impedance, active-state, and load regimes where the scalar ratio is insufficient. The divider itself is not the novelty.
- **Software implications:** Added a deterministic post-processing script and derived Phase 1 artifacts only. Validated model code, raw result CSVs, primary analyses, manuscript scientific source, tables, and publication figures were preserved.
- **Validation required:** Phase 2 must compare the SMI ratio against `R_neck`, `R_in,d`, the analytic divider transform, and residual predictors without conflating ratio algebra with independent predictive value.
- **Files affected:** `scripts/revision_restart/phase1_divider_residual_analysis.py`, `results/revision_restart/phase1/*`, `manuscript/revision_restart/PHASE1_*`, `reports/PHASE_RESTART_1_REPORT.md`, `docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`, `checkpoints/SPINE_restart_phase_1_checkpoint.zip`.

### 2026-06-12 - Treat SMI as an interpretable divider coordinate, not a universally superior predictor

- **Phase:** Revision Restart Phase 2
- **Status:** accepted
- **Question:** Does the load-normalized ratio add enough predictive value to be preferred over its component resistances?
- **Decision:** Present SMI as a compact and interpretable coordinate for the low-frequency local divider expectation, while using the analytic divider transform for first-order local-transfer prediction and richer component, conductance, dynamic, or impedance descriptors when residual precision, amplitude, or somatic transfer matters.
- **Alternatives:** Claim SMI is generally the best predictor; abandon SMI entirely; use the two component resistances for all targets without retaining the compact ratio.
- **Evidence:** Phase 2 generated a 3,718-row standardized descriptor table. In non-exploratory local-transfer rows, raw SMI and `Gamma_divider` had identical absolute Spearman association (0.948576), but `Gamma_divider` had better scalar CV RMSE than raw SMI (0.051987 versus 0.091467). The log component pair improved over raw SMI (CV RMSE 0.071815) but did not beat the divider transform. Dynamic SMI and transfer-gain models performed best where impedance descriptors existed. Residuals, amplitude, and somatic transfer were better explained by dynamic/impedance, component, and conductance descriptors than by raw SMI alone.
- **Scientific implications:** The revised manuscript should not frame the ratio as a new empirical law or universal predictor. The scientific contribution shifts to the operational load definition, analytic-divider null, residual-domain map, and target-specific descriptor boundaries.
- **Software implications:** Added deterministic post-processing only. No validated model code or raw source data changed.
- **Validation required:** Phase 3 must recast ranking and CV language as descriptive, not inferential, and remove overstrong "best predictor" wording from manuscript-facing text.
- **Files affected:** `scripts/revision_restart/phase2_descriptor_value_analysis.py`, `results/revision_restart/phase2/*`, `manuscript/revision_restart/PHASE2_*`, `reports/PHASE_RESTART_2_REPORT.md`, `docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`.

### 2026-06-12 - Retain spine-omitted R_in,d as an operational convention despite negligible attached-load differences in current rows

- **Phase:** Revision Restart Phase 2
- **Status:** accepted
- **Question:** Is the spine-omitted dendritic input resistance definition materially different from a spine-attached measurement in available models?
- **Decision:** Retain the spine-omitted definition as the conceptually clean operational convention, but report that Phase 2's available passive-head DC reconstruction found negligible numerical differences from a spine-attached load.
- **Alternatives:** Claim the omitted definition has large numerical effects; drop the omitted convention; rerun primary ensembles with attached-load measurement.
- **Evidence:** No raw CSV contained both omitted and attached `R_in,d`. Phase 2 computed a deterministic DC one-port reconstruction for 3,702 rows using existing `R_neck`, omitted `R_in,d`, and passive head leak. Median relative attached-minus-omitted `R_in,d` difference was -1.528e-6, median SMI relative change was 1.528e-6, and 0/3,702 SMI class assignments changed.
- **Scientific implications:** The convention's value is avoiding circular normalization and clarifying the load, not demonstrating a large numerical correction in the current compact passive-head model family. Dense spine populations or active attached-spine states remain future work.
- **Software implications:** Derived analysis only; no primary simulations or validated utilities were modified.
- **Validation required:** Later manuscript text should caveat the attached-versus-omitted result as a DC one-port reconstruction rather than full reassembly of every network.
- **Files affected:** `results/revision_restart/phase2/phase2_spine_omitted_vs_attached_rind.csv`, `manuscript/revision_restart/PHASE2_DESCRIPTOR_VALUE_ANALYSIS_REPORT.md`, `manuscript/revision_restart/PHASE2_CLAIM_REASSESSMENT.md`, `docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`.

### 2026-06-12 - Reframe deterministic sensitivity statistics as descriptive design summaries

- **Phase:** Revision Restart Phase 3
- **Status:** accepted
- **Question:** How should intervals, percentages, and predictor rankings from deterministic ensembles and designed cases be described?
- **Decision:** Treat Latin-hypercube rows, designed challenge cases, eligible-pair counterexamples, and row-level cross-validation as deterministic design analyses. Remove Wilson/binomial confidence-interval language from deterministic design fractions, rename bootstrap intervals over designed rows as deterministic stability ranges, replace "prevalence" with "fraction of sampled parameter combinations," and replace exact "best predictor" language with descriptor-family and target-specific language.
- **Alternatives:** Keep confidence-interval and prevalence language; drop all uncertainty summaries; develop a full probabilistic model during Phase 3.
- **Evidence:** Phase 3 generated 712 statistical-language audit rows, 50 interval-classification rows, 122 descriptive sensitivity summaries, 85 predictor-family rows, and 8 claim-reframing rows. Thirty Wilson/binomial rows were classified as inappropriate or misleading for deterministic design fractions, and 14 bootstrap predictor rows were classified as stability intervals over designed rows rather than confidence intervals.
- **Scientific implications:** The revised manuscript should commit to sensitivity-analysis language unless a later phase adds a justified sampling model. The results remain useful as domain-of-validity and stress-test evidence but should not be presented as biological population inference.
- **Software implications:** Added deterministic post-processing only. No validated model code or raw source data changed.
- **Validation required:** Phase 6 manuscript rewrite must use the Phase 3 audit and claim-reframing table to remove inferential-looking language from manuscript-facing claims.
- **Files affected:** `scripts/revision_restart/phase3_statistical_reframing.py`, `results/revision_restart/phase3/*`, `manuscript/revision_restart/PHASE3_*`, `reports/PHASE_RESTART_3_REPORT.md`, `docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`.

### 2026-06-12 - Scope high-SMI uncertainty claims instead of launching a new ensemble in Phase 3

- **Phase:** Revision Restart Phase 3
- **Status:** accepted
- **Question:** Does the existing deterministic uncertainty ensemble cover the high-SMI regime, and should Phase 3 run a new diagnostic extension?
- **Decision:** Do not run a new high-SMI diagnostic during Phase 3. Report the coverage limitation explicitly: the N=768 deterministic uncertainty ensemble covers sampled low/intermediate SMI combinations and contains no high-SMI rows, while high-SMI examples are present only in reference and designed challenge datasets.
- **Alternatives:** Launch a new high-SMI ensemble during Phase 3; ignore the high-SMI gap; treat designed high-SMI rows as uncertainty coverage.
- **Evidence:** Phase 3 high-SMI coverage audit found that `results/phase05_1/global_uncertainty_samples_N768.csv` has SMI range 0.015345 to 0.316648, with 757 low-SMI rows, 11 intermediate-SMI rows, and 0 high-SMI rows. Existing reference and designed datasets do include high-SMI rows, but they are not uncertainty ensemble coverage.
- **Scientific implications:** Uncertainty and class-fragility claims must be scoped to sampled low/intermediate SMI combinations. High-isolation statements should rely on reference/designed cases unless a later, clearly labeled high-SMI diagnostic is authorized.
- **Software implications:** No new primary ensemble or simulation output was generated. Phase 3 remains a post-processing and reframing phase.
- **Validation required:** Later manuscript text should state this limitation explicitly; any future high-SMI extension must be labeled as a separate diagnostic, not part of the original uncertainty ensemble.
- **Files affected:** `results/revision_restart/phase3/phase3_high_smi_coverage_audit.csv`, `manuscript/revision_restart/PHASE3_HIGH_SMI_COVERAGE_REPORT.md`, `manuscript/revision_restart/PHASE3_MANUSCRIPT_INSERT_DRAFT.md`, `docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`.

### 2026-06-12 - Use independent direct-matrix and analytic validation when NEURON is unavailable

- **Phase:** Revision Restart Phase 4
- **Status:** accepted
- **Question:** How should the external-validation critique be addressed when NEURON is not available in the execution environment?
- **Decision:** Check NEURON availability first, record its absence honestly, and use a separated independent direct-matrix benchmark plus DC analytic checks as the executed fallback validation. Retain NEURON as an optional future validation dependency only, not a required SPINE runtime dependency.
- **Alternatives:** Install NEURON during the phase; skip external/independent validation; claim BE-vs-CN is sufficient; modify production solver code to ease cross-validation; claim NEURON validation without running it.
- **Evidence:** The bundled Python runtime returned `None` for `importlib.util.find_spec('neuron')`. The independent direct-matrix benchmark reproduced the existing SPINE low/intermediate/high baseline traces to numerical roundoff, with maximum all-trace voltage difference `1.249e-13` mV. The DC analytic benchmark matched the closed-form two-node `R_in,d` to within `2.98e-14` MOhm, produced the expected divider limits, and found attached passive one-port `R_in,d` differences of about `-6.67e-07` relative. BE-vs-CN peak differences remained small but were classified as internal self-consistency only.
- **Scientific implications:** The passive baseline implementation is more computationally credible than before Phase 4, but the manuscript must not claim NEURON validation. The validation claim should be scoped to passive three-compartment reference cases and separated from active, morphology, uncertainty, or exploratory extensions unless those are independently benchmarked later.
- **Software implications:** Added separated validation scripts and derived outputs only. No validated model code, raw result CSVs, manuscript TeX source, tables, publication figures, release state, license state, DOI state, repository publication, preprint, or submission state changed.
- **Validation required:** Later manuscript text should describe independent matrix/analytic validation accurately and identify NEURON cross-validation as optional/future unless actually performed. Future NEURON work must document the lumped-circuit mapping and avoid tuning parameters silently.
- **Files affected:** `scripts/revision_restart/phase4_independent_matrix_benchmark.py`, `scripts/revision_restart/phase4_validation_runner.py`, `results/revision_restart/phase4/*`, `manuscript/revision_restart/PHASE4_*`, `reports/PHASE_RESTART_4_REPORT.md`, `docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`.

### 2026-06-12 - Stage reviewer-access packages without public release decisions

- **Phase:** Revision Restart Phase 5
- **Status:** accepted
- **Question:** How should SPINE address reviewer-access code/data release readiness without prematurely creating a public release, DOI, or license commitment?
- **Decision:** Create curated blinded and unblinded internal package drafts with manifests, checksums, environment instructions, test instructions, bounded reproduction instructions, and identifier audits. Keep license selection, DOI minting, repository publication, public archiving, preprint submission, and manuscript-source editing out of Phase 5.
- **Alternatives:** Package the entire working tree; expose LaTeX logs and local build products; create a public repository; choose a license immediately; defer all code/data readiness until after peer review; manually copy files without manifests or checksums.
- **Evidence:** Phase 5 generated `submission/reviewer_access_package/blinded_spine_review_package/` with 275 files and 0 blinded text identifier hits, plus `submission/reviewer_access_package/unblinded_internal_release_candidate/` with 279 files. The blinded archive SHA-256 is `efaca101ecbd3df262f502f5c24e3b55012cbbf70c06c09d351226eefeaa428c`; the unblinded internal archive SHA-256 is `42caa289d4d7e45838a67b2de0b9b1f679ea2a8aeec49695a04967bd57cdeaf0`. Protected-file hash comparison found 0 changed or missing protected files.
- **Scientific implications:** Reviewers can be given a bounded package containing implementation, configuration, tests, selected source-data outputs, validation artifacts, and provenance tables without implying that public archival, licensing, or DOI decisions have been finalized.
- **Software implications:** Added a separated packaging script and generated package artifacts only. Validated model code, raw result CSVs, manuscript TeX source, manuscript tables, publication figures, public repository state, license state, DOI state, preprint state, and submission state were preserved.
- **Validation required:** Before any actual reviewer distribution or public release, rerun the package builder from a clean state, rerun the blinded identifier audit, verify archive checksums, and resolve license/IP/repository decisions.
- **Files affected:** `scripts/revision_restart/phase5_prepare_review_packages.py`, `reproducibility_review_package/*`, `submission/reviewer_access_package/*`, `results/revision_restart/phase5/*`, `manuscript/revision_restart/PHASE5_*`, `reports/PHASE_RESTART_5_REPORT.md`, `docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`.

### 2026-06-12 - Make the Phase 7 manuscript rewrite a controlled execution of the divider-residual thesis

- **Phase:** Revision Restart Phase 6
- **Status:** accepted
- **Question:** How should the external review and Restart Phases 1-5 be synthesized before editing manuscript source?
- **Decision:** Treat Phase 6 as a planning and synthesis phase only. Finalize the manuscript rewrite thesis as follows: the load-normalized spine-neck ratio recovers the classical local voltage-divider expectation in the appropriate low-frequency limit, while SPINE's contribution is quantifying residual departures and identifying when transient conductance dynamics, impedance, active mechanisms, morphology, and measurement uncertainty make the scalar descriptor insufficient. Recommend `load-normalized spine-neck ratio` as the lead term and retain `SMI` only as author-defined shorthand if needed.
- **Alternatives:** Begin manuscript TeX edits immediately; keep "Spine Morphology Index" as the lead title phrase; frame local SMI association as a novel empirical discovery; claim NEURON validation; claim public release/DOI/license from the Phase 5 package draft; defer all reviewer-response planning to the manuscript-edit phase.
- **Evidence:** Phase 1 derived `Gamma_divider = 1/(1+SMI)` and found 3718 residual rows with median absolute residual 0.0548 and maximum residual 0.4924. Phase 2 showed the ratio is a compact coordinate rather than a generally superior predictor, with components and dynamic/conductance descriptors needed for residuals and nonlocal targets. Phase 3 reclassified deterministic sensitivity percentages and found the N=768 uncertainty ensemble has zero high-SMI rows. Phase 4 added independent direct-matrix and DC analytic validation while recording NEURON unavailability. Phase 5 prepared blinded and unblinded reviewer package drafts without public release decisions.
- **Scientific implications:** Phase 7 should rewrite the manuscript around analytic expectation plus residual-domain mapping, not around a standalone positive correlation. The revised manuscript should present deterministic design fractions as design-specific, state high-SMI uncertainty limits, scope validation to what was actually run, and preserve active/exploratory restraint.
- **Software implications:** Added Phase 6 synthesis and planning artifacts only. Validated model code, raw result CSVs, manuscript TeX source, manuscript tables, publication figures, public repository state, license state, DOI state, preprint state, and submission state were preserved.
- **Validation required:** Phase 7 must edit manuscript source according to the Phase 6 blueprints, then run static overclaim/language searches, protected-file checks, table/ledger CSV parsing, unittest discovery where feasible, and production checks if TeX tools are available.
- **Files affected:** `manuscript/revision_restart/PHASE6_*`, `reports/PHASE_RESTART_6_REPORT.md`, `results/revision_restart/phase6/phase6_protected_hashes_before.csv`, `docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`.

### 2026-06-12 - Rewrite the manuscript around divider residuals and scoped computational credibility

- **Phase:** Revision Restart Phase 7
- **Status:** accepted
- **Question:** How should the actual manuscript source be rewritten after the restart analyses and external-review synthesis?
- **Decision:** Rewrite the manuscript as a residual-domain analysis of a load-normalized spine-neck ratio. Lead with the analytic local divider `Gamma_div = 1/(1+SMI)`, present the residual from that divider as the main scientific object, use descriptor-family and target-specific language, remove deterministic population-inference wording, state the high-SMI uncertainty gap, and scope computational credibility to independent direct-matrix/DC analytic validation plus internal BE-vs-CN checks. Do not claim NEURON validation or public release.
- **Alternatives:** Keep the old SMI-success manuscript; claim SMI as a universal or generally superior predictor; retain Wilson/prevalence/best-predictor wording; claim NEURON validation; defer the actual TeX rewrite to a later phase; remove SMI entirely instead of keeping it as a compact author-defined shorthand.
- **Evidence:** Phase 1 found 3718 residual rows with median absolute residual 0.0548, maximum absolute residual 0.4924, and 3680 negative residuals. Phase 2 showed the analytic divider is the appropriate compact local-transfer transform while component/dynamic/conductance descriptors are needed for residuals and nonlocal targets. Phase 3 found the N=768 uncertainty ensemble has 757 low, 11 intermediate, and zero high-SMI rows. Phase 4 independent direct-matrix validation reproduced baseline traces to `1.249e-13` mV maximum all-trace difference and DC analytic checks matched `R_in,d` to roundoff. Phase 5 prepared reviewer package drafts without public release decisions.
- **Scientific implications:** The manuscript now makes the divider expected and the residuals informative. The load-normalized ratio remains useful as a local divider coordinate, but head amplitude, somatic transfer, active response, residual precision, categorical classes, and equivalence claims require richer descriptors and explicit uncertainty scope.
- **Software implications:** Added a separated Phase 7 figure-generation script and derived Phase 7 outputs only. No validated model/runtime code, configs, raw result CSVs, or broad primary ensembles changed. Manuscript source, tables, supplement source, ledgers, manifests, bibliography cleanup, and publication figure assets were changed intentionally for the rewrite.
- **Validation completed:** Phase 7 script compiled and ran; CSV ledgers/manifests parsed; protected hash comparison found 0 changed/missing/added protected files outside Phase 7 outputs; 63 unit tests passed; unblinded, blinded, target-journal, and supplement PDFs built with direct `pdflatex`/`bibtex`; static language audit and blinded identifier scan passed with only pending/not-claimed availability caveats remaining.
- **Files affected:** `manuscript/metadata.tex`, `manuscript/main_blinded.tex`, `manuscript/main_unblinded.tex`, `manuscript/target_journal.tex`, `manuscript/sections/*`, `manuscript/supplement/*`, `manuscript/tables/*`, `manuscript/references.bib`, `manuscript/CLAIM_TO_SOURCE_LEDGER.csv`, `manuscript/FIGURE_SOURCE_MANIFEST.csv`, `manuscript/TABLE_SOURCE_MANIFEST.csv`, `manuscript/NUMERICAL_VERIFICATION_REPORT.md`, `manuscript/figures_publication/Fig3_divider_residuals.*`, `scripts/revision_restart/phase7_generate_divider_residual_figure.py`, `results/revision_restart/phase7/*`, `manuscript/revision_restart/PHASE7_*`, `reports/PHASE_RESTART_7_REPORT.md`, `docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`.

### 2026-06-12 - Advance to PI/coauthor review, not journal submission, after Phase 8 QA

- **Phase:** Revision Restart Phase 8
- **Status:** accepted
- **Question:** Is the rewritten analytic-divider/residual-domain manuscript ready for submission after final QA and hostile reviewer simulation?
- **Decision:** Treat the manuscript as ready for PI/coauthor review but not yet ready for journal submission. Require a synchronized reviewer-access package rebuild and final administrative metadata/repository/archive/license decisions before any submission or reviewer distribution.
- **Alternatives:** Submit immediately after PDF QA; block even internal review until package rebuild; restart the manuscript rewrite; claim the older Phase 5 packages are current enough for reviewers.
- **Evidence:** Phase 8 rebuilt and inspected the unblinded, blinded, target-journal, and supplement PDFs; static PDF audit found no old internal phase tags, placeholders, local paths, NEURON-validation overclaim, Wilson/confidence/prevalence language, "SMI predicts," "best predictor," "Spine Morphology Index," or "epileptogenesis"; blinded identifier scanning found 0 word-boundary hits; package checksums still match their sidecars; package synchronization audit found that Phase 5 packages predate Phase 7/8 manuscript, figure, ledger, and numerical-verification changes; protected model/config/result hash comparison found 189 unchanged, 0 changed, and 0 missing paths; full unittest discovery passed 63 tests.
- **Scientific implications:** The revised scientific frame is now coherent enough for senior author review: SMI is a load-normalized local divider coordinate, residuals carry the domain-of-validity result, high-SMI uncertainty limits are disclosed, and computational credibility is scoped to the independent matrix/DC analytic and internal BE-vs-CN evidence actually run.
- **Software implications:** Added a separated Phase 8 QA audit script and derived QA outputs. Minor manuscript/figure/table production fixes were made, but validated model code, raw result CSVs, broad primary ensembles, public repository state, license state, DOI state, preprint state, and submission state were preserved.
- **Validation required:** Before journal submission or reviewer-package distribution, rerun package staging against the current manuscript/figure/ledger state, rerun blinded identifier and checksum audits, resolve final correspondence and availability metadata, and repeat final PDF/static/package checks after any PI/coauthor edits.
- **Files affected:** `scripts/revision_restart/phase8_final_qa_audit.py`, `results/revision_restart/phase8/*`, `manuscript/revision_restart/PHASE8_*`, `reports/PHASE_RESTART_8_REPORT.md`, `manuscript/metadata.tex`, `manuscript/tables/claim_summary.tex`, `scripts/revision_v2/r4_generate_publication_figures.py`, `manuscript/figures_publication/Fig1_architecture.*`, `manuscript/figures_publication/Fig8_summary.*`, `manuscript/figures_publication/FigS9_phase06_uncertainty.*`, `docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`.

### 2026-06-12 - Resolve the package synchronization blocker without making public-release decisions

- **Phase:** Revision Restart Phase 9
- **Status:** accepted
- **Question:** How should the Phase 8 reviewer-package synchronization blocker be handled without prematurely submitting or publicly releasing the project?
- **Decision:** Rebuild the blinded reviewer package, rebuild the unblinded internal release-candidate package, and create a PI/coauthor review package from the current post-Phase-8 state. Treat the resulting packages as private review artifacts only. Do not create a public repository, mint a DOI, select a license, post a preprint, distribute reviewer packages, or submit the manuscript without explicit human approval.
- **Alternatives:** Distribute the stale Phase 5 packages; include only PDFs and omit code/data; create a public repository immediately; defer package rebuilding until after PI review; reopen scientific analysis during package synchronization.
- **Evidence:** Phase 9 generated a 424-row blinded package manifest, 478-row unblinded package manifest, and 22-row PI/coauthor package manifest. Archive sidecars verified for all three packages. The blinded package had 0 identifier hits and 0 local-path hits. Unblinded and PI packages had expected identifiers but 0 local-path hits. Package-document risky-language audit had 0 hits. Package consistency checks passed. Protected hash comparison found 304 unchanged paths, 0 changed, 0 missing, and 0 added. The blinded package ran 57 unit tests successfully, a fresh archive extraction ran the Phase 4 validation runner successfully, and full repository unittest discovery passed 63 tests.
- **Scientific implications:** No scientific claim changed. Phase 9 improves reproducibility readiness by aligning private package evidence with the Phase 7/8 analytic-divider and residual-domain manuscript state.
- **Software implications:** Added a Phase 9 package synchronizer and generated package artifacts, manifests, checksum sidecars, PI/coauthor decision forms, audits, and reports. Validated model code, raw result CSVs, broad scientific analyses, public repository state, license state, DOI state, preprint state, and submission state were preserved.
- **Validation required:** After PI/coauthor edits or administrative decisions, rerun package synchronization, identifier/local-path audit, checksum verification, manuscript/package consistency audit, and final unit/package smoke tests before any distribution or submission.
- **Files affected:** `scripts/revision_restart/phase9_sync_review_packages.py`, `submission/reviewer_access_package/blinded_spine_review_package/*`, `submission/reviewer_access_package/unblinded_internal_release_candidate/*`, `submission/reviewer_access_package/SPINE_blinded_reviewer_package_phase9.zip*`, `submission/reviewer_access_package/SPINE_unblinded_internal_release_candidate_phase9.zip*`, `submission/pi_coauthor_review_package/*`, `results/revision_restart/phase9/*`, `manuscript/revision_restart/PHASE9_*`, `reports/PHASE_RESTART_9_REPORT.md`, `docs/PROJECT_STATE.md`, `docs/DECISION_LOG.md`.
