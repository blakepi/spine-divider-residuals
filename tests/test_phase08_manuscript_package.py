import csv
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Phase08ManuscriptPackageTests(unittest.TestCase):
    def test_required_phase08_files_exist(self):
        required = [
            "manuscript/main_unblinded.tex",
            "manuscript/main_blinded.tex",
            "manuscript/target_journal.tex",
            "manuscript/preamble.tex",
            "manuscript/metadata.tex",
            "manuscript/references.bib",
            "manuscript/JOURNAL_TARGET_ASSESSMENT.md",
            "manuscript/CLAIM_TO_SOURCE_LEDGER.csv",
            "manuscript/FIGURE_SOURCE_MANIFEST.csv",
            "manuscript/TABLE_SOURCE_MANIFEST.csv",
            "manuscript/NUMERICAL_VERIFICATION_REPORT.md",
            "manuscript/supplement/supplement.tex",
            "manuscript/BUILD_INSTRUCTIONS.md",
            "manuscript/LATEX_VALIDATION_REPORT.md",
            "submission/COVER_LETTER.md",
            "submission/TITLE_PAGE.md",
            "submission/DATA_AND_CODE_AVAILABILITY.md",
            "submission/AUTHOR_CONFIRMATION_CHECKLIST.md",
            "submission/JOURNAL_COMPLIANCE_CHECKLIST.md",
            "repository/REPOSITORY_RELEASE_PLAN.md",
            "repository/CITATION.cff",
            "repository/LICENSE_OPTIONS.md",
            "reports/PHASE08_MANUSCRIPT_REPORT.md",
            "reports/PHASE08_JOURNAL_COMPLIANCE.md",
            "reports/PHASE08_REPOSITORY_REPORT.md",
            "reports/PHASE_08_REPORT.md",
        ]
        missing = [p for p in required if not (ROOT / p).exists()]
        self.assertEqual([], missing)

    def test_figure_and_table_manifest_paths_exist(self):
        for manifest_name, fields in [
            ("manuscript/FIGURE_SOURCE_MANIFEST.csv", ["submission_file", "original_source_figure", "source_data", "script"]),
            ("manuscript/TABLE_SOURCE_MANIFEST.csv", ["latex_file", "source_data"]),
        ]:
            with (ROOT / manifest_name).open(newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertGreater(len(rows), 0)
            missing = []
            for row in rows:
                for field in fields:
                    for item in row[field].split(";"):
                        item = item.strip()
                        if item and not (ROOT / item).exists():
                            missing.append((row.get("figure_id") or row.get("table_id"), field, item))
            self.assertEqual([], missing)

    def test_claim_ledger_source_paths_exist_and_key_values_present(self):
        with (ROOT / "manuscript/CLAIM_TO_SOURCE_LEDGER.csv").open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertGreaterEqual(len(rows), 20)
        missing = []
        values = set()
        for row in rows:
            if row["source_csv"] and not (ROOT / row["source_csv"]).exists():
                missing.append(row["source_csv"])
            if row["source_report"] and not (ROOT / row["source_report"]).exists():
                missing.append(row["source_report"])
            values.add(row["numerical_value"])
        self.assertEqual([], missing)
        self.assertIn("0.23958333333333334", values)
        self.assertIn("0.6454282711508145", values)
        self.assertIn("0.9249061498523893", values)

    def test_bibliography_and_citations_are_consistent(self):
        bib_text = (ROOT / "manuscript/references.bib").read_text(encoding="utf-8")
        bib_keys = set(re.findall(r"@\w+\{([^,]+),", bib_text))
        tex_paths = list((ROOT / "manuscript/sections").glob("*.tex"))
        tex_paths += list((ROOT / "manuscript/supplement/sections").glob("*.tex"))
        cited = set()
        for path in tex_paths:
            text = path.read_text(encoding="utf-8")
            for match in re.findall(r"\\cite[tp]?\{([^}]+)\}", text):
                cited.update(k.strip() for k in match.split(",") if k.strip())
        self.assertTrue(cited)
        self.assertTrue(cited.issubset(bib_keys), cited - bib_keys)
        self.assertEqual(bib_keys, cited)

    def test_blinded_source_omits_author_identifiers(self):
        blinded_paths = [ROOT / "manuscript/main_blinded.tex"]
        blinded_paths += list((ROOT / "manuscript/sections").glob("*.tex"))
        forbidden = [
            "Gregory",
            "Pierpoint",
            "Alberto",
            "Musto",
            "Virginia Health Sciences",
            "Eastern Virginia",
            "Old Dominion",
            "Norfolk",
        ]
        joined = "\n".join(path.read_text(encoding="utf-8") for path in blinded_paths)
        for token in forbidden:
            self.assertNotIn(token, joined)

    def test_manuscript_faithful_track_still_isolated(self):
        baseline = (ROOT / "configs/manuscript_faithful/baseline.toml").read_text(encoding="utf-8")
        self.assertIn('track = "manuscript_faithful"', baseline)
        self.assertNotIn("active_extension", baseline)
        self.assertNotIn("epilepsy_exploratory", baseline)


if __name__ == "__main__":
    unittest.main()
