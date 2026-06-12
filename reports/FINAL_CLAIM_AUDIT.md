# Final Claim Audit

Date: 2026-06-10

## Classification Scale

- **Strongly supported:** multiple validated phases and convergence/uncertainty
  checks support the claim.
- **Supported:** substantial evidence supports the claim, with important
  conditions.
- **Ensemble-dependent:** true in some sampled regimes but not universal.
- **Exploratory:** hypothesis-generating only.
- **Uncertain:** current evidence is insufficient or mixed.
- **Contradicted:** evidence argues against the claim.

## Required Claims

| Claim | Classification | Evidence |
|---|---|---|
| 1. SMI is a local isolation descriptor. | supported | Phase 03 SMI local abs(Spearman) `0.942342`; Phase 04 `0.924906`; Phase 05.1 N=768 passive/active SMI local abs(Spearman) about `0.94`. |
| 2. SMI predicts head amplitude. | contradicted | Phase 05.1 amplitude SMI abs(Spearman) about `0.22`; synaptic conductance dominates; iso-SMI amplitude failures are dominant. |
| 3. SMI predicts somatic transfer. | ensemble-dependent | Phase 03-04 challenge suites favor transfer/impedance predictors; Phase 05 compact ensemble favored SMI; Phase 05.1 passive returned to transfer gain while active remained SMI-led. |
| 4. Equal SMI implies equivalent electrical behavior. | contradicted | Passive and active iso-SMI amplitude counterexamples are dominant; identifiability examples show same-SMI/different-morphology cases. |
| 5. Active mechanisms preserve local SMI usefulness. | supported | Active SMI remains strong for local `Gamma_h_to_d`, but active NMDA/full restrained mechanisms produce local iso-SMI counterexamples. |
| 6. Radius uncertainty destabilizes SMI classes. | strongly supported | N=768 radius-induced class flip fraction `0.239583`; intermediate-class flip fraction `1.000000`. |
| 7. Exploratory epilepsy perturbations preserve local SMI utility. | exploratory | Phase 06 compact scenario ensemble supports local SMI, but it uses restrained hypothesis-level perturbations and `N=8` uncertainty screen. |
| 8. Exploratory epilepsy perturbations alter global synaptic impact. | exploratory | Phase 06 synaptic-strength and clustered scenarios changed amplitude/threshold-like behavior without supporting disease-level claims. |

## Additional Major Claims

| Claim | Classification | Evidence |
|---|---|---|
| Manuscript-faithful passive caption values reproduce. | strongly supported | Phase 02 reproduced all tested Figure 2 caption targets under predefined tolerances. |
| Fixed-load SMI adds information beyond `R_neck`. | contradicted | Phase 02 fixed-load sweep produced `Spearman(SMI, R_neck) = 1.0`. |
| SMI is useful as part of a broader impedance/load descriptor family. | supported | Dynamic SMI, `R_neck`, transfer gain, and multivariable predictors improve context-dependent interpretation. |
| Exact top-predictor labels are stable. | contradicted | Phase 05.1 final ranking stability validation failed due to near-tied dynamic-SMI variants. |
| Parameter values are uniquely identifiable from limited voltage metrics. | contradicted | Phase 05 exported 60 degeneracy examples. |
| Phase 06 scenarios are calibrated epilepsy mechanisms. | contradicted | Reports explicitly label them exploratory and evidence-graded, with no clinical claims. |

## Recommended Final Claim Set

1. SMI is a useful local, low-frequency isolation coordinate.
2. SMI is not a head-amplitude predictor.
3. SMI is not a universal or sufficient somatic-transfer predictor.
4. Equal SMI does not imply equivalent transient, nonlinear, or active
   electrical behavior.
5. SMI class labels are measurement-sensitive and should be used cautiously.
6. Impedance, morphology, synaptic drive, active state, and uncertainty are
   required for a full scientific interpretation.

## Claims To Avoid

- SMI universally predicts synaptic integration.
- SMI alone predicts somatic impact across regimes.
- SMI classes are robust biological categories.
- Active mechanisms rescue broad SMI claims.
- Exploratory epilepsy scenarios imply clinical relevance.
