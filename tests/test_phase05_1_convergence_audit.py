from pathlib import Path
import csv
import unittest

from spine.phase05_1 import SAMPLE_SIZES, progressive_seed
from spine.phase05 import lhs_samples


RESULTS = Path("results/phase05_1")
FIGURES = Path("figures/phase05_1")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class Phase051ConvergenceAuditTests(unittest.TestCase):
    def test_phase05_1_outputs_exist(self):
        required = [
            RESULTS / "progressive_uncertainty_summary.csv",
            RESULTS / "progressive_convergence_deltas.csv",
            RESULTS / "convergence_cause_diagnostics.csv",
            RESULTS / "predictor_stability_summary.csv",
            RESULTS / "predictor_rankings_by_n.csv",
            RESULTS / "counterexample_prevalence_by_n.csv",
            RESULTS / "radius_uncertainty_by_n.csv",
            RESULTS / "radius_boundary_examples.csv",
            RESULTS / "radius_only_uncertainty.csv",
            RESULTS / "claim_reassessment.csv",
            RESULTS / "phase05_1_validation.csv",
            FIGURES / "convergence_SMI_median.svg",
            FIGURES / "convergence_SMI_interval_width.svg",
            FIGURES / "predictor_stability_somatic_SMI.svg",
            FIGURES / "radius_flip_prevalence.svg",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing {path}")
            self.assertGreater(path.stat().st_size, 0)

    def test_progressive_samples_are_reproducible(self):
        for n in SAMPLE_SIZES:
            rows = read_rows(RESULTS / f"global_uncertainty_samples_N{n}.csv")
            self.assertEqual(len(rows), n)
            expected = lhs_samples(n, progressive_seed(n))[0]
            self.assertAlmostEqual(float(rows[0]["neck_radius_um"]), expected["neck_radius_um"], places=15)
            self.assertAlmostEqual(float(rows[0]["neck_length_um"]), expected["neck_length_um"], places=15)

    def test_final_convergence_and_preserved_ranking_instability(self):
        validation = {row["validation"]: row for row in read_rows(RESULTS / "phase05_1_validation.csv")}
        self.assertEqual(validation["final_smi_median_convergence"]["passed"], "True")
        self.assertLess(float(validation["final_smi_median_convergence"]["value"]), 0.10)
        self.assertEqual(validation["final_all_median_convergence"]["passed"], "True")
        self.assertEqual(validation["final_ranking_stability_vs_previous_n"]["passed"], "False")

        deltas = read_rows(RESULTS / "progressive_convergence_deltas.csv")
        smi_final = [
            row
            for row in deltas
            if row["n_current"] == "768" and row["output"] == "SMI" and row["metric"] == "median"
        ][0]
        self.assertLess(float(smi_final["relative_change"]), 0.10)

    def test_radius_instability_and_counterexamples_are_quantified(self):
        radius = {row["n"]: row for row in read_rows(RESULTS / "radius_uncertainty_by_n.csv")}
        final_radius = radius["768"]
        self.assertGreater(float(final_radius["flip_fraction"]), 0.20)
        self.assertEqual(float(final_radius["intermediate_flip_fraction"]), 1.0)
        self.assertLess(float(final_radius["median_distance_to_boundary_flipped"]), float(final_radius["median_distance_to_boundary_all"]))

        counter = [
            row
            for row in read_rows(RESULTS / "counterexample_prevalence_by_n.csv")
            if row["n"] == "768" and row["counterexample_type"] == "passive_iso_SMI_amplitude_failure"
        ][0]
        self.assertEqual(counter["classification"], "dominant")
        self.assertGreater(float(counter["prevalence"]), 0.60)
        self.assertEqual(counter["stable_vs_previous"], "True")

    def test_claim_reassessment_records_changed_and_stable_claims(self):
        claims = {row["claim"]: row for row in read_rows(RESULTS / "claim_reassessment.csv")}
        self.assertEqual(claims["SMI is a local isolation descriptor"]["classification"], "supported")
        self.assertEqual(claims["SMI is not a reliable amplitude predictor"]["classification"], "strongly supported")
        self.assertEqual(claims["SMI is not a universal transfer predictor"]["classification"], "supported")
        self.assertEqual(claims["Active mechanisms sharpen SMI limitations"]["classification"], "uncertain")
        self.assertEqual(claims["SMI class assignments are stable under radius uncertainty"]["classification"], "contradicted")


if __name__ == "__main__":
    unittest.main()
