from pathlib import Path
import csv
import unittest

import numpy as np

from spine.phase05 import (
    BOOTSTRAP_SEED,
    CV_SEED,
    GLOBAL_N,
    LHS_SEED,
    bootstrap_abs_spearman_ci,
    cv_rmse_univariate,
    latin_hypercube,
    lhs_samples,
)


RESULTS = Path("results/phase05")
FIGURES = Path("figures/phase05")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class Phase05SensitivityStatisticsTests(unittest.TestCase):
    def test_latin_hypercube_is_deterministic_and_stratified(self):
        first = latin_hypercube(12, 4, LHS_SEED)
        second = latin_hypercube(12, 4, LHS_SEED)
        self.assertTrue(np.array_equal(first, second))
        self.assertTrue(np.all(first > 0.0))
        self.assertTrue(np.all(first < 1.0))
        for column in range(first.shape[1]):
            strata = np.floor(first[:, column] * 12).astype(int)
            self.assertEqual(set(strata.tolist()), set(range(12)))

        samples = lhs_samples(GLOBAL_N, LHS_SEED)
        self.assertEqual(len(samples), GLOBAL_N)
        self.assertEqual(samples[0]["sample_id"], 0.0)

    def test_bootstrap_and_cross_validation_are_seed_reproducible(self):
        x = np.linspace(0.0, 1.0, 20)
        y = 0.25 + 2.0 * x
        ci_a = bootstrap_abs_spearman_ci(x, y, seed=BOOTSTRAP_SEED, n_boot=30)
        ci_b = bootstrap_abs_spearman_ci(x, y, seed=BOOTSTRAP_SEED, n_boot=30)
        self.assertEqual(ci_a, ci_b)
        rmse_a = cv_rmse_univariate(x, y, seed=CV_SEED)
        rmse_b = cv_rmse_univariate(x, y, seed=CV_SEED)
        self.assertEqual(rmse_a, rmse_b)
        self.assertLess(rmse_a, 1e-12)

    def test_phase05_outputs_exist(self):
        required = [
            RESULTS / "uncertainty_distributions.csv",
            RESULTS / "local_sensitivity.csv",
            RESULTS / "global_uncertainty_samples.csv",
            RESULTS / "uncertainty_summary.csv",
            RESULTS / "uncertainty_decomposition.csv",
            RESULTS / "radius_uncertainty_class_stability.csv",
            RESULTS / "identifiability_degeneracy_examples.csv",
            RESULTS / "predictor_comparison.csv",
            RESULTS / "residual_analysis.csv",
            RESULTS / "counterexample_prevalence.csv",
            RESULTS / "claim_robustness.csv",
            RESULTS / "phase05_validation.csv",
            RESULTS / "phase05_summary.csv",
            FIGURES / "uncertainty_SMI_vs_Gamma_hd.svg",
            FIGURES / "uncertainty_SMI_vs_Gamma_hs.svg",
            FIGURES / "uncertainty_radius_vs_Rneck.svg",
            FIGURES / "radius_class_stability.svg",
            FIGURES / "sensitivity_SMI_ranked.svg",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing {path}")
            self.assertGreater(path.stat().st_size, 0)

    def test_validation_records_passed_checks_and_visible_convergence_limit(self):
        rows = read_rows(RESULTS / "phase05_validation.csv")
        by_name = {row["validation"]: row for row in rows}
        self.assertEqual(by_name["latin_hypercube_reproducibility"]["passed"], "True")
        self.assertLess(abs(float(by_name["local_sensitivity_radius_Rneck"]["value"]) + 2.0), 0.02)
        self.assertLess(abs(float(by_name["local_sensitivity_length_Rneck"]["value"]) - 1.0), 0.02)
        self.assertLess(abs(float(by_name["local_sensitivity_resistivity_Rneck"]["value"]) - 1.0), 0.02)
        self.assertEqual(by_name["bootstrap_seed_fixed"]["passed"], "True")
        self.assertEqual(by_name["cross_validation_seed_fixed"]["passed"], "True")

        convergence = by_name["uncertainty_convergence_48_vs_96"]
        self.assertEqual(convergence["passed"], "False")
        self.assertGreater(float(convergence["value"]), float(convergence["threshold"]))

    def test_residual_analysis_records_key_targets(self):
        rows = read_rows(RESULTS / "residual_analysis.csv")
        keys = {(row["target"], row["predictor"]) for row in rows}
        self.assertIn(("Gamma_h_to_d", "SMI"), keys)
        self.assertIn(("Gamma_h_to_s", "SMI"), keys)
        self.assertIn(("A_h_mV", "synaptic_conductance_scale"), keys)
        for row in rows:
            self.assertGreaterEqual(float(row["rmse_full"]), 0.0)
            self.assertNotEqual(row["dominant_residual_correlate"], "")

    def test_counterexamples_and_claim_classifications_are_preserved(self):
        counterexamples = {row["counterexample_type"]: row for row in read_rows(RESULTS / "counterexample_prevalence.csv")}
        self.assertEqual(counterexamples["passive_iso_SMI_amplitude_failure"]["classification"], "dominant")
        self.assertGreater(float(counterexamples["passive_iso_SMI_amplitude_failure"]["prevalence"]), 0.5)
        self.assertEqual(counterexamples["active_amplitude_failure"]["classification"], "dominant")
        self.assertEqual(counterexamples["passive_iso_SMI_local_failure"]["classification"], "rare")

        claims = {row["claim"]: row for row in read_rows(RESULTS / "claim_robustness.csv")}
        self.assertEqual(claims["SMI is a local isolation descriptor"]["classification"], "supported")
        self.assertEqual(claims["SMI is not a reliable somatic-transfer predictor"]["classification"], "uncertain")
        self.assertEqual(claims["SMI is not a reliable amplitude predictor"]["classification"], "strongly supported")
        self.assertEqual(claims["Equal SMI does not imply electrical equivalence"]["classification"], "strongly supported")


if __name__ == "__main__":
    unittest.main()
