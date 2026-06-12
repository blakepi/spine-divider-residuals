from __future__ import annotations

import hashlib
import re
import sys
import zipfile
from pathlib import Path

EXCLUDE_PARTS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".tmp"}


def should_include(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    if any(part in EXCLUDE_PARTS for part in relative.parts):
        return False
    if path.suffix.lower() in EXCLUDE_SUFFIXES:
        return False
    if path.name.startswith("SPINE_phase_") and path.suffix == ".zip":
        return False
    if path.name.startswith("SPINE_phase_") and path.name.endswith(".zip.sha256"):
        return False
    return path.is_file()


def main() -> int:
    if len(sys.argv) != 2 or not re.fullmatch(r"\d+(?:\.\d+)?", sys.argv[1]):
        print("Usage: python scripts/make_checkpoint.py <phase_number_or_label>")
        return 2

    label_parts = sys.argv[1].split(".")
    phase_label = f"{int(label_parts[0]):02d}"
    if len(label_parts) == 2:
        phase_label = f"{phase_label}_{int(label_parts[1])}"
    root = Path(__file__).resolve().parents[1]
    output_dir = root / "checkpoints"
    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / f"SPINE_phase_{phase_label}_checkpoint.zip"

    files = [p for p in root.rglob("*") if should_include(p, root)]

    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(files):
            zf.write(path, path.relative_to(root))

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum = archive.with_suffix(".zip.sha256")
    checksum.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")

    print(f"Created {archive}")
    print(f"SHA-256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
