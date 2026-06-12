from pathlib import Path
import unittest

from spine.config import load_config


class ConfigTests(unittest.TestCase):
    def test_load_manuscript_faithful_config(self):
        path = Path("configs/manuscript_faithful/baseline.toml")
        config = load_config(path)

        self.assertEqual(config.track, "manuscript_faithful")
        self.assertEqual(config.get("reversal", "leak_mV"), -70.0)
        self.assertGreater(
            config.get("synapse", "tau_decay_ms"),
            config.get("synapse", "tau_rise_ms"),
        )


    def test_load_plausibility_revised_config(self):
        path = Path("configs/plausibility_revised/baseline.toml")
        config = load_config(path)

        self.assertEqual(config.track, "plausibility_revised")
