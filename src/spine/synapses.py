"""Conductance-based manuscript synapse."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class DoubleExponentialSynapse:
    g_max_S: float
    tau_rise_s: float
    tau_decay_s: float
    event_time_s: float
    reversal_V: float

    def __post_init__(self) -> None:
        if self.g_max_S < 0:
            raise ValueError("g_max_S must be nonnegative")
        if self.tau_rise_s <= 0 or self.tau_decay_s <= 0:
            raise ValueError("synaptic time constants must be positive")
        if self.tau_decay_s <= self.tau_rise_s:
            raise ValueError("tau_decay_s must exceed tau_rise_s")

    @property
    def peak_delay_s(self) -> float:
        tr = self.tau_rise_s
        td = self.tau_decay_s
        return tr * td / (td - tr) * math.log(td / tr)

    @property
    def eta(self) -> float:
        tp = self.peak_delay_s
        value = math.exp(-tp / self.tau_decay_s) - math.exp(-tp / self.tau_rise_s)
        return 1.0 / value

    def conductance_at(self, time_s: float) -> float:
        dt = time_s - self.event_time_s
        if dt < 0.0 or self.g_max_S == 0.0:
            return 0.0
        return self.g_max_S * self.eta * (
            math.exp(-dt / self.tau_decay_s) - math.exp(-dt / self.tau_rise_s)
        )

    def conductance(self, times_s: np.ndarray) -> np.ndarray:
        dt = times_s - self.event_time_s
        values = np.zeros_like(times_s, dtype=float)
        mask = dt >= 0.0
        values[mask] = self.g_max_S * self.eta * (
            np.exp(-dt[mask] / self.tau_decay_s)
            - np.exp(-dt[mask] / self.tau_rise_s)
        )
        return values

    def analytical_peak_conductance_S(self) -> float:
        return self.conductance_at(self.event_time_s + self.peak_delay_s)

    def discrete_peak_error_S(self, dt_s: float, stop_s: float) -> float:
        if dt_s <= 0 or stop_s <= self.event_time_s:
            raise ValueError("dt_s must be positive and stop_s must exceed event_time_s")
        times = np.arange(0.0, stop_s + 0.5 * dt_s, dt_s)
        return float(np.max(self.conductance(times)) - self.g_max_S)


def magnesium_block(
    voltage_V: float | np.ndarray,
    magnesium_mM: float = 1.0,
    eta_mM: float = 3.57,
    gamma_per_mV: float = 0.062,
) -> float | np.ndarray:
    """Return the voltage-dependent NMDA magnesium unblock factor.

    The form follows the common Jahr-Stevens-style phenomenological factor
    `1 / (1 + [Mg]/eta * exp(-gamma * V_mV))`. Voltage is the absolute
    membrane potential in volts and is converted to millivolts internally.
    """
    if magnesium_mM < 0:
        raise ValueError("magnesium_mM must be nonnegative")
    if eta_mM <= 0 or gamma_per_mV <= 0:
        raise ValueError("eta_mM and gamma_per_mV must be positive")
    voltage_mV = np.asarray(voltage_V) * 1e3
    value = 1.0 / (1.0 + (magnesium_mM / eta_mM) * np.exp(-gamma_per_mV * voltage_mV))
    if np.isscalar(voltage_V):
        return float(value)
    return value


@dataclass(frozen=True)
class MultiEventDoubleExponentialSynapse:
    """Normalized double-exponential conductance summed over event times."""

    g_max_S: float
    tau_rise_s: float
    tau_decay_s: float
    event_times_s: tuple[float, ...]
    reversal_V: float

    def __post_init__(self) -> None:
        if self.g_max_S < 0:
            raise ValueError("g_max_S must be nonnegative")
        if self.tau_rise_s <= 0 or self.tau_decay_s <= 0:
            raise ValueError("synaptic time constants must be positive")
        if self.tau_decay_s <= self.tau_rise_s:
            raise ValueError("tau_decay_s must exceed tau_rise_s")
        if any(t < 0 for t in self.event_times_s):
            raise ValueError("event times must be nonnegative")

    @classmethod
    def from_events(
        cls,
        g_max_S: float,
        tau_rise_s: float,
        tau_decay_s: float,
        event_times_s: Iterable[float],
        reversal_V: float,
    ) -> "MultiEventDoubleExponentialSynapse":
        return cls(
            g_max_S=g_max_S,
            tau_rise_s=tau_rise_s,
            tau_decay_s=tau_decay_s,
            event_times_s=tuple(float(t) for t in event_times_s),
            reversal_V=reversal_V,
        )

    @property
    def template(self) -> DoubleExponentialSynapse:
        return DoubleExponentialSynapse(
            g_max_S=self.g_max_S,
            tau_rise_s=self.tau_rise_s,
            tau_decay_s=self.tau_decay_s,
            event_time_s=0.0,
            reversal_V=self.reversal_V,
        )

    @property
    def peak_delay_s(self) -> float:
        return self.template.peak_delay_s

    @property
    def eta(self) -> float:
        return self.template.eta

    def conductance_at(self, time_s: float) -> float:
        total = 0.0
        for event_time_s in self.event_times_s:
            total += DoubleExponentialSynapse(
                self.g_max_S,
                self.tau_rise_s,
                self.tau_decay_s,
                event_time_s,
                self.reversal_V,
            ).conductance_at(time_s)
        return total

    def conductance(self, times_s: np.ndarray) -> np.ndarray:
        total = np.zeros_like(times_s, dtype=float)
        for event_time_s in self.event_times_s:
            total += DoubleExponentialSynapse(
                self.g_max_S,
                self.tau_rise_s,
                self.tau_decay_s,
                event_time_s,
                self.reversal_V,
            ).conductance(times_s)
        return total


@dataclass(frozen=True)
class AMPANMDASynapse:
    """Configurable AMPA-only or AMPA+NMDA excitatory synapse.

    AMPA is voltage independent. NMDA uses the same normalized conductance
    family multiplied by the magnesium unblock factor at the local voltage.
    Conductance and current values are SI: siemens, volts, amperes, seconds.
    """

    ampa: MultiEventDoubleExponentialSynapse
    nmda: MultiEventDoubleExponentialSynapse | None = None
    magnesium_mM: float = 1.0
    nmda_eta_mM: float = 3.57
    nmda_gamma_per_mV: float = 0.062
    label: str = "AMPA"

    def __post_init__(self) -> None:
        if self.magnesium_mM < 0:
            raise ValueError("magnesium_mM must be nonnegative")
        if self.nmda_eta_mM <= 0 or self.nmda_gamma_per_mV <= 0:
            raise ValueError("NMDA magnesium block parameters must be positive")

    @property
    def has_nmda(self) -> bool:
        return self.nmda is not None and self.nmda.g_max_S > 0

    def raw_conductances_at(self, time_s: float) -> dict[str, float]:
        out = {"AMPA": self.ampa.conductance_at(time_s)}
        out["NMDA_raw"] = self.nmda.conductance_at(time_s) if self.nmda is not None else 0.0
        return out

    def effective_conductances_at(self, time_s: float, voltage_V: float) -> dict[str, float]:
        raw = self.raw_conductances_at(time_s)
        block = magnesium_block(
            voltage_V,
            magnesium_mM=self.magnesium_mM,
            eta_mM=self.nmda_eta_mM,
            gamma_per_mV=self.nmda_gamma_per_mV,
        )
        raw["NMDA_block"] = float(block)
        raw["NMDA"] = raw["NMDA_raw"] * float(block)
        return raw

    def source_terms_at(self, time_s: float, voltage_V: float) -> tuple[float, float]:
        """Return `(total_conductance_S, reversal_weighted_source_A_per_V)`.

        The returned source is the conductance-weighted reversal term used in
        `C dV/dt = -G V + source`.
        """
        conductances = self.effective_conductances_at(time_s, voltage_V)
        g_ampa = conductances["AMPA"]
        g_nmda = conductances["NMDA"]
        e_ampa = self.ampa.reversal_V
        e_nmda = self.nmda.reversal_V if self.nmda is not None else e_ampa
        return g_ampa + g_nmda, g_ampa * e_ampa + g_nmda * e_nmda

    def current_A(self, time_s: float, voltage_V: float) -> float:
        """Return outward synaptic current at the local voltage."""
        conductances = self.effective_conductances_at(time_s, voltage_V)
        i_ampa = conductances["AMPA"] * (voltage_V - self.ampa.reversal_V)
        if self.nmda is None:
            return i_ampa
        i_nmda = conductances["NMDA"] * (voltage_V - self.nmda.reversal_V)
        return i_ampa + i_nmda


def make_ampa_nmda_synapse(
    event_times_s: Iterable[float],
    ampa_g_max_S: float,
    nmda_g_max_S: float = 0.0,
    ampa_tau_rise_s: float = 0.0003,
    ampa_tau_decay_s: float = 0.003,
    nmda_tau_rise_s: float = 0.002,
    nmda_tau_decay_s: float = 0.080,
    reversal_V: float = 0.0,
    magnesium_mM: float = 1.0,
    label: str = "AMPA",
) -> AMPANMDASynapse:
    ampa = MultiEventDoubleExponentialSynapse.from_events(
        g_max_S=ampa_g_max_S,
        tau_rise_s=ampa_tau_rise_s,
        tau_decay_s=ampa_tau_decay_s,
        event_times_s=event_times_s,
        reversal_V=reversal_V,
    )
    nmda = None
    if nmda_g_max_S > 0:
        nmda = MultiEventDoubleExponentialSynapse.from_events(
            g_max_S=nmda_g_max_S,
            tau_rise_s=nmda_tau_rise_s,
            tau_decay_s=nmda_tau_decay_s,
            event_times_s=event_times_s,
            reversal_V=reversal_V,
        )
    return AMPANMDASynapse(ampa=ampa, nmda=nmda, magnesium_mM=magnesium_mM, label=label)
