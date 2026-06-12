"""Small Phase 01 source-data export helpers."""

from __future__ import annotations

import csv
from pathlib import Path

from spine.passive import SimulationResult
from spine.units import S_to_nS, V_to_mV, s_to_ms


def export_voltage_csv(result: SimulationResult, path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time_ms", "V_h_mV", "V_d_mV", "V_s_mV", "g_syn_nS"])
        for time_s, voltage, g_syn in zip(result.time_s, result.voltage_V, result.g_syn_S):
            writer.writerow(
                [
                    s_to_ms(float(time_s)),
                    V_to_mV(float(voltage[0])),
                    V_to_mV(float(voltage[1])),
                    V_to_mV(float(voltage[2])),
                    S_to_nS(float(g_syn)),
                ]
            )
    return output
