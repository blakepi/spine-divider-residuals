"""Run Phase 06 exploratory epilepsy analyses."""

from __future__ import annotations

from spine.phase06 import run_phase06


if __name__ == "__main__":
    outputs = run_phase06()
    for name, path in sorted(outputs.items()):
        print(f"{name}: {path}")
