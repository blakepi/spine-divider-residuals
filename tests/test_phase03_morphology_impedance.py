from pathlib import Path
import csv
import math
import unittest

import numpy as np

from spine.impedance import sinusoidal_impedance_validation
from spine.morphology import parse_swc_text, procedural_cable
from spine.network import PassiveNetwork


RESULTS = Path("results/phase03")
FIGURES = Path("figures/phase03")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class Phase03MorphologyImpedanceTests(unittest.TestCase):
    def test_sparse_dense_equivalence_for_procedural_cable(self):
        build = procedural_cable(60.0, 0.4, 4)
        sparse = build.network.assemble_sparse_admittance()
        dense = build.network.assemble_dense_admittance()
        self.assertLess(np.max(np.abs(sparse.to_dense() - dense)), 1e-12)
        vector = np.arange(build.network.n, dtype=float)
        self.assertLess(np.max(np.abs(sparse.matvec(vector) - dense @ vector)), 1e-12)

    def test_swc_parser_builds_tree(self):
        swc = "\n".join(
            [
                "1 1 0 0 0 5 -1",
                "2 3 10 0 0 1 1",
                "3 3 20 0 0 1 2",
                "4 3 20 10 0 0.8 2",
            ]
        )
        build = parse_swc_text(swc)
        self.assertEqual(build.network.n, 4)
        self.assertEqual(len(build.network.connections), 3)
        self.assertEqual(len(build.terminal_indices), 2)

    def test_direct_sinusoidal_validation_is_consistent(self):
        build = procedural_cable(80.0, 0.5, 5)
        result = sinusoidal_impedance_validation(
            build.network,
            build.terminal_indices[0],
            build.soma_index,
            frequency_hz=25.0,
            dt_s=2e-5,
            cycles=8,
        )
        self.assertLess(result["relative_amplitude_error"], 0.01)
        self.assertLess(result["phase_error_rad"], 0.03)

    def test_phase03_output_files_exist(self):
        required = [
            RESULTS / "smi_challenge_suite.csv",
            RESULTS / "predictor_comparison.csv",
            RESULTS / "impedance_spectrum.csv",
            RESULTS / "sinusoidal_validation.csv",
            RESULTS / "chirp_validation.csv",
            RESULTS / "neck_model_comparison.csv",
            RESULTS / "spatial_convergence.csv",
            RESULTS / "falsification_summary.csv",
            FIGURES / "challenge_SMI_vs_Gamma_hd.svg",
            FIGURES / "dynamic_SMI_spectrum.svg",
            FIGURES / "neck_model_transfer.svg",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing {path}")
            self.assertGreater(path.stat().st_size, 0)

    def test_phase03_validation_tables_meet_thresholds(self):
        sinusoid = read_rows(RESULTS / "sinusoidal_validation.csv")
        self.assertLess(max(float(row["relative_amplitude_error"]) for row in sinusoid), 0.05)
        self.assertLess(max(float(row["phase_error_rad"]) for row in sinusoid), 0.10)

        chirp = read_rows(RESULTS / "chirp_validation.csv")
        self.assertTrue(all(row["validation_method"] == "log_chirp_fft" for row in chirp))
        self.assertLess(max(float(row["relative_amplitude_error"]) for row in chirp), 0.10)

        spatial = read_rows(RESULTS / "spatial_convergence.csv")
        last_halving = [row for row in spatial if row["nseg"] == "16"][0]
        self.assertLess(float(last_halving["Gamma_h_to_s_rel_diff_vs_32seg"]), 0.05)

    def test_phase03_counterexamples_are_recorded(self):
        rows = read_rows(RESULTS / "falsification_summary.csv")
        results = {row["criterion"]: row["result"] for row in rows}
        self.assertEqual(
            results["iso_smi_Gamma_h_to_d_spread_gt_20_percent"],
            "SMI failure/counterexample",
        )
        self.assertEqual(
            results["iso_smi_A_h_spread_gt_20_percent"],
            "SMI failure/counterexample",
        )

    def test_distributed_neck_matches_lumped_when_only_passive_membrane_is_tiny(self):
        rows = read_rows(RESULTS / "neck_model_comparison.csv")
        lumped = [row for row in rows if row["model"] == "cylindrical_lumped"][0]
        distributed = [row for row in rows if row["model"] == "cylindrical_distributed_cable"][0]
        self.assertTrue(
            math.isclose(
                float(lumped["effective_R_neck_Mohm"]),
                float(distributed["effective_R_neck_Mohm"]),
                rel_tol=1e-12,
            )
        )
        self.assertLess(
            abs(float(lumped["Gamma_h_to_d"]) - float(distributed["Gamma_h_to_d"])),
            1e-3,
        )
