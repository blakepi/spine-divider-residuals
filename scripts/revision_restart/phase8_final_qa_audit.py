from __future__ import annotations

import csv
import hashlib
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "revision_restart" / "phase8"
PDF_TEXT = OUT / "pdf_text"
PDF_RENDERS = OUT / "pdf_renders"


PDFS = {
    "main_unblinded": ROOT / "manuscript" / "main_unblinded.pdf",
    "main_blinded": ROOT / "manuscript" / "main_blinded.pdf",
    "target_journal": ROOT / "manuscript" / "target_journal.pdf",
    "supplement": ROOT / "manuscript" / "supplement" / "supplement.pdf",
}

PDF_RENDER_PAGES = {
    "main_unblinded": [1, 6, 7, 8, 10, 14, 18],
    "main_blinded": [1, 6, 17],
    "target_journal": [1, 6, 17],
    "supplement": [1, 5, 11],
}

SEARCH_TERMS = [
    "Spine Morphology Index",
    "SMI predicts",
    "SMI predicted",
    "best predictor",
    "strongest predictor",
    "prevalence",
    "confidence interval",
    "Wilson",
    "biological prevalence",
    "population estimate",
    "NEURON validated",
    "NEURON validation",
    "field-standard",
    "R3",
    "R4",
    "R5",
    "R6",
    "R7",
    "audited CSV",
    "internal",
    "pipeline",
    "AUTHOR CONFIRMATION",
    "TODO",
    "FIXME",
    "placeholder",
    "clinical_claim",
    "epileptogenesis",
    "public repository",
    "DOI",
    "license selected",
    "C:\\",
    "Users\\",
    "gbp34",
    "gblakepierpoint",
]

BLINDED_TERMS = [
    "Blake",
    "Gregory",
    "Pierpoint",
    "Musto",
    "EVMS",
    "ODU",
    "Eastern Virginia",
    "Old Dominion",
]

SOURCE_GLOBS = [
    "manuscript/*.tex",
    "manuscript/sections/*.tex",
    "manuscript/tables/*.tex",
    "manuscript/supplement/*.tex",
    "manuscript/supplement/sections/*.tex",
    "manuscript/*.csv",
    "manuscript/references.bib",
    "manuscript/NUMERICAL_VERIFICATION_REPORT.md",
    "manuscript/figures_publication/*.svg",
]

CORE_CSVS = [
    "manuscript/CLAIM_TO_SOURCE_LEDGER.csv",
    "manuscript/FIGURE_SOURCE_MANIFEST.csv",
    "manuscript/TABLE_SOURCE_MANIFEST.csv",
    "manuscript/revision_restart/PHASE7_CLAIM_UPDATE_LOG.csv",
    "results/revision_restart/phase7/phase7_divider_residual_figure_data.csv",
    "results/revision_restart/phase7/phase7_divider_residual_figure_summary.csv",
    "submission/reviewer_access_package/blinded_spine_review_package/PACKAGE_MANIFEST.csv",
    "submission/reviewer_access_package/unblinded_internal_release_candidate/PACKAGE_MANIFEST.csv",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def extract_pdf_text() -> None:
    PDF_TEXT.mkdir(parents=True, exist_ok=True)
    PDF_RENDERS.mkdir(parents=True, exist_ok=True)
    for name, path in PDFS.items():
        if path.exists():
            run(["pdftotext", "-layout", str(path), str(PDF_TEXT / f"{name}.txt")])
            for page in PDF_RENDER_PAGES.get(name, []):
                run(
                    [
                        "pdftoppm",
                        "-png",
                        "-r",
                        "120",
                        "-f",
                        str(page),
                        "-singlefile",
                        str(path),
                        str(PDF_RENDERS / f"{name}_p{page:02d}"),
                    ]
                )


def pdf_info() -> None:
    rows = []
    for name, path in PDFS.items():
        row: dict[str, object] = {"pdf_id": name, "path": rel(path), "exists": path.exists()}
        if path.exists():
            proc = run(["pdfinfo", str(path)])
            for line in proc.stdout.splitlines():
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                key = key.strip().lower().replace(" ", "_")
                if key in {"pages", "page_size", "file_size", "pdf_version", "creationdate", "moddate"}:
                    row[key] = value.strip()
        rows.append(row)
    write_csv(OUT / "phase8_pdf_info.csv", rows)


def iter_source_files() -> list[Path]:
    files: list[Path] = []
    for pattern in SOURCE_GLOBS:
        files.extend(ROOT.glob(pattern))
    return sorted(set(p for p in files if p.is_file()))


def scan_file(path: Path, terms: list[str], category: str) -> list[dict[str, object]]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return [
            {
                "category": category,
                "term": "READ_ERROR",
                "path": rel(path),
                "line_number": "",
                "line": str(exc),
            }
        ]
    rows: list[dict[str, object]] = []
    lines = text.splitlines()
    for i, line in enumerate(lines, start=1):
        for term in terms:
            if category == "blinded_identifier_scan":
                pattern = r"(?<![A-Za-z])" + re.escape(term) + r"(?![A-Za-z])"
                found = re.search(pattern, line, flags=re.IGNORECASE) is not None
            else:
                found = term.lower() in line.lower()
            if found:
                rows.append(
                    {
                        "category": category,
                        "term": term,
                        "path": rel(path),
                        "line_number": i,
                        "line": line.strip()[:500],
                    }
                )
    return rows


def static_language_scan() -> None:
    rows: list[dict[str, object]] = []
    for path in iter_source_files():
        rows.extend(scan_file(path, SEARCH_TERMS, "manuscript_source"))
    for path in sorted(PDF_TEXT.glob("*.txt")):
        rows.extend(scan_file(path, SEARCH_TERMS, "pdf_text"))
    blinded_sources = [
        ROOT / "manuscript" / "main_blinded.tex",
        *(ROOT / "manuscript" / "sections").glob("*.tex"),
        *(ROOT / "manuscript" / "tables").glob("*.tex"),
        ROOT / "manuscript" / "supplement" / "supplement.tex",
        *(ROOT / "manuscript" / "supplement" / "sections").glob("*.tex"),
        PDF_TEXT / "main_blinded.txt",
    ]
    for path in blinded_sources:
        if path.exists():
            rows.extend(scan_file(path, BLINDED_TERMS, "blinded_identifier_scan"))
    write_csv(
        OUT / "phase8_static_language_hits.csv",
        rows,
        ["category", "term", "path", "line_number", "line"],
    )


def parse_csvs() -> None:
    rows = []
    for item in CORE_CSVS:
        path = ROOT / item
        row: dict[str, object] = {"path": item, "exists": path.exists(), "status": "missing", "rows": "", "columns": ""}
        if path.exists():
            try:
                with path.open(newline="", encoding="utf-8") as handle:
                    reader = csv.DictReader(handle)
                    data = list(reader)
                row.update({"status": "ok", "rows": len(data), "columns": len(reader.fieldnames or [])})
            except Exception as exc:
                row.update({"status": "error", "notes": str(exc)})
        rows.append(row)
    write_csv(OUT / "phase8_csv_parse_summary.csv", rows)


def audit_logs() -> None:
    logs = {
        "main_unblinded": ROOT / "manuscript" / "main_unblinded.log",
        "main_blinded": ROOT / "manuscript" / "main_blinded.log",
        "target_journal": ROOT / "manuscript" / "target_journal.log",
        "supplement": ROOT / "manuscript" / "supplement" / "supplement.log",
    }
    patterns = ["Undefined control sequence", "LaTeX Warning: Reference", "Citation", "Overfull", "Underfull", "Fatal error", "Emergency stop"]
    rows = []
    for name, path in logs.items():
        text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
        for pattern in patterns:
            matches = [line.strip() for line in text.splitlines() if pattern.lower() in line.lower()]
            rows.append(
                {
                    "document": name,
                    "log": rel(path),
                    "pattern": pattern,
                    "count": len(matches),
                    "first_match": matches[0][:300] if matches else "",
                }
            )
    write_csv(OUT / "phase8_latex_log_audit.csv", rows)


def audit_packages() -> None:
    package_rows = []
    packages = [
        (
            "blinded",
            ROOT / "submission" / "reviewer_access_package" / "SPINE_blinded_reviewer_package_draft.zip",
            ROOT / "submission" / "reviewer_access_package" / "SPINE_blinded_reviewer_package_draft.zip.sha256",
            ROOT / "submission" / "reviewer_access_package" / "blinded_spine_review_package" / "PACKAGE_MANIFEST.csv",
        ),
        (
            "unblinded_internal",
            ROOT / "submission" / "reviewer_access_package" / "SPINE_unblinded_internal_release_candidate.zip",
            ROOT / "submission" / "reviewer_access_package" / "SPINE_unblinded_internal_release_candidate.zip.sha256",
            ROOT / "submission" / "reviewer_access_package" / "unblinded_internal_release_candidate" / "PACKAGE_MANIFEST.csv",
        ),
    ]
    sync_rows = []
    for name, archive, sidecar, manifest in packages:
        sidecar_hash = ""
        if sidecar.exists():
            sidecar_hash = sidecar.read_text(encoding="utf-8", errors="replace").split()[0].lower()
        computed = sha256(archive) if archive.exists() else ""
        manifest_rows = []
        if manifest.exists():
            with manifest.open(newline="", encoding="utf-8") as handle:
                manifest_rows = list(csv.DictReader(handle))
        package_rows.append(
            {
                "package": name,
                "archive": rel(archive),
                "archive_exists": archive.exists(),
                "sidecar_exists": sidecar.exists(),
                "computed_sha256": computed,
                "sidecar_sha256": sidecar_hash,
                "checksum_match": computed.lower() == sidecar_hash.lower() if computed and sidecar_hash else False,
                "manifest": rel(manifest),
                "manifest_exists": manifest.exists(),
                "manifest_rows": len(manifest_rows),
            }
        )
        current_by_rel = {
            row.get("source_path", "") or row.get("path", ""): row
            for row in manifest_rows
        }
        for important in [
            "manuscript/CLAIM_TO_SOURCE_LEDGER.csv",
            "manuscript/FIGURE_SOURCE_MANIFEST.csv",
            "manuscript/TABLE_SOURCE_MANIFEST.csv",
            "manuscript/NUMERICAL_VERIFICATION_REPORT.md",
            "manuscript/figures_publication/Fig1_architecture.pdf",
            "manuscript/figures_publication/Fig3_divider_residuals.pdf",
            "results/revision_restart/phase1/phase1_divider_residual_rows.csv",
            "results/revision_restart/phase2/phase2_descriptor_recommendation_table.csv",
            "results/revision_restart/phase3/phase3_high_smi_coverage_audit.csv",
            "results/revision_restart/phase4/phase4_independent_matrix_benchmark.csv",
        ]:
            current = ROOT / important
            manifest_row = current_by_rel.get(important)
            manifest_hash = manifest_row.get("checksum_sha256", "") if manifest_row else ""
            current_hash = sha256(current) if current.exists() else ""
            sync_rows.append(
                {
                    "package": name,
                    "source_path": important,
                    "present_in_manifest": manifest_row is not None,
                    "current_exists": current.exists(),
                    "manifest_sha256": manifest_hash,
                    "current_sha256": current_hash,
                    "hash_matches_current": bool(manifest_hash and current_hash and manifest_hash.lower() == current_hash.lower()),
                }
            )
    write_csv(OUT / "phase8_package_checksum_audit.csv", package_rows)
    write_csv(OUT / "phase8_package_sync_audit.csv", sync_rows)


def protected_hash_compare() -> None:
    baseline = ROOT / "results" / "revision_restart" / "phase7" / "phase7_protected_hashes_after.csv"
    rows = []
    if baseline.exists():
        with baseline.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                path_text = row.get("path") or row.get("relative_path") or ""
                old_hash = row.get("sha256", "") or row.get("after_sha256", "")
                path = ROOT / path_text
                current_hash = sha256(path) if path.exists() else ""
                rows.append(
                    {
                        "path": path_text,
                        "baseline_sha256": old_hash,
                        "current_sha256": current_hash,
                        "exists_now": path.exists(),
                        "status": "unchanged" if current_hash and old_hash and current_hash.lower() == old_hash.lower() else "changed_or_missing",
                    }
                )
    write_csv(OUT / "phase8_protected_model_result_hash_comparison.csv", rows)


def claim_evidence_audit() -> None:
    rows = [
        {
            "claim_id": "P8-CLAIM-001",
            "manuscript_location": "Abstract; Results 3.2",
            "claim_text_or_summary": "SMI defines the analytic local divider Gamma_div = 1/(1+SMI).",
            "evidence_source": "PHASE1_ANALYTIC_DIVIDER_DERIVATION.md; supplement extended equations",
            "evidence_strength": "strong analytic",
            "wording_strength": "appropriately scoped",
            "overclaim_risk": "low",
            "action_needed": "none",
            "notes": "Presented as DC small-signal expectation, not transient equality.",
        },
        {
            "claim_id": "P8-CLAIM-002",
            "manuscript_location": "Abstract; Results 3.2; Fig. 3",
            "claim_text_or_summary": "Residuals from the divider are the domain-of-validity object.",
            "evidence_source": "phase1_divider_residual_rows.csv; phase7_divider_residual_figure_data.csv",
            "evidence_strength": "strong derived-data",
            "wording_strength": "appropriately scoped",
            "overclaim_risk": "low",
            "action_needed": "none",
            "notes": "3718 rows; median absolute residual 0.0548; max 0.492.",
        },
        {
            "claim_id": "P8-CLAIM-003",
            "manuscript_location": "Results 3.3; Table 3",
            "claim_text_or_summary": "The ratio is compact rather than generally superior to components.",
            "evidence_source": "phase2_descriptor_recommendation_table.csv",
            "evidence_strength": "moderate-to-strong descriptive",
            "wording_strength": "careful",
            "overclaim_risk": "low",
            "action_needed": "none",
            "notes": "Avoids exact-winner language.",
        },
        {
            "claim_id": "P8-CLAIM-004",
            "manuscript_location": "Results 3.4",
            "claim_text_or_summary": "Residuals, head amplitude, and somatic transfer require richer descriptor families.",
            "evidence_source": "phase2_residual_predictor_summary.csv; phase2_target_specific_descriptor_summary.csv",
            "evidence_strength": "strong descriptive",
            "wording_strength": "appropriately scoped",
            "overclaim_risk": "low",
            "action_needed": "none",
            "notes": "Target-specific rather than universal.",
        },
        {
            "claim_id": "P8-CLAIM-005",
            "manuscript_location": "Results 3.6; Discussion 4.3",
            "claim_text_or_summary": "N=768 deterministic uncertainty ensemble has no high-SMI rows.",
            "evidence_source": "phase3_high_smi_coverage_audit.csv",
            "evidence_strength": "strong audit",
            "wording_strength": "appropriately scoped",
            "overclaim_risk": "low",
            "action_needed": "none",
            "notes": "High-SMI uncertainty claims are explicitly limited.",
        },
        {
            "claim_id": "P8-CLAIM-006",
            "manuscript_location": "Results 3.7; Discussion 4.4; Table 2",
            "claim_text_or_summary": "Independent direct-matrix/DC benchmarks support passive baseline credibility.",
            "evidence_source": "phase4_independent_matrix_benchmark.csv; phase4_dc_analytic_benchmark.csv",
            "evidence_strength": "strong within passive baseline scope",
            "wording_strength": "careful",
            "overclaim_risk": "low",
            "action_needed": "none",
            "notes": "NEURON not claimed.",
        },
        {
            "claim_id": "P8-CLAIM-007",
            "manuscript_location": "Data and Code Availability",
            "claim_text_or_summary": "Reviewer-access package exists; public release/DOI/license pending approval.",
            "evidence_source": "submission/reviewer_access_package/*; phase8_package_checksum_audit.csv",
            "evidence_strength": "integrity strong; synchronization incomplete",
            "wording_strength": "honest",
            "overclaim_risk": "moderate",
            "action_needed": "rebuild reviewer package after Phase 7/8 source fixes",
            "notes": "Phase 5 packages predate Phase 7 manuscript/ledger edits.",
        },
        {
            "claim_id": "P8-CLAIM-008",
            "manuscript_location": "Methods 2.4; Results 3.5; Supplement",
            "claim_text_or_summary": "Active/NMDA cases are generic stress tests, disabled in baseline.",
            "evidence_source": "active_extension config; active validation reports",
            "evidence_strength": "moderate",
            "wording_strength": "appropriately limited",
            "overclaim_risk": "low",
            "action_needed": "none",
            "notes": "No disease or calibrated active reconstruction claim.",
        },
        {
            "claim_id": "P8-CLAIM-009",
            "manuscript_location": "Methods 2.2; Supplement",
            "claim_text_or_summary": "R_in,d is measured with stimulated spine omitted.",
            "evidence_source": "src/spine/impedance.py; phase2 attached-vs-omitted audit",
            "evidence_strength": "strong implementation and derived audit",
            "wording_strength": "appropriate",
            "overclaim_risk": "low",
            "action_needed": "none",
            "notes": "Current attached-vs-omitted differences are negligible but convention remains conceptually clean.",
        },
    ]
    write_csv(ROOT / "manuscript" / "revision_restart" / "PHASE8_CLAIM_EVIDENCE_AUDIT.csv", rows)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    extract_pdf_text()
    pdf_info()
    static_language_scan()
    parse_csvs()
    audit_logs()
    audit_packages()
    protected_hash_compare()
    claim_evidence_audit()
    print(f"Wrote Phase 8 QA outputs to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
