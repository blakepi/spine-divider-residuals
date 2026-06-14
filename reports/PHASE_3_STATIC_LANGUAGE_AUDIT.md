# Phase 3 Static Language Audit

## Search Terms

Positive caveat terms:

- `summary-level external decision gate`
- `three summary-usable rows`
- `Harnett model/summary`
- `Popovic measured summary`
- `Popovic model-fit`
- `source-native`
- `fixed/recovered common loads`
- `Popovic measured uncertainty envelope remained low`
- `transfer proxies`
- `not SPINE residuals`
- `not a per-spine reanalysis`
- `not biological validation`
- `not a controversy resolution`

Negative overclaim terms:

- `biologically validates SPINE`
- `validates SPINE`
- `resolves the controversy`
- `controversy is resolved`
- `per-spine validation`
- `population prevalence`
- `SPINE residuals from transfer proxies`

## Raw Hit Summary

All required positive patterns passed in `results/external_empirical/phase3_manuscript_addon/phase3_static_language_audit.csv`. All forbidden overclaim patterns were absent under the Phase 3 audit regexes.

## Classified Hits

Positive required caveats were found in the manuscript TeX corpus. Negative hits were classified as absent. The only earlier audit issue was a regex false positive around the phrase `not a per-spine reanalysis, not biological validation`; the audit pattern was tightened to detect affirmative per-spine validation claims rather than caveated negations.

## Positive Caveat Checks

- Summary-level gate: passed.
- Three summary rows: passed.
- Harnett model/summary caveat: passed.
- Popovic measured/model-fit separation: passed.
- Source-native and common-load separation: passed.
- Popovic uncertainty envelope: passed.
- Transfer proxies not residuals: passed.
- No per-spine, validation, or controversy-resolution caveats: passed.

## Negative Overclaim Checks

- No biological-validation claim detected.
- No controversy-resolution claim detected.
- No per-spine validation claim detected.
- No population-prevalence claim detected.
- No transfer-proxy SPINE-residual claim detected.

## Remaining Risks

The main residual risk is reader overinterpretation of Figure S10. This is mitigated by caption language stating that points lie on the divider by definition and do not constitute residual validation, per-spine inference, or controversy resolution.

## Pass/Fail Verdict

Verdict: `passed`.
