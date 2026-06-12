from pathlib import Path
import csv
import unittest

import numpy as np

from spine.active import SynapsePlacement, peak_depolarization_metrics, simulate_active_network
from spine.channels import default_active_channels, make_channel
from spine.config import load_config
from spine.morphology import procedural_cable
from spine.phase03 import add_lumped_spine
from spine.synapses import magnesium_block, make_ampa_nmda_synapse
from spine.units import nS_to_S


RESULTS = Path("results/phase04")
FIGURES = Path("figures/phase04")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class Phase04ActiveNonlinearTests(unittest.TestCase):
    def test_active_config_is_separate_from_manuscript_faithful(self):
        manuscript = load_config("configs/manuscript_faithful/baseline.toml")
        active = load_config("configs/active_extension/baseline.toml")
        self.assertEqual(manuscript.track, "manuscript_faithful")
        self.assertEqual(active.track, "active_extension")
        self.assertNotIn("active_channels", manuscript.data)
        self.assertIn("active_channels", active.data)

    def test_nmda_magnesium_block_and_iv_behavior(self):
        values = [magnesium_block(v) for v in np.linspace(-0.080, 0.040, 7)]
        self.assertTrue(all(b > a for a, b in zip(values, values[1:])))
        syn = make_ampa_nmda_synapse(
            [0.020],
            ampa_g_max_S=nS_to_S(1.4),
            nmda_g_max_S=nS_to_S(0.7),
        )
        t = 0.030
        self.assertGreater(abs(syn.current_A(t, -0.020)), abs(syn.current_A(t, -0.080)))
        self.assertAlmostEqual(syn.current_A(t, 0.0), 0.0, places=18)

    def test_active_channel_gate_bounds_and_current_signs(self):
        channels = default_active_channels("full_restrained")
        for channel in channels:
            gates = channel.initialize(-0.070)
            self.assertTrue(all(0.0 <= value <= 1.0 for value in gates.values()))
            updated = channel.update_gates(gates, -0.050, 1e-5)
            self.assertTrue(all(0.0 <= value <= 1.0 for value in updated.values()))
        self.assertLess(make_channel("na", 1.0).current_A(-0.070, make_channel("na", 1.0).initialize(-0.070)), 0.0)
        self.assertGreater(make_channel("kdr", 1.0).current_A(-0.050, make_channel("kdr", 1.0).initialize(-0.050)), 0.0)
        self.assertLess(make_channel("hcn", 1.0).current_A(-0.070, make_channel("hcn", 1.0).initialize(-0.070)), 0.0)

    def test_active_solver_keeps_gates_bounded_for_small_synapse(self):
        build = procedural_cable(80.0, 0.5, 4)
        parent = build.terminal_indices[0]
        network, head = add_lumped_spine(build.network, parent, 200e6)
        syn = make_ampa_nmda_synapse([0.010], ampa_g_max_S=nS_to_S(0.2), nmda_g_max_S=0.0)
        result = simulate_active_network(
            network,
            [],
            [SynapsePlacement(head, syn)],
            dt_s=1e-5,
            stop_s=0.025,
        )
        metrics = peak_depolarization_metrics(result, head, {"d": parent, "s": build.soma_index}, 0.010, 0.010)
        self.assertTrue(result.finite)
        self.assertGreater(metrics["A_h_mV"], 0.0)
        self.assertLess(metrics["max_voltage_mV"], 150.0)

    def test_phase04_outputs_and_validation_exist(self):
        required = [
            RESULTS / "active_validation.csv",
            RESULTS / "active_smi_challenge_suite.csv",
            RESULTS / "active_predictor_comparison.csv",
            RESULTS / "active_protocol_library.csv",
            RESULTS / "active_impedance_operating_point.csv",
            RESULTS / "active_falsification_summary.csv",
            RESULTS / "phase04_summary.csv",
            FIGURES / "active_SMI_vs_Gamma_hd.svg",
            FIGURES / "active_protocol_strength_sweep.svg",
            FIGURES / "active_impedance_full_restrained.svg",
        ]
        for path in required:
            self.assertTrue(path.exists(), f"missing {path}")
            self.assertGreater(path.stat().st_size, 0)
        validation_rows = read_rows(RESULTS / "active_validation.csv")
        self.assertTrue(all(row["passed"] == "True" for row in validation_rows))
        protocol_rows = read_rows(RESULTS / "active_protocol_library.csv")
        bap_rows = [row for row in protocol_rows if row["protocol_family"] == "back_propagating_action_potential"]
        self.assertEqual(len(bap_rows), 1)
        self.assertEqual(bap_rows[0]["soma_crossed_0mV"], "True")


if __name__ == "__main__":
    unittest.main()
