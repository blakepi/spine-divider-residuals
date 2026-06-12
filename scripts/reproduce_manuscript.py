from __future__ import annotations

from spine.protocols import run_manuscript_reproduction


def main() -> int:
    outputs = run_manuscript_reproduction()
    for name, path in sorted(outputs.items()):
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
