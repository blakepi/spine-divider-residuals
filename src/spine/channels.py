"""Phase 04 active conductance mechanisms.

The mechanisms are deliberately compact Hodgkin-Huxley-style conductances.
They are not loaded by the manuscript-faithful passive core and must be
attached explicitly by active-extension protocols.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from spine.units import mV_to_V, nS_to_S


def _clip_gate(value: float) -> float:
    if not math.isfinite(value):
        raise FloatingPointError("gate value became nonfinite")
    return min(1.0, max(0.0, value))


def _exp_limited(value: float) -> float:
    return math.exp(min(80.0, max(-80.0, value)))


def _vtrap_mV(x_mV: float, y_mV: float) -> float:
    """Return x/(1-exp(-x/y)) with the removable singularity handled."""
    if abs(x_mV / y_mV) < 1e-7:
        return y_mV * (1.0 + x_mV / (2.0 * y_mV))
    return x_mV / (1.0 - _exp_limited(-x_mV / y_mV))


def _gate_from_rates(alpha_per_ms: float, beta_per_ms: float) -> tuple[float, float]:
    if alpha_per_ms < 0 or beta_per_ms < 0:
        raise ValueError("gate rates must be nonnegative")
    total_per_s = (alpha_per_ms + beta_per_ms) * 1000.0
    if total_per_s <= 0:
        raise ValueError("gate total rate must be positive")
    return alpha_per_ms / (alpha_per_ms + beta_per_ms), 1.0 / total_per_s


@dataclass(frozen=True)
class ActiveChannel:
    name: str
    gbar_S: float
    reversal_V: float
    gate_powers: dict[str, int]
    source: str
    temperature_C: float = 6.3
    provenance: str = "generic active-extension setting"

    def __post_init__(self) -> None:
        if self.gbar_S < 0:
            raise ValueError("gbar_S must be nonnegative")
        if any(power <= 0 for power in self.gate_powers.values()):
            raise ValueError("gate powers must be positive")
        if self.name not in {"na", "kdr", "hcn", "ka", "cat"}:
            raise ValueError(f"unsupported active channel: {self.name}")

    @property
    def gate_names(self) -> tuple[str, ...]:
        return tuple(self.gate_powers.keys())

    def gate_inf_tau_s(self, gate_name: str, voltage_V: float) -> tuple[float, float]:
        return gate_inf_tau_s(self.name, gate_name, voltage_V)

    def initialize(self, voltage_V: float) -> dict[str, float]:
        return {
            gate_name: _clip_gate(self.gate_inf_tau_s(gate_name, voltage_V)[0])
            for gate_name in self.gate_names
        }

    def update_gates(self, gates: dict[str, float], voltage_V: float, dt_s: float) -> dict[str, float]:
        if dt_s <= 0:
            raise ValueError("dt_s must be positive")
        updated: dict[str, float] = {}
        for gate_name in self.gate_names:
            inf, tau_s = self.gate_inf_tau_s(gate_name, voltage_V)
            if tau_s <= 0:
                raise ValueError("gate time constant must be positive")
            old = gates[gate_name]
            value = inf + (old - inf) * math.exp(-dt_s / tau_s)
            updated[gate_name] = _clip_gate(value)
        return updated

    def open_probability(self, gates: dict[str, float]) -> float:
        probability = 1.0
        for gate_name, power in self.gate_powers.items():
            probability *= _clip_gate(gates[gate_name]) ** power
        return probability

    def conductance_S(self, gates: dict[str, float]) -> float:
        return self.gbar_S * self.open_probability(gates)

    def current_A(self, voltage_V: float, gates: dict[str, float]) -> float:
        """Return outward transmembrane current."""
        return self.conductance_S(gates) * (voltage_V - self.reversal_V)


def gate_inf_tau_s(channel_name: str, gate_name: str, voltage_V: float) -> tuple[float, float]:
    """Return steady-state gate value and time constant in seconds."""
    voltage_mV = voltage_V * 1e3

    if channel_name == "na":
        if gate_name == "m":
            alpha = 0.1 * _vtrap_mV(voltage_mV + 40.0, 10.0)
            beta = 4.0 * _exp_limited(-(voltage_mV + 65.0) / 18.0)
            return _gate_from_rates(alpha, beta)
        if gate_name == "h":
            alpha = 0.07 * _exp_limited(-(voltage_mV + 65.0) / 20.0)
            beta = 1.0 / (1.0 + _exp_limited(-(voltage_mV + 35.0) / 10.0))
            return _gate_from_rates(alpha, beta)

    if channel_name == "kdr":
        if gate_name == "n":
            alpha = 0.01 * _vtrap_mV(voltage_mV + 55.0, 10.0)
            beta = 0.125 * _exp_limited(-(voltage_mV + 65.0) / 80.0)
            return _gate_from_rates(alpha, beta)

    if channel_name == "hcn":
        if gate_name == "r":
            inf = 1.0 / (1.0 + _exp_limited((voltage_mV + 82.0) / 8.0))
            tau_ms = 30.0 + 170.0 / (
                _exp_limited((voltage_mV + 75.0) / 12.0)
                + _exp_limited(-(voltage_mV + 75.0) / 12.0)
            )
            return inf, tau_ms * 1e-3

    if channel_name == "ka":
        if gate_name == "a":
            inf = 1.0 / (1.0 + _exp_limited(-(voltage_mV + 50.0) / 20.0))
            tau_ms = 2.0
            return inf, tau_ms * 1e-3
        if gate_name == "b":
            inf = 1.0 / (1.0 + _exp_limited((voltage_mV + 80.0) / 6.0))
            tau_ms = 20.0 + 50.0 / (1.0 + _exp_limited((voltage_mV + 55.0) / 8.0))
            return inf, tau_ms * 1e-3

    if channel_name == "cat":
        if gate_name == "p":
            inf = 1.0 / (1.0 + _exp_limited(-(voltage_mV + 55.0) / 6.2))
            tau_ms = 5.0
            return inf, tau_ms * 1e-3
        if gate_name == "q":
            inf = 1.0 / (1.0 + _exp_limited((voltage_mV + 80.0) / 4.0))
            tau_ms = 30.0
            return inf, tau_ms * 1e-3

    raise ValueError(f"unsupported gate {channel_name}.{gate_name}")


def make_channel(name: str, gbar_nS: float, reversal_mV: float | None = None) -> ActiveChannel:
    """Create a Phase 04 active channel from readable electrophysiology units."""
    defaults = {
        "na": {
            "reversal_mV": 55.0,
            "gate_powers": {"m": 3, "h": 1},
            "source": "Hodgkin and Huxley 1952 sodium-current formalism",
            "provenance": "restrained active-extension density, not manuscript baseline",
        },
        "kdr": {
            "reversal_mV": -90.0,
            "gate_powers": {"n": 4},
            "source": "Hodgkin and Huxley 1952 delayed-rectifier formalism",
            "provenance": "restrained active-extension density, not manuscript baseline",
        },
        "hcn": {
            "reversal_mV": -30.0,
            "gate_powers": {"r": 1},
            "source": "Magee 1998/1999 HCN/Ih dendritic integration literature",
            "provenance": "generic subthreshold HCN approximation for Phase 04",
        },
        "ka": {
            "reversal_mV": -90.0,
            "gate_powers": {"a": 3, "b": 1},
            "source": "Connor-Stevens-family transient A-type potassium formalism",
            "provenance": "restrained generic transient potassium current",
        },
        "cat": {
            "reversal_mV": 120.0,
            "gate_powers": {"p": 2, "q": 1},
            "source": "reduced low-threshold calcium conductance literature family",
            "provenance": "electrical-only restrained calcium current; no calcium concentration model",
        },
    }
    if name not in defaults:
        raise ValueError(f"unsupported channel name: {name}")
    spec = defaults[name]
    return ActiveChannel(
        name=name,
        gbar_S=nS_to_S(gbar_nS),
        reversal_V=mV_to_V(spec["reversal_mV"] if reversal_mV is None else reversal_mV),
        gate_powers=dict(spec["gate_powers"]),
        source=str(spec["source"]),
        provenance=str(spec["provenance"]),
    )


def default_active_channels(profile: str = "na_kdr_hcn") -> list[ActiveChannel]:
    """Return restrained active-extension channel sets.

    Conductances are absolute nS per attached compartment for Phase 04 compact
    test networks, not morphology-derived densities.
    """
    if profile == "none":
        return []
    if profile == "hcn":
        return [make_channel("hcn", 0.05)]
    if profile == "na_kdr":
        return [make_channel("na", 6.0), make_channel("kdr", 1.5)]
    if profile == "na_kdr_hcn":
        return [make_channel("na", 6.0), make_channel("kdr", 1.5), make_channel("hcn", 0.05)]
    if profile == "full_restrained":
        return [
            make_channel("na", 6.0),
            make_channel("kdr", 1.5),
            make_channel("hcn", 0.05),
            make_channel("ka", 0.5),
            make_channel("cat", 0.05),
        ]
    raise ValueError(f"unsupported active profile: {profile}")


def audit_channel_gates(channels: list[ActiveChannel], voltages_V: np.ndarray) -> dict[str, float]:
    values: list[float] = []
    taus: list[float] = []
    for channel in channels:
        for voltage_V in voltages_V:
            for gate in channel.gate_names:
                inf, tau_s = channel.gate_inf_tau_s(gate, float(voltage_V))
                values.append(inf)
                taus.append(tau_s)
    return {
        "min_gate_inf": float(min(values)) if values else 0.0,
        "max_gate_inf": float(max(values)) if values else 0.0,
        "min_tau_s": float(min(taus)) if taus else 0.0,
        "max_tau_s": float(max(taus)) if taus else 0.0,
    }
