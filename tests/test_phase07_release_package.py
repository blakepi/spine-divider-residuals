from __future__ import annotations

import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class Phase07ReleasePackageTests(unittest.TestCase):
    def test_required_release_reports_exist(self) -> None:
        required = {
            "PHASE07_FULL_AUDIT.md",
            "PHASE07_REPRODUCIBILITY.md",
            "FINAL_SCIENTIFIC_SYNTHESIS.md",
            "PUBLICATION_GUIDE.md",
            "FIGURE_INDEX.md",
            "FINAL_CLAIM_AUDIT.md",
            "FUTURE_WORK.md",
            "PHASE_07_REPORT.md",
        }
        for name in required:
            path = ROOT / "reports" / name
            self.assertTrue(path.exists(), name)
            text = path.read_text(encoding="utf-8")
            self.assertGreater(len(text), 500, name)

    def test_release_docs_exist_and_are_science_bounded(self) -> None:
        for name in ["README.md", "INSTALL.md", "QUICKSTART.md", "CHANGELOG.md"]:
            path = ROOT / name
            self.assertTrue(path.exists(), name)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("not a universal predictor", readme)
        self.assertIn("epilepsy", readme.lower())
        quickstart = (ROOT / "QUICKSTART.md").read_text(encoding="utf-8")
        for script in [
            "reproduce_manuscript.py",
            "run_phase03.py",
            "run_phase04.py",
            "run_phase05.py",
            "run_phase05_1.py",
            "run_phase06.py",
        ]:
            self.assertIn(script, quickstart)

    def test_traceability_is_closed_for_late_phases(self) -> None:
        rows = read_csv(ROOT / "docs" / "TRACEABILITY_MATRIX.csv")
        text = (ROOT / "docs" / "TRACEABILITY_MATRIX.csv").read_text(encoding="utf-8").lower()
        self.assertNotIn("phase 02 pending", text)
        self.assertNotIn("future api", text)
        sources = {row["source"] for row in rows}
        for source in ["Phase 03", "Phase 04", "Phase 05", "Phase 05.1", "Phase 06"]:
            self.assertIn(source, sources)

    def test_configuration_tracks_remain_isolated(self) -> None:
        manuscript = (ROOT / "configs" / "manuscript_faithful" / "baseline.toml").read_text(encoding="utf-8").lower()
        self.assertNotIn("epilepsy", manuscript)
        self.assertNotIn("nmda", manuscript)
        self.assertNotIn("active", manuscript)
        active = (ROOT / "configs" / "active_extension" / "baseline.toml").read_text(encoding="utf-8").lower()
        exploratory = (ROOT / "configs" / "epilepsy_exploratory" / "baseline.toml").read_text(encoding="utf-8").lower()
        self.assertIn("active_extension", active)
        self.assertIn("epilepsy_exploratory", exploratory)
        self.assertIn("clinical_claims_allowed = false", exploratory)

    def test_source_data_and_figures_are_present(self) -> None:
        expected_csv_counts = {
            "phase02": 10,
            "phase03": 10,
            "phase04": 8,
            "phase05": 13,
            "phase05_1": 15,
            "phase06": 12,
        }
        for phase, minimum_count in expected_csv_counts.items():
            self.assertGreaterEqual(len(list((ROOT / "results" / phase).glob("*.csv"))), minimum_count, phase)
        expected_svg_counts = {
            "phase02": 12,
            "phase03": 7,
            "phase04": 6,
            "phase05": 5,
            "phase05_1": 8,
            "phase06": 5,
        }
        for phase, minimum_count in expected_svg_counts.items():
            self.assertGreaterEqual(len(list((ROOT / "figures" / phase).glob("*.svg"))), minimum_count, phase)

    def test_final_claim_audit_preserves_core_classifications(self) -> None:
        text = (ROOT / "reports" / "FINAL_CLAIM_AUDIT.md").read_text(encoding="utf-8")
        self.assertIn("SMI is a local isolation descriptor. | supported", text)
        self.assertIn("SMI predicts head amplitude. | contradicted", text)
        self.assertIn("Equal SMI implies equivalent electrical behavior. | contradicted", text)
        self.assertIn("Radius uncertainty destabilizes SMI classes. | strongly supported", text)


if __name__ == "__main__":
    unittest.main()
