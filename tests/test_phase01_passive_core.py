from dataclasses import replace
import math
from pathlib import Path
import unittest

import numpy as np

from spine.config import load_config
from spine.geometry import (
    cylindrical_neck_resistance_ohm,
    nonuniform_neck_resistance_ohm,
)
from spine.impedance import (
    dendrite_soma_time_constants_s,
    dendritic_input_resistance_ohm,
    dendritic_input_resistance_time_domain_ohm,
    dendritic_input_resistance_steady_state_ohm,
    smi,
)
from spine.metrics import compute_voltage_metrics
from spine.passive import (
    assemble_passive_matrix,
    capacitance_matrix,
    parameters_from_config,
    simulate_three_compartment,
    simulate_with_neck_resistance,
)
from spine.synapses import DoubleExponentialSynapse
from spine.units import ms_to_s, nS_to_S


CONFIG = Path("configs/manuscript_faithful/baseline.toml")


def manuscript_parameters():
    return parameters_from_config(load_config(CONFIG))


class Phase01PassiveCoreTests(unittest.TestCase):
    def test_nonuniform_constant_radius_matches_cylinder(self):
        cylinder = cylindrical_neck_resistance_ohm(100.0, 1.0, 0.1)
        nonuniform = nonuniform_neck_resistance_ohm(100.0, 1.0, lambda _x: 0.1)
        self.assertTrue(math.isclose(nonuniform, cylinder, rel_tol=2e-6))

    def test_nonuniform_linear_taper_matches_analytic_integral(self):
        rho = 100.0
        length_um = 1.0
        r0_um = 0.1
        r1_um = 0.2
        slope = (r1_um - r0_um) / length_um
        expected = rho * 1e4 / math.pi * (1.0 / slope) * (1.0 / r0_um - 1.0 / r1_um)
        actual = nonuniform_neck_resistance_ohm(
            rho, length_um, lambda x: r0_um + slope * x, samples=20001
        )
        self.assertTrue(math.isclose(actual, expected, rel_tol=2e-5))

    def test_double_exponential_normalization(self):
        params = manuscript_parameters()
        syn = params.synapse
        self.assertTrue(math.isclose(syn.analytical_peak_conductance_S(), syn.g_max_S))
        error = abs(syn.discrete_peak_error_S(params.dt_s, params.stop_s))
        self.assertLess(error / syn.g_max_S, 1e-4)

    def test_rest_equilibrium_without_synapse(self):
        params = manuscript_parameters()
        silent_synapse = DoubleExponentialSynapse(
            g_max_S=0.0,
            tau_rise_s=params.synapse.tau_rise_s,
            tau_decay_s=params.synapse.tau_decay_s,
            event_time_s=params.synapse.event_time_s,
            reversal_V=params.synapse.reversal_V,
        )
        result = simulate_three_compartment(replace(params, synapse=silent_synapse), 0.75, 0.12)
        self.assertLess(np.max(np.abs(result.voltage_V - params.leak_reversal_V)), 1e-12)

    def test_excitatory_synapse_depolarizes_and_reduces_driving_force(self):
        result = simulate_three_compartment(manuscript_parameters(), 0.75, 0.12)
        metrics = compute_voltage_metrics(result)
        self.assertGreater(metrics.amplitude_head_V, 0.0)
        self.assertGreater(metrics.amplitude_dendrite_V, 0.0)
        event_index = int(np.searchsorted(result.time_s, result.parameters.synapse.event_time_s))
        initial_force = abs(result.head_V[event_index] - result.parameters.synaptic_reversal_V)
        self.assertLess(abs(result.head_V.max() - result.parameters.synaptic_reversal_V), initial_force)
        self.assertGreater(metrics.driving_force_reduction_V, 0.0)
        self.assertLess(metrics.minimum_abs_driving_force_V, metrics.initial_abs_driving_force_V)

    def test_backward_euler_matches_crank_nicolson_cross_check(self):
        params = manuscript_parameters()
        be = simulate_three_compartment(params, 0.75, 0.12, method="backward_euler")
        cn = simulate_three_compartment(params, 0.75, 0.12, method="crank_nicolson")
        self.assertLess(np.max(np.abs(be.voltage_V - cn.voltage_V)), 5e-5)

    def test_time_step_refinement_changes_metrics_slightly(self):
        params = manuscript_parameters()
        coarse = simulate_three_compartment(params, 0.75, 0.12)
        fine = simulate_three_compartment(replace(params, dt_s=params.dt_s / 2.0), 0.75, 0.12)
        coarse_metrics = compute_voltage_metrics(coarse)
        fine_metrics = compute_voltage_metrics(fine)
        self.assertLess(
            abs(coarse_metrics.amplitude_head_V - fine_metrics.amplitude_head_V),
            2e-4,
        )

    def test_input_resistance_uses_spine_omitted_dendrite_soma_load(self):
        params = manuscript_parameters()
        result = dendritic_input_resistance_ohm(params)
        steady, _ = dendritic_input_resistance_steady_state_ohm(params)
        self.assertTrue(math.isclose(result.steady_state_ohm, steady))
        self.assertLess(abs(result.time_domain_ohm - result.steady_state_ohm) / steady, 1e-6)
        gld = params.g_leak_dendrite_S
        gls = params.g_leak_soma_S
        gds = params.g_dendrite_soma_S
        expected = (gls + gds) / ((gld + gds) * (gls + gds) - gds**2)
        self.assertTrue(math.isclose(steady, expected))

    def test_input_resistance_duration_validates_against_time_constants(self):
        params = manuscript_parameters()
        slowest = float(np.max(dendrite_soma_time_constants_s(params)))
        with self.assertRaises(ValueError):
            dendritic_input_resistance_time_domain_ohm(params, duration_s=5.0 * slowest)
        value, _ = dendritic_input_resistance_time_domain_ohm(params, duration_s=10.0 * slowest)
        self.assertGreater(value, 0.0)

    def test_smi_fixed_load_is_scaled_neck_resistance(self):
        params = manuscript_parameters()
        rin = dendritic_input_resistance_ohm(params).steady_state_ohm
        r1 = cylindrical_neck_resistance_ohm(100.0, 0.5, 0.1)
        r2 = cylindrical_neck_resistance_ohm(100.0, 1.0, 0.1)
        self.assertTrue(math.isclose(smi(r2, rin) / smi(r1, rin), r2 / r1))

    def test_backward_euler_residual_current_balance(self):
        params = manuscript_parameters()
        result = simulate_three_compartment(params, 0.75, 0.12)
        index = int(np.searchsorted(result.time_s, params.synapse.event_time_s + ms_to_s(1.0)))
        matrix, source = assemble_passive_matrix(
            params, result.neck_conductance_S, result.g_syn_S[index]
        )
        c_over_dt = capacitance_matrix(params) / params.dt_s
        residual = (
            (c_over_dt + matrix) @ result.voltage_V[index]
            - c_over_dt @ result.voltage_V[index - 1]
            - source
        )
        self.assertLess(np.max(np.abs(residual)), 1e-20)

    def test_large_synaptic_conductance_is_stable(self):
        params = manuscript_parameters()
        large_synapse = replace(params.synapse, g_max_S=nS_to_S(100.0))
        result = simulate_three_compartment(replace(params, synapse=large_synapse), 0.75, 0.12)
        self.assertFalse(np.isnan(result.voltage_V).any())
        self.assertFalse(np.isinf(result.voltage_V).any())
        self.assertLessEqual(float(np.max(result.head_V)), params.synaptic_reversal_V + 1e-9)

    def test_parameter_time_validation_rejects_invalid_programmatic_values(self):
        params = manuscript_parameters()
        with self.assertRaises(ValueError):
            simulate_with_neck_resistance(replace(params, dt_s=0.0), 1e8)
        with self.assertRaises(ValueError):
            simulate_with_neck_resistance(replace(params, stop_s=params.synapse.event_time_s), 1e8)
        with self.assertRaises(ValueError):
            simulate_with_neck_resistance(replace(params, metric_window_s=params.stop_s), 1e8)
