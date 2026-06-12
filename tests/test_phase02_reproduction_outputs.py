from pathlib import Path
import csv
import math
import unittest


RESULTS = Path("results/phase02")
FIGURES = Path("figures/phase02")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class Phase02ReproductionOutputTests(unittest.TestCase):
    def test_reproduction_outputs_exist(self):
        required = [
            RESULTS / "caption_discrepancy_table.csv",
            RESULTS / "Figure2_representative_summary.csv",
            RESULTS / "Figure3_geometry_sweep.csv",
            RESULTS / "Figure4_matched_neck_heterogeneous_load.csv",
            RESULTS / "central_smi_claim_tests.csv",
            RESULTS / "convergence_dt_intermediate.csv",
            FIGURES / "Figure1_architecture.svg",
            FIGURES / "Figure2_low_trace.svg",
            FIGURES / "Figure2_intermediate_trace.svg",
            FIGURES / "Figure2_high_trace.svg",
            FIGURES / "Figure3A_Gamma_hs_heatmap.svg",
            FIGURES / "Figure3B_SMI_heatmap.svg",
            FIGURES / "Figure3C_SMI_vs_Gamma_hs.svg",
            FIGURES / "Figure3D_SMI_vs_Ah.svg",
            FIGURES / "Figure4A_Rneck_vs_Gamma_hs.svg",
            FIGURES / "Figure4B_SMI_vs_Gamma_hs.svg",
            FIGURES / "Figure4C_SMI_vs_Ah.svg",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing {path}")
            self.assertGreater(path.stat().st_size, 0)

    def test_caption_discrepancy_classifications_are_explicit(self):
        rows = read_rows(RESULTS / "caption_discrepancy_table.csv")
        self.assertEqual(len(rows), 9)
        classes = {row["classification"] for row in rows}
        self.assertTrue(classes <= {"exact reproduction", "approximate reproduction", "failed reproduction"})
        self.assertEqual(classes, {"exact reproduction"})

    def test_geometry_sweep_fixed_load_smi_rank(self):
        rows = read_rows(RESULTS / "central_smi_claim_tests.csv")
        by_claim = {row["claim"]: row for row in rows}
        rank = float(by_claim["fixed_load_SMI_and_Rneck_identical_rank_order"]["value"])
        self.assertTrue(math.isclose(rank, 1.0))
        self.assertEqual(
            by_claim["fixed_load_SMI_and_Rneck_identical_rank_order"]["interpretation"],
            "supporting",
        )

    def test_convergence_is_small_at_manuscript_dt(self):
        rows = read_rows(RESULTS / "convergence_dt_intermediate.csv")
        manuscript_dt = [row for row in rows if row["dt_ms"] == "0.01"][0]
        self.assertLess(float(manuscript_dt["A_h_mV_abs_diff_vs_0_0025_ms"]), 0.001)
        self.assertLess(float(manuscript_dt["Gamma_h_to_s_abs_diff_vs_0_0025_ms"]), 0.001)
