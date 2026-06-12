import math
import unittest

from spine.units import (
    cylindrical_neck_resistance_ohm,
    mV_to_V,
    nS_per_um2_to_S_per_m2,
    nS_to_S,
    ohm_cm_to_ohm_m,
    pA_to_A,
    pF_per_um2_to_F_per_m2,
    pF_to_F,
    sphere_area_um2,
    um_to_cm,
)


class UnitTests(unittest.TestCase):
    def test_basic_unit_conversions(self):
        self.assertEqual(um_to_cm(1.0), 1e-4)
        self.assertEqual(pF_to_F(1.0), 1e-12)
        self.assertEqual(nS_to_S(1.0), 1e-9)
        self.assertEqual(pA_to_A(10.0), 1e-11)
        self.assertEqual(mV_to_V(-70.0), -0.070)
        self.assertEqual(ohm_cm_to_ohm_m(100.0), 1.0)
        self.assertEqual(nS_per_um2_to_S_per_m2(3e-6), 3e-3)
        self.assertEqual(pF_per_um2_to_F_per_m2(0.01), 0.01)


    def test_head_area_and_neck_resistance(self):
        self.assertTrue(math.isclose(sphere_area_um2(0.35), 1.5393804002589986))
        resistance = cylindrical_neck_resistance_ohm(100.0, 1.0, 0.1)
        self.assertTrue(math.isclose(resistance / 1e6, 31.830988618379067))
