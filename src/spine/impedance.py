"""DC input resistance and SMI helpers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from spine.network import PassiveNetwork
from spine.passive import PassiveParameters


@dataclass(frozen=True)
class InputResistanceResult:
    steady_state_ohm: float
    time_domain_ohm: float
    delta_voltage_dendrite_V: float
    delta_voltage_soma_V: float


def dendrite_soma_time_constants_s(parameters: PassiveParameters) -> np.ndarray:
    """Return passive dendrite-soma load time constants with the spine omitted."""
    c = np.diag([parameters.c_dendrite_F, parameters.c_soma_F])
    gld = parameters.g_leak_dendrite_S
    gls = parameters.g_leak_soma_S
    gds = parameters.g_dendrite_soma_S
    matrix = np.array([[gld + gds, -gds], [-gds, gls + gds]], dtype=float)
    rates = np.linalg.eigvals(np.linalg.solve(c, matrix))
    return np.sort(1.0 / np.real(rates))


def dendritic_input_resistance_steady_state_ohm(
    parameters: PassiveParameters,
) -> tuple[float, np.ndarray]:
    """Compute R_in,d from the dendrite-soma load with the spine omitted."""
    gld = parameters.g_leak_dendrite_S
    gls = parameters.g_leak_soma_S
    gds = parameters.g_dendrite_soma_S
    matrix = np.array([[gld + gds, -gds], [-gds, gls + gds]], dtype=float)
    rhs = np.array([parameters.input_resistance_current_A, 0.0], dtype=float)
    delta_v = np.linalg.solve(matrix, rhs)
    return float(delta_v[0] / parameters.input_resistance_current_A), delta_v


def dendritic_input_resistance_time_domain_ohm(
    parameters: PassiveParameters,
    duration_s: float = 1.0,
) -> tuple[float, np.ndarray]:
    """Time-domain check using only dendrite and soma; spine is absent."""
    if duration_s <= 0:
        raise ValueError("duration_s must be positive")
    slowest_tau_s = float(np.max(dendrite_soma_time_constants_s(parameters)))
    if duration_s < 10.0 * slowest_tau_s:
        raise ValueError("duration_s must be at least 10 dendrite-soma time constants")
    dt = parameters.dt_s
    times = np.arange(0.0, duration_s + 0.5 * dt, dt)
    c = np.diag([parameters.c_dendrite_F, parameters.c_soma_F])
    c_over_dt = c / dt
    gld = parameters.g_leak_dendrite_S
    gls = parameters.g_leak_soma_S
    gds = parameters.g_dendrite_soma_S
    matrix = np.array([[gld + gds, -gds], [-gds, gls + gds]], dtype=float)
    source = np.array([gld * parameters.leak_reversal_V, gls * parameters.leak_reversal_V])
    injection = np.array([parameters.input_resistance_current_A, 0.0])
    voltage = np.empty((len(times), 2), dtype=float)
    voltage[0, :] = parameters.leak_reversal_V
    lhs = c_over_dt + matrix
    for i in range(1, len(times)):
        rhs = c_over_dt @ voltage[i - 1] + source + injection
        voltage[i, :] = np.linalg.solve(lhs, rhs)
    delta_v = voltage[-1, :] - parameters.leak_reversal_V
    return float(delta_v[0] / parameters.input_resistance_current_A), delta_v


def dendritic_input_resistance_ohm(parameters: PassiveParameters) -> InputResistanceResult:
    steady, steady_delta = dendritic_input_resistance_steady_state_ohm(parameters)
    dynamic, _ = dendritic_input_resistance_time_domain_ohm(parameters)
    return InputResistanceResult(
        steady_state_ohm=steady,
        time_domain_ohm=dynamic,
        delta_voltage_dendrite_V=float(steady_delta[0]),
        delta_voltage_soma_V=float(steady_delta[1]),
    )


def smi(neck_resistance_ohm: float, dendritic_input_resistance_ohm_value: float) -> float:
    if neck_resistance_ohm <= 0 or dendritic_input_resistance_ohm_value <= 0:
        raise ValueError("resistances must be positive")
    return neck_resistance_ohm / dendritic_input_resistance_ohm_value


def local_input_impedance(
    network: PassiveNetwork, compartment_index: int, frequency_hz: float
) -> complex:
    injection = np.zeros(network.n, dtype=complex)
    injection[compartment_index] = 1.0
    response = network.solve_frequency(frequency_hz, injection)
    return complex(response[compartment_index])


def transfer_impedance(
    network: PassiveNetwork, source_index: int, target_index: int, frequency_hz: float
) -> complex:
    injection = np.zeros(network.n, dtype=complex)
    injection[source_index] = 1.0
    response = network.solve_frequency(frequency_hz, injection)
    return complex(response[target_index])


def impedance_gain_phase(z_value: complex) -> tuple[float, float]:
    return abs(z_value), float(np.angle(z_value))


def impedance_spectrum(
    network: PassiveNetwork,
    source_index: int,
    target_index: int,
    frequencies_hz: np.ndarray,
) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for frequency_hz in frequencies_hz:
        z_in = local_input_impedance(network, source_index, float(frequency_hz))
        z_transfer = transfer_impedance(network, source_index, target_index, float(frequency_hz))
        rows.append(
            {
                "frequency_hz": float(frequency_hz),
                "Z_in_abs_Mohm": abs(z_in) / 1e6,
                "Z_in_phase_rad": float(np.angle(z_in)),
                "Z_transfer_abs_Mohm": abs(z_transfer) / 1e6,
                "Z_transfer_phase_rad": float(np.angle(z_transfer)),
                "gain_abs": abs(z_transfer / z_in) if z_in != 0 else float("nan"),
                "gain_phase_rad": float(np.angle(z_transfer / z_in)) if z_in != 0 else float("nan"),
            }
        )
    return rows


def dynamic_smi(
    neck_impedance_ohm: complex, dendritic_input_impedance_ohm: complex
) -> complex:
    if dendritic_input_impedance_ohm == 0:
        raise ValueError("dendritic_input_impedance_ohm cannot be zero")
    return neck_impedance_ohm / dendritic_input_impedance_ohm


def fit_sinusoid_response(
    times_s: np.ndarray,
    values: np.ndarray,
    frequency_hz: float,
    fit_start_s: float,
) -> complex:
    mask = times_s >= fit_start_s
    t = times_s[mask]
    y = values[mask]
    cos_col = np.cos(2.0 * np.pi * frequency_hz * t)
    sin_col = np.sin(2.0 * np.pi * frequency_hz * t)
    design = np.column_stack([cos_col, sin_col, np.ones_like(t)])
    coeffs, *_ = np.linalg.lstsq(design, y, rcond=None)
    cos_amp, sin_amp, _offset = coeffs
    return complex(float(cos_amp), float(-sin_amp))


def sinusoidal_impedance_validation(
    network: PassiveNetwork,
    source_index: int,
    target_index: int,
    frequency_hz: float,
    current_amplitude_A: float = 1e-12,
    dt_s: float = 2e-5,
    cycles: int = 12,
) -> dict[str, float]:
    stop_s = cycles / frequency_hz

    def current_fn(t: float) -> np.ndarray:
        injection = np.zeros(network.n)
        injection[source_index] = current_amplitude_A * np.cos(2.0 * np.pi * frequency_hz * t)
        return injection

    times, voltage = network.simulate_linear_current(current_fn, dt_s=dt_s, stop_s=stop_s)
    phasor = fit_sinusoid_response(times, voltage[:, target_index], frequency_hz, fit_start_s=0.5 * stop_s)
    z_time = phasor / current_amplitude_A
    z_freq = transfer_impedance(network, source_index, target_index, frequency_hz)
    phase_error = abs(float(np.angle(z_time / z_freq))) if z_freq != 0 else float("nan")
    amp_error = abs(abs(z_time) - abs(z_freq)) / abs(z_freq) if z_freq != 0 else float("nan")
    return {
        "frequency_hz": frequency_hz,
        "time_abs_Mohm": abs(z_time) / 1e6,
        "freq_abs_Mohm": abs(z_freq) / 1e6,
        "relative_amplitude_error": amp_error,
        "phase_error_rad": phase_error,
    }


def chirp_impedance_validation(
    network: PassiveNetwork,
    source_index: int,
    target_index: int,
    frequencies_hz: list[float],
    current_amplitude_A: float = 1e-12,
    dt_s: float = 5e-5,
    cycles_per_frequency: int = 8,
) -> list[dict[str, float]]:
    """Validate transfer impedance with a logarithmic chirp and FFT ratio.

    The sinusoidal validator above checks steady-state single tones. This
    routine uses one continuous logarithmic sweep, estimates the transfer
    function as FFT(V_target) / FFT(I_source), and compares selected frequency
    bins with the direct frequency-domain solve.
    """
    if not frequencies_hz:
        raise ValueError("frequencies_hz must not be empty")
    if dt_s <= 0 or current_amplitude_A <= 0 or cycles_per_frequency <= 0:
        raise ValueError("dt_s, current_amplitude_A, and cycles_per_frequency must be positive")

    requested = sorted(float(frequency_hz) for frequency_hz in frequencies_hz)
    if requested[0] <= 0:
        raise ValueError("frequencies must be positive")

    sweep_start_hz = max(0.1, 0.25 * requested[0])
    sweep_stop_hz = 1.5 * requested[-1]
    duration_s = max(1.0, 1.5 * cycles_per_frequency / requested[0])
    log_ratio = float(np.log(sweep_stop_hz / sweep_start_hz))

    def phase_at(t: np.ndarray | float) -> np.ndarray | float:
        return (
            2.0
            * np.pi
            * sweep_start_hz
            * duration_s
            / log_ratio
            * (np.exp(log_ratio * np.asarray(t) / duration_s) - 1.0)
        )

    def current_fn(t: float) -> np.ndarray:
        injection = np.zeros(network.n)
        injection[source_index] = current_amplitude_A * np.cos(float(phase_at(t)))
        return injection

    times, voltage = network.simulate_linear_current(current_fn, dt_s=dt_s, stop_s=duration_s)
    current = current_amplitude_A * np.cos(phase_at(times))

    mask = times >= 0.1 * duration_s
    current_segment = current[mask] - float(np.mean(current[mask]))
    voltage_segment = voltage[mask, target_index] - float(np.mean(voltage[mask, target_index]))
    window = np.hanning(len(current_segment))
    input_fft = np.fft.rfft(current_segment * window)
    output_fft = np.fft.rfft(voltage_segment * window)
    fft_frequencies = np.fft.rfftfreq(len(current_segment), dt_s)

    rows: list[dict[str, float]] = []
    for frequency_hz in requested:
        bin_index = int(np.argmin(np.abs(fft_frequencies - frequency_hz)))
        bin_frequency_hz = float(fft_frequencies[bin_index])
        if abs(input_fft[bin_index]) == 0:
            raise ValueError("chirp input has zero FFT magnitude at requested frequency")
        z_time = output_fft[bin_index] / input_fft[bin_index]
        z_freq = transfer_impedance(network, source_index, target_index, bin_frequency_hz)
        phase_error = abs(float(np.angle(z_time / z_freq))) if z_freq != 0 else float("nan")
        amp_error = abs(abs(z_time) - abs(z_freq)) / abs(z_freq) if z_freq != 0 else float("nan")
        rows.append(
            {
                "frequency_hz": frequency_hz,
                "fft_bin_frequency_hz": bin_frequency_hz,
                "time_abs_Mohm": abs(z_time) / 1e6,
                "freq_abs_Mohm": abs(z_freq) / 1e6,
                "relative_amplitude_error": amp_error,
                "phase_error_rad": phase_error,
                "validation_method": "log_chirp_fft",
            }
        )
    return rows
