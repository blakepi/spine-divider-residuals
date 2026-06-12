"""Phase 04 nonlinear active-network solver."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from spine.channels import ActiveChannel
from spine.network import PassiveNetwork
from spine.synapses import AMPANMDASynapse


@dataclass(frozen=True)
class ChannelPlacement:
    compartment_index: int
    channel: ActiveChannel
    label: str = ""


@dataclass(frozen=True)
class SynapsePlacement:
    compartment_index: int
    synapse: AMPANMDASynapse
    label: str = ""


@dataclass(frozen=True)
class VoltageClamp:
    compartment_index: int
    conductance_S: float
    command_fn: Callable[[float], float]
    label: str = "voltage_clamp"

    def __post_init__(self) -> None:
        if self.conductance_S <= 0:
            raise ValueError("voltage-clamp conductance must be positive")


@dataclass(frozen=True)
class ActiveSimulationResult:
    time_s: np.ndarray
    voltage_V: np.ndarray
    gate_history: dict[str, np.ndarray]
    synaptic_conductance_S: np.ndarray
    method: str
    channel_placements: tuple[ChannelPlacement, ...]
    synapse_placements: tuple[SynapsePlacement, ...]

    @property
    def max_gate_value(self) -> float:
        if not self.gate_history:
            return 0.0
        return float(max(np.max(values) for values in self.gate_history.values()))

    @property
    def min_gate_value(self) -> float:
        if not self.gate_history:
            return 0.0
        return float(min(np.min(values) for values in self.gate_history.values()))

    @property
    def finite(self) -> bool:
        return bool(np.all(np.isfinite(self.voltage_V))) and all(
            bool(np.all(np.isfinite(values))) for values in self.gate_history.values()
        )


def place_channels(
    channels: list[ActiveChannel],
    compartment_indices: list[int],
    label_prefix: str = "active",
) -> list[ChannelPlacement]:
    placements: list[ChannelPlacement] = []
    for compartment_index in compartment_indices:
        for channel in channels:
            placements.append(
                ChannelPlacement(
                    compartment_index=compartment_index,
                    channel=channel,
                    label=f"{label_prefix}_{compartment_index}_{channel.name}",
                )
            )
    return placements


def _capacitance_diagonal(network: PassiveNetwork) -> np.ndarray:
    c = network.capacitance_vector()
    if np.any(c <= 0):
        raise ValueError("all compartment capacitances must be positive")
    return c


def initialize_gates(
    network: PassiveNetwork,
    placements: list[ChannelPlacement],
    initial_voltage_V: np.ndarray | None = None,
) -> list[dict[str, float]]:
    voltage = initial_voltage_V if initial_voltage_V is not None else network.resting_voltage_vector()
    states: list[dict[str, float]] = []
    for placement in placements:
        states.append(placement.channel.initialize(float(voltage[placement.compartment_index])))
    return states


def _gate_key(placement_index: int, placement: ChannelPlacement, gate_name: str) -> str:
    label = placement.label or placement.channel.name
    return f"{placement_index}:{label}:{gate_name}"


def _assemble_active_terms(
    network: PassiveNetwork,
    channel_placements: tuple[ChannelPlacement, ...],
    synapse_placements: tuple[SynapsePlacement, ...],
    gate_states: list[dict[str, float]],
    voltage_for_nonlinear_terms_V: np.ndarray,
    time_s: float,
    external_current_A: np.ndarray,
    voltage_clamps: tuple[VoltageClamp, ...],
) -> tuple[np.ndarray, np.ndarray, float]:
    matrix = network.assemble_dense_admittance().astype(float)
    source = network.source_vector().astype(float)
    total_synaptic_g = 0.0

    for placement, gates in zip(channel_placements, gate_states):
        idx = placement.compartment_index
        g = placement.channel.conductance_S(gates)
        matrix[idx, idx] += g
        source[idx] += g * placement.channel.reversal_V

    for placement in synapse_placements:
        idx = placement.compartment_index
        voltage = float(voltage_for_nonlinear_terms_V[idx])
        g, syn_source = placement.synapse.source_terms_at(time_s, voltage)
        matrix[idx, idx] += g
        source[idx] += syn_source
        total_synaptic_g += g

    for clamp in voltage_clamps:
        command_V = clamp.command_fn(time_s)
        idx = clamp.compartment_index
        matrix[idx, idx] += clamp.conductance_S
        source[idx] += clamp.conductance_S * command_V

    source = source + external_current_A
    return matrix, source, total_synaptic_g


def simulate_active_network(
    network: PassiveNetwork,
    channel_placements: list[ChannelPlacement] | tuple[ChannelPlacement, ...],
    synapse_placements: list[SynapsePlacement] | tuple[SynapsePlacement, ...],
    dt_s: float,
    stop_s: float,
    method: str = "semi_implicit",
    initial_voltage_V: np.ndarray | None = None,
    external_current_fn: Callable[[float], np.ndarray] | None = None,
    voltage_clamps: list[VoltageClamp] | tuple[VoltageClamp, ...] | None = None,
    voltage_bounds_V: tuple[float, float] = (-0.200, 0.150),
) -> ActiveSimulationResult:
    """Simulate passive network plus active channels and nonlinear synapses.

    `semi_implicit` updates gates from the previous voltage and solves the
    voltage equation implicitly with those conductances. `explicit_euler` uses
    the same gate update and conductances but advances voltage explicitly; it
    is intended as an independent small-step cross-check, not as the default.
    """
    if dt_s <= 0 or stop_s <= 0:
        raise ValueError("dt_s and stop_s must be positive")
    if method not in {"semi_implicit", "explicit_euler"}:
        raise ValueError(f"unsupported active solver method: {method}")
    lo, hi = voltage_bounds_V
    if lo >= hi:
        raise ValueError("invalid voltage bounds")

    channel_tuple = tuple(channel_placements)
    synapse_tuple = tuple(synapse_placements)
    clamp_tuple = tuple(voltage_clamps or ())
    for placement in channel_tuple:
        network._check_index(placement.compartment_index)
    for placement in synapse_tuple:
        network._check_index(placement.compartment_index)
    for clamp in clamp_tuple:
        network._check_index(clamp.compartment_index)

    times = np.arange(0.0, stop_s + 0.5 * dt_s, dt_s)
    voltage = np.empty((len(times), network.n), dtype=float)
    voltage[0, :] = initial_voltage_V if initial_voltage_V is not None else network.resting_voltage_vector()
    if np.any(voltage[0, :] < lo) or np.any(voltage[0, :] > hi):
        raise ValueError("initial voltage outside stability bounds")

    capacitance = _capacitance_diagonal(network)
    c_over_dt = np.diag(capacitance / dt_s)
    gate_states = initialize_gates(network, list(channel_tuple), voltage[0, :])

    gate_history: dict[str, np.ndarray] = {}
    for placement_index, placement in enumerate(channel_tuple):
        for gate_name in placement.channel.gate_names:
            key = _gate_key(placement_index, placement, gate_name)
            gate_history[key] = np.empty(len(times), dtype=float)
            gate_history[key][0] = gate_states[placement_index][gate_name]

    synaptic_conductance = np.zeros(len(times), dtype=float)
    zero_current = np.zeros(network.n, dtype=float)

    for k in range(1, len(times)):
        t = float(times[k])
        previous_voltage = voltage[k - 1, :]
        for placement_index, placement in enumerate(channel_tuple):
            idx = placement.compartment_index
            gate_states[placement_index] = placement.channel.update_gates(
                gate_states[placement_index],
                float(previous_voltage[idx]),
                dt_s,
            )

        external_current_A = (
            np.asarray(external_current_fn(t), dtype=float)
            if external_current_fn is not None
            else zero_current
        )
        if external_current_A.shape != (network.n,):
            raise ValueError("external_current_fn returned wrong shape")

        matrix, source, syn_g = _assemble_active_terms(
            network,
            channel_tuple,
            synapse_tuple,
            gate_states,
            previous_voltage,
            t,
            external_current_A,
            clamp_tuple,
        )
        synaptic_conductance[k] = syn_g

        if method == "semi_implicit":
            lhs = c_over_dt + matrix
            rhs = c_over_dt @ previous_voltage + source
            voltage[k, :] = np.linalg.solve(lhs, rhs)
        else:
            derivative = (-matrix @ previous_voltage + source) / capacitance
            voltage[k, :] = previous_voltage + dt_s * derivative

        if not np.all(np.isfinite(voltage[k, :])):
            raise FloatingPointError("voltage became nonfinite")
        if np.any(voltage[k, :] < lo) or np.any(voltage[k, :] > hi):
            raise FloatingPointError("voltage left configured stability bounds")

        for placement_index, placement in enumerate(channel_tuple):
            for gate_name in placement.channel.gate_names:
                gate_history[_gate_key(placement_index, placement, gate_name)][k] = gate_states[
                    placement_index
                ][gate_name]

    return ActiveSimulationResult(
        time_s=times,
        voltage_V=voltage,
        gate_history=gate_history,
        synaptic_conductance_S=synaptic_conductance,
        method=method,
        channel_placements=channel_tuple,
        synapse_placements=synapse_tuple,
    )


def peak_depolarization_metrics(
    result: ActiveSimulationResult,
    head_index: int,
    observe_indices: dict[str, int],
    event_time_s: float,
    metric_window_s: float,
) -> dict[str, float]:
    times = result.time_s
    baseline_index = max(0, int(np.searchsorted(times, event_time_s)) - 1)
    mask = (times >= event_time_s) & (times <= event_time_s + metric_window_s)
    if not np.any(mask):
        raise ValueError("metric window contains no samples")
    head_depol = result.voltage_V[mask, head_index] - result.voltage_V[baseline_index, head_index]
    ah = float(np.max(head_depol))
    out = {
        "A_h_mV": ah * 1e3,
        "V_h_peak_mV": float(np.max(result.voltage_V[mask, head_index]) * 1e3),
        "V_h_min_mV": float(np.min(result.voltage_V[mask, head_index]) * 1e3),
    }
    for label, idx in observe_indices.items():
        depol = result.voltage_V[mask, idx] - result.voltage_V[baseline_index, idx]
        amp = float(np.max(depol))
        out[f"A_{label}_mV"] = amp * 1e3
        out[f"Gamma_h_to_{label}"] = amp / ah if ah != 0 else float("nan")
        out[f"V_{label}_peak_mV"] = float(np.max(result.voltage_V[mask, idx]) * 1e3)
        out[f"V_{label}_min_mV"] = float(np.min(result.voltage_V[mask, idx]) * 1e3)
    if "Gamma_h_to_d" in out:
        out["local_voltage_isolation"] = 1.0 - float(out["Gamma_h_to_d"])
    out["max_voltage_mV"] = float(np.max(result.voltage_V) * 1e3)
    out["min_voltage_mV"] = float(np.min(result.voltage_V) * 1e3)
    out["min_gate"] = result.min_gate_value
    out["max_gate"] = result.max_gate_value
    return out


def frozen_gate_admittance(
    network: PassiveNetwork,
    channel_placements: list[ChannelPlacement] | tuple[ChannelPlacement, ...],
    operating_voltage_V: np.ndarray | None = None,
) -> np.ndarray:
    """Return a frozen-gate operating-point conductance matrix.

    This is an exploratory Phase 04 impedance approximation. It adds channel
    chord conductances at the stated operating point but does not include
    dynamic gate derivatives.
    """
    voltage = operating_voltage_V if operating_voltage_V is not None else network.resting_voltage_vector()
    matrix = network.assemble_dense_admittance().astype(float)
    for placement in channel_placements:
        gates = placement.channel.initialize(float(voltage[placement.compartment_index]))
        matrix[placement.compartment_index, placement.compartment_index] += placement.channel.conductance_S(gates)
    return matrix


def frozen_gate_impedance(
    network: PassiveNetwork,
    channel_placements: list[ChannelPlacement] | tuple[ChannelPlacement, ...],
    source_index: int,
    target_index: int,
    frequency_hz: float,
) -> complex:
    omega = 2.0 * np.pi * frequency_hz
    matrix = frozen_gate_admittance(network, channel_placements).astype(complex)
    matrix = matrix + 1j * omega * network.capacitance_matrix()
    injection = np.zeros(network.n, dtype=complex)
    injection[source_index] = 1.0
    response = np.linalg.solve(matrix, injection)
    return complex(response[target_index])
