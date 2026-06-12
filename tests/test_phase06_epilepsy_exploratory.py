from __future__ import annotations

import csv
import unittest
from pathlib import Path

from spine.phase06 import EVIDENCE_ROWS, SCENARIOS, PHASE06_UNCERTAINTY_N


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "phase06"
REPORTS = ROOT / "reports"
FIGURES = ROOT / "figures" / "phase06"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class Phase06EpilepsyExploratoryTests(unittest.TestCase):
    def test_config_family_is_separated(self) -> None:
        text = (ROOT / "configs" / "epilepsy_exploratory" / "baseline.toml").read_text(encoding="utf-8")
        self.assertIn('track = "epilepsy_exploratory"', text)
        self.assertIn("clinical_claims_allowed = false", text)
        self.assertIn("separated_from_manuscript_faithful = true", text)
        manuscript = (ROOT / "configs" / "manuscript_faithful" / "baseline.toml").read_text(encoding="utf-8")
        self.assertNotIn("epilepsy_exploratory", manuscript)

    def test_evidence_table_has_traceable_references(self) -> None:
        rows = read_csv(RESULTS / "epilepsy_evidence_table.csv")
        self.assertGreaterEqual(len(rows), len(EVIDENCE_ROWS))
        doi_rows = [row for row in rows if row["doi_or_stable_id"].startswith("10.")]
        self.assertGreaterEqual(len(doi_rows), 10)
        grades = {row["evidence_grade"] for row in rows}
        self.assertIn("conflicting", grades)
        self.assertIn("limited", grades)

    def test_all_scenarios_and_protocols_are_present(self) -> None:
        rows = read_csv(RESULTS / "scenario_metrics.csv")
        scenarios = {row["scenario"] for row in rows}
        protocols = {row["protocol"] for row in rows}
        self.assertEqual(scenarios, {scenario.name for scenario in SCENARIOS})
        self.assertEqual(protocols, {"isolated_single_spine", "clustered_synchronous", "clustered_asynchronous"})
        for row in rows:
            self.assertEqual(row["clinical_claim"], "none")
            self.assertEqual(row["exploratory_only"], "True")
            self.assertGreater(float(row["R_neck_Mohm"]), 0.0)
            self.assertGreater(float(row["R_in_d_Mohm"]), 0.0)

    def test_uncertainty_outputs_are_deterministic_and_bounded(self) -> None:
        rows = read_csv(RESULTS / "scenario_uncertainty_samples.csv")
        self.assertEqual(len(rows), len(SCENARIOS) * PHASE06_UNCERTAINTY_N)
        summary = read_csv(RESULTS / "scenario_uncertainty_summary.csv")
        smi_rows = [row for row in summary if row["metric"] == "SMI"]
        self.assertEqual(len(smi_rows), len(SCENARIOS))
        for row in rows:
            self.assertEqual(row["finite"], "True")
            self.assertGreaterEqual(float(row["min_gate"]), -1e-12)
            self.assertLessEqual(float(row["max_gate"]), 1.0 + 1e-12)

    def test_validation_and_reports_preserve_limits(self) -> None:
        validation = read_csv(RESULTS / "phase06_validation.csv")
        self.assertTrue(validation)
        self.assertTrue(all(row["status"] == "pass" for row in validation))
        report = (REPORTS / "PHASE_06_REPORT.md").read_text(encoding="utf-8")
        self.assertIn("No clinical, diagnostic, prognostic, or therapeutic claims", report)
        self.assertIn("Phase 07 was not started", report)
        literature = (REPORTS / "PHASE06_LITERATURE_REVIEW.md").read_text(encoding="utf-8")
        self.assertIn("calibrated clinical or disease-state parameter", literature)

    def test_required_figures_exist(self) -> None:
        names = {
            "scenario_SMI_vs_Gamma_hd.svg",
            "scenario_SMI_vs_Gamma_hs.svg",
            "scenario_SMI_vs_Ah.svg",
            "mechanistic_decomposition_Ah.svg",
            "uncertainty_SMI_by_scenario.svg",
        }
        for name in names:
            path = FIGURES / name
            self.assertTrue(path.exists(), name)
            self.assertIn("<svg", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
