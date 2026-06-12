"""Manuscript-faithful passive three-compartment core."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from spine.config import SpineConfig, load_config
from spine.geometry import cylindrical_neck_resistance_ohm, sphere_area_um2
from spine.synapses import DoubleExponentialSynapse
from spine.units import mV_to_V, ms_to_s, nS_to_S, pA_to_A, pF_to_F


@dataclass(frozen=True)
class PassiveParameters:
    leak_reversal_V: float
    synaptic_reversal_V: float
    c_head_F: float
    c_dendrite_F: float
    c_soma_F: float
    g_leak_head_S: float
    g_leak_dendrite_S: float
    g_leak_soma_S: float
    g_dendrite_soma_S: float
    intracellular_resistivity_ohm_cm: float
    synapse: DoubleExponentialSynapse
    dt_s: float
    stop_s: float
    metric_window_s: float
    input_resistance_current_A: float

    def __post_init__(self) -> None:
        positive_fields = {
            "c_head_F": self.c_head_F,
            "c_dendrite_F": self.c_dendrite_F,
            "c_soma_F": self.c_soma_F,
            "g_leak_head_S": self.g_leak_head_S,
            "g_leak_dendrite_S": self.g_leak_dendrite_S,
            "g_leak_soma_S": self.g_leak_soma_S,
            "g_dendrite_soma_S": self.g_dendrite_soma_S,
            "intracellular_resistivity_ohm_cm": self.intracellular_resistivity_ohm_cm,
            "dt_s": self.dt_s,
            "stop_s": self.stop_s,
            "metric_window_s": self.metric_window_s,
            "input_resistance_current_A": self.input_resistance_current_A,
        }
        for name, value in positive_fields.items():
            if value <= 0:
                raise ValueError(f"{name} must be positive")
        if self.stop_s <= self.synapse.event_time_s:
            raise ValueError("stop_s must exceed synapse event_time_s")
        if self.synapse.event_time_s + self.metric_window_s > self.stop_s:
            raise ValueError("metric window must end at or before stop_s")


@dataclass(frozen=True)
class SimulationResult:
    time_s: np.ndarray
    voltage_V: np.ndarray
    g_syn_S: np.ndarray
    neck_resistance_ohm: float
    neck_conductance_S: float
    parameters: PassiveParameters

    @property
    def head_V(self) -> np.ndarray:
        return self.voltage_V[:, 0]

    @property
    def dendrite_V(self) -> np.ndarray:
        return self.voltage_V[:, 1]

    @property
    def soma_V(self) -> np.ndarray:
        return self.voltage_V[:, 2]


def parameters_from_config(config: SpineConfig) -> PassiveParameters:
    if config.track != "manuscript_faithful":
        raise ValueError("Phase 01 passive core accepts only manuscript_faithful configs")

    area_um2 = sphere_area_um2(config.get("spine_head", "radius_um"))
    c_head_pF = config.get("spine_head", "specific_capacitance_pF_per_um2") * area_um2
    g_head_nS = config.get("spine_head", "specific_leak_nS_per_um2") * area_um2

    synapse = DoubleExponentialSynapse(
        g_max_S=nS_to_S(config.get("synapse", "g_max_nS")),
        tau_rise_s=ms_to_s(config.get("synapse", "tau_rise_ms")),
        tau_decay_s=ms_to_s(config.get("synapse", "tau_decay_ms")),
        event_time_s=ms_to_s(config.get("synapse", "event_time_ms")),
        reversal_V=mV_to_V(config.get("reversal", "excitatory_synapse_mV")),
    )

    return PassiveParameters(
        leak_reversal_V=mV_to_V(config.get("reversal", "leak_mV")),
        synaptic_reversal_V=mV_to_V(config.get("reversal", "excitatory_synapse_mV")),
        c_head_F=pF_to_F(c_head_pF),
        c_dendrite_F=pF_to_F(config.get("dendrite", "capacitance_pF")),
        c_soma_F=pF_to_F(config.get("soma", "capacitance_pF")),
        g_leak_head_S=nS_to_S(g_head_nS),
        g_leak_dendrite_S=nS_to_S(config.get("dendrite", "leak_conductance_nS")),
        g_leak_soma_S=nS_to_S(config.get("soma", "leak_conductance_nS")),
        g_dendrite_soma_S=nS_to_S(config.get("coupling", "dendrite_soma_conductance_nS")),
        intracellular_resistivity_ohm_cm=config.get("coupling", "intracellular_resistivity_ohm_cm"),
        synapse=synapse,
        dt_s=ms_to_s(config.get("numerics", "time_step_ms")),
        stop_s=ms_to_s(config.get("numerics", "simulation_stop_ms")),
        metric_window_s=ms_to_s(config.get("numerics", "metric_window_ms")),
        input_resistance_current_A=pA_to_A(config.get("numerics", "input_resistance_current_pA")),
    )


def load_manuscript_parameters(path: str | Path) -> PassiveParameters:
    return parameters_from_config(load_config(path))


def capacitance_matrix(parameters: PassiveParameters) -> np.ndarray:
    return np.diag([parameters.c_head_F, parameters.c_dendrite_F, parameters.c_soma_F])


def assemble_passive_matrix(
    parameters: PassiveParameters, neck_conductance_S: float, g_syn_S: float
) -> tuple[np.ndarray, np.ndarray]:
    if neck_conductance_S < 0 or g_syn_S < 0:
        raise ValueError("conductances must be nonnegative")
    glh = parameters.g_leak_head_S
    gld = parameters.g_leak_dendrite_S
    gls = parameters.g_leak_soma_S
    gds = parameters.g_dendrite_soma_S
    e_l = parameters.leak_reversal_V
    e_syn = parameters.synaptic_reversal_V

    matrix = np.array(
        [
            [glh + g_syn_S + neck_conductance_S, -neck_conductance_S, 0.0],
            [-neck_conductance_S, gld + neck_conductance_S + gds, -gds],
            [0.0, -gds, gls + gds],
        ],
        dtype=float,
    )
    source = np.array([glh * e_l + g_syn_S * e_syn, gld * e_l, gls * e_l], dtype=float)
    return matrix, source


def simulate_three_compartment(
    parameters: PassiveParameters,
    neck_length_um: float,
    neck_radius_um: float,
    method: str = "backward_euler",
) -> SimulationResult:
    r_neck = cylindrical_neck_resistance_ohm(
        parameters.intracellular_resistivity_ohm_cm, neck_length_um, neck_radius_um
    )
    return simulate_with_neck_resistance(parameters, r_neck, method=method)


def simulate_with_neck_resistance(
    parameters: PassiveParameters,
    neck_resistance_ohm: float,
    method: str = "backward_euler",
) -> SimulationResult:
    if neck_resistance_ohm <= 0:
        raise ValueError("neck_resistance_ohm must be positive")
    dt = parameters.dt_s
    times = np.arange(0.0, parameters.stop_s + 0.5 * dt, dt)
    voltages = np.empty((len(times), 3), dtype=float)
    voltages[0, :] = parameters.leak_reversal_V
    c_matrix = capacitance_matrix(parameters)
    c_over_dt = c_matrix / dt
    g_neck = 1.0 / neck_resistance_ohm
    g_syn = parameters.synapse.conductance(times)

    previous_matrix, previous_source = assemble_passive_matrix(parameters, g_neck, g_syn[0])
    for i in range(1, len(times)):
        current_matrix, current_source = assemble_passive_matrix(parameters, g_neck, g_syn[i])
        if method == "backward_euler":
            lhs = c_over_dt + current_matrix
            rhs = c_over_dt @ voltages[i - 1] + current_source
        elif method == "crank_nicolson":
            lhs = c_over_dt + 0.5 * current_matrix
            rhs = (
                (c_over_dt - 0.5 * previous_matrix) @ voltages[i - 1]
                + 0.5 * (previous_source + current_source)
            )
        else:
            raise ValueError(f"unsupported method: {method}")
        voltages[i, :] = np.linalg.solve(lhs, rhs)
        previous_matrix = current_matrix
        previous_source = current_source

    return SimulationResult(
        time_s=times,
        voltage_V=voltages,
        g_syn_S=g_syn,
        neck_resistance_ohm=neck_resistance_ohm,
        neck_conductance_S=g_neck,
        parameters=parameters,
    )
