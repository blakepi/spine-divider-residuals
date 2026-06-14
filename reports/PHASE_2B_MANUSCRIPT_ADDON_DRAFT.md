# Phase 2b Manuscript Add-On Draft

This is draft text only. It is not manuscript source.

## 1. Proposed Subsection Title

External summary anchors as a bounded load-normalization decision gate

## 2. Proposed Results Paragraph

As a summary-level external decision gate, we placed the machine-recoverable Harnett and Popovic anchor values on the same load-normalized divider coordinate used by SPINE. The Harnett row is a model/summary high-isolation anchor, not recovered paired measured per-spine data. Its source-native value was `rho_L = 4` (`Gamma_div = 0.2`), whereas the Popovic measured summary row was low (`rho_L = 0.0982`, `Gamma_div = 0.911`) and the Popovic model-fit row was also low (`rho_L = 0.0718`, `Gamma_div = 0.933`). Under fixed/recovered common loads, Harnett remained high, Popovic measured remained low, and Popovic model-fit remained low or intermediate. A deterministic diagnostic load grid preserved ordered class separation while exposing the expected boundary behavior near `rho_L = 0.75`. Thus, the external summary anchors support a load-normalization hypothesis for part of the apparent high- versus low-isolation contrast, while remaining summary-level anchors only.

## 3. Proposed Methods Paragraph

External rows were taken only from the locked Phase 1 summary dataset. We computed `rho_L = R_neck / load` and `Gamma_div = 1 / (1 + rho_L)` for three summary-usable rows: Harnett model/summary, Popovic measured summary, and Popovic model fit. Load sensitivity used source-native loads, four fixed/recovered common loads (`144.487`, `125`, `275`, and `564` MOhm), and a deterministic diagnostic grid (`75` to `666.667` MOhm). Source-reported uncertainty was propagated only where available in the curated dataset; no uncertainty was invented for Harnett or the Popovic model-fit row. Kwon and Cornejo remained context/exclusion rows because no accepted paired `R_neck`/load coordinate was available.

## 4. Proposed Figure Caption

Candidate Figure X. Bounded summary-level load sensitivity for external Route 1 anchors. A, Source-native summary anchors are plotted on the analytic divider relationship `Gamma_div = 1/(1 + rho_L)`. Points lie on the divider by definition and do not represent residual validation. B, Class stability across source-native and deterministic common-load calculations. Harnett remains high across fixed/recovered common loads; Popovic measured remains low across those loads; Popovic model fit remains low or intermediate and never high. The diagnostic grid is a deterministic stress test, not a biological distribution. C, Analytic class-threshold loads show the load required for each row to cross low/intermediate/high `rho_L` classes. Rows are summary/model anchors only, not per-spine measurements.

## 5. Proposed Limitations Paragraph

This external overlay is intentionally limited. It uses three summary-usable anchors, not a per-spine reanalysis. Harnett is represented by a model/summary anchor rather than recovered native paired measured rows, Popovic measured and model-fit summaries are kept separate, and Kwon and Cornejo remain context/exclusion rows. External transfer proxies were treated as proxy-only compatibility checks and are not SPINE residuals. The result is therefore best read as a bounded load-normalization hypothesis, not as biological validation or field-resolution evidence.

## 6. Proposed One-Sentence Discussion Insertion

These summary-level anchors suggest that some apparent high- versus low-isolation contrast can be reframed in load-normalized coordinates, but the evidence remains too limited for per-spine or validation-strength claims.

## 7. Exact Caveat Sentence

This analysis uses summary-level anchors only: it is not a per-spine reanalysis, Harnett is a model/summary anchor rather than recovered paired measured per-spine data, Kwon and Cornejo remain context/exclusion rows, and transfer proxies are not SPINE residuals.
