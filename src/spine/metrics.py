"""Voltage, current, and transfer metrics for Phase 01."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from spine.passive import SimulationResult


@dataclass(frozen=True)
class VoltageMetrics:
    amplitude_head_V: float
    amplitude_dendrite_V: float
    amplitude_soma_V: float
    gamma_head_to_dendrite: float
    gamma_head_to_soma: float
    gamma_dendrite_to_soma: float
    latency_head_s: float
    latency_dendrite_s: float
    latency_soma_s: float
    half_width_head_s: float
    half_width_dendrite_s: float
    half_width_soma_s: float
    integral_head_V_s: float
    integral_dendrite_V_s: float
    integral_soma_V_s: float
    peak_synaptic_current_A: float
    integrated_synaptic_current_C: float
    peak_neck_current_A: float
    integrated_neck_current_C: float
    dendritic_charge_from_neck_C: float
    peak_driving_force_V: float
    initial_abs_driving_force_V: float
    minimum_abs_driving_force_V: float
    driving_force_reduction_V: float


def _window(result: SimulationResult) -> np.ndarray:
    p = result.parameters
    start = p.synapse.event_time_s
    stop = start + p.metric_window_s
    return (result.time_s >= start) & (result.time_s <= stop)


def _amplitude_latency_half_width(
    time_s: np.ndarray, signal_V: np.ndarray, baseline_V: float
) -> tuple[float, float, float, float]:
    depol = signal_V - baseline_V
    peak_index = int(np.argmax(depol))
    amplitude = float(depol[peak_index])
    latency = float(time_s[peak_index] - time_s[0])
    integral = float(np.trapezoid(depol, time_s))
    if amplitude <= 0:
        return amplitude, latency, 0.0, integral
    above = depol >= 0.5 * amplitude
    indices = np.flatnonzero(above)
    half_width = float(time_s[indices[-1]] - time_s[indices[0]]) if len(indices) else 0.0
    return amplitude, latency, half_width, integral


def compute_voltage_metrics(result: SimulationResult) -> VoltageMetrics:
    mask = _window(result)
    times = result.time_s[mask]
    voltage = result.voltage_V[mask, :]
    if len(times) < 2:
        raise ValueError("metric window must include at least two samples")
    baseline_index = int(np.searchsorted(result.time_s, result.parameters.synapse.event_time_s))
    baseline = result.voltage_V[baseline_index, :]

    ah, lh, hwh, ih = _amplitude_latency_half_width(times, voltage[:, 0], baseline[0])
    ad, ld, hwd, id_ = _amplitude_latency_half_width(times, voltage[:, 1], baseline[1])
    a_s, ls, hws, is_ = _amplitude_latency_half_width(times, voltage[:, 2], baseline[2])
    gamma_hd = ad / ah if ah != 0 else float("nan")
    gamma_hs = a_s / ah if ah != 0 else float("nan")
    gamma_ds = a_s / ad if ad != 0 else float("nan")

    driving_force = voltage[:, 0] - result.parameters.synaptic_reversal_V
    abs_driving_force = np.abs(driving_force)
    syn_current = result.g_syn_S[mask] * driving_force
    neck_current = result.neck_conductance_S * (voltage[:, 0] - voltage[:, 1])
    initial_abs_driving_force = float(abs_driving_force[0])
    minimum_abs_driving_force = float(np.min(abs_driving_force))

    return VoltageMetrics(
        amplitude_head_V=ah,
        amplitude_dendrite_V=ad,
        amplitude_soma_V=a_s,
        gamma_head_to_dendrite=float(gamma_hd),
        gamma_head_to_soma=float(gamma_hs),
        gamma_dendrite_to_soma=float(gamma_ds),
        latency_head_s=lh,
        latency_dendrite_s=ld,
        latency_soma_s=ls,
        half_width_head_s=hwh,
        half_width_dendrite_s=hwd,
        half_width_soma_s=hws,
        integral_head_V_s=ih,
        integral_dendrite_V_s=id_,
        integral_soma_V_s=is_,
        peak_synaptic_current_A=float(np.min(syn_current)),
        integrated_synaptic_current_C=float(np.trapezoid(syn_current, times)),
        peak_neck_current_A=float(np.max(neck_current)),
        integrated_neck_current_C=float(np.trapezoid(neck_current, times)),
        dendritic_charge_from_neck_C=float(np.trapezoid(neck_current, times)),
        peak_driving_force_V=float(np.max(abs_driving_force)),
        initial_abs_driving_force_V=initial_abs_driving_force,
        minimum_abs_driving_force_V=minimum_abs_driving_force,
        driving_force_reduction_V=initial_abs_driving_force - minimum_abs_driving_force,
    )
