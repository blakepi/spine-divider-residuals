"""Explicit unit conversion helpers for SPINE.

Canonical internal units are SI: meters, seconds, volts, amperes, siemens,
farads, and ohms.
"""

from __future__ import annotations

import math


def um_to_m(value: float) -> float:
    return value * 1e-6


def m_to_um(value: float) -> float:
    return value * 1e6


def um_to_cm(value: float) -> float:
    return value * 1e-4


def cm_to_m(value: float) -> float:
    return value * 1e-2


def pF_to_F(value: float) -> float:
    return value * 1e-12


def F_to_pF(value: float) -> float:
    return value * 1e12


def nS_to_S(value: float) -> float:
    return value * 1e-9


def S_to_nS(value: float) -> float:
    return value * 1e9


def pA_to_A(value: float) -> float:
    return value * 1e-12


def A_to_pA(value: float) -> float:
    return value * 1e12


def mV_to_V(value: float) -> float:
    return value * 1e-3


def V_to_mV(value: float) -> float:
    return value * 1e3


def megaohm_to_ohm(value: float) -> float:
    return value * 1e6


def ohm_to_megaohm(value: float) -> float:
    return value / 1e6


def ms_to_s(value: float) -> float:
    return value * 1e-3


def s_to_ms(value: float) -> float:
    return value * 1e3


def ohm_cm_to_ohm_m(value: float) -> float:
    return value * 1e-2


def nS_per_um2_to_S_per_m2(value: float) -> float:
    return value * 1e3


def pF_per_um2_to_F_per_m2(value: float) -> float:
    return value


def sphere_area_um2(radius_um: float) -> float:
    if radius_um <= 0:
        raise ValueError("radius_um must be positive")
    return 4.0 * math.pi * radius_um**2


def cylindrical_neck_resistance_ohm(
    resistivity_ohm_cm: float, length_um: float, radius_um: float
) -> float:
    """Return rho*L/(pi*r^2), converting um geometry to cm."""
    if resistivity_ohm_cm <= 0:
        raise ValueError("resistivity_ohm_cm must be positive")
    if length_um <= 0:
        raise ValueError("length_um must be positive")
    if radius_um <= 0:
        raise ValueError("radius_um must be positive")
    length_cm = um_to_cm(length_um)
    radius_cm = um_to_cm(radius_um)
    return resistivity_ohm_cm * length_cm / (math.pi * radius_cm**2)
