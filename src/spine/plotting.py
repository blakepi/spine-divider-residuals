"""Basic Phase 01 plotting helpers."""

from __future__ import annotations

from pathlib import Path

from spine.passive import SimulationResult
from spine.units import V_to_mV, s_to_ms


def plot_voltage_trace(result: SimulationResult, path: str | Path) -> Path:
    """Write a simple three-compartment voltage trace plot.

    Matplotlib is imported lazily so the computational core and tests can run in
    minimal environments. Normal local installs get matplotlib from
    `pyproject.toml` or `requirements.txt`.
    """
    import matplotlib.pyplot as plt

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    time_ms = [s_to_ms(float(t)) for t in result.time_s]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(time_ms, [V_to_mV(float(v)) for v in result.head_V], label="head")
    ax.plot(time_ms, [V_to_mV(float(v)) for v in result.dendrite_V], label="dendrite")
    ax.plot(time_ms, [V_to_mV(float(v)) for v in result.soma_V], label="soma")
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Voltage (mV)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)
    return output
