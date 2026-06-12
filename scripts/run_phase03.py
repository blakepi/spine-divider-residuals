from __future__ import annotations

from spine.phase03 import run_phase03


def main() -> int:
    outputs = run_phase03()
    for name, path in sorted(outputs.items()):
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
