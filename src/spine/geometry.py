"""Manuscript-faithful geometry helpers."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
import math

from spine.units import cylindrical_neck_resistance_ohm, sphere_area_um2


@dataclass(frozen=True)
class NeckModelResult:
    model: str
    length_um: float
    mean_radius_um: float
    effective_resistance_ohm: float
    lumped_cylinder_resistance_ohm: float
    notes: str = ""


def nonuniform_neck_resistance_ohm(
    resistivity_ohm_cm: float,
    length_um: float,
    radius_um: Callable[[float], float] | Sequence[float],
    samples: int = 1001,
) -> float:
    """Numerically integrate rho/(pi*r(x)^2) dx over a nonuniform neck.

    The integration variable is micrometers for the public API; each interval is
    converted to centimeters before accumulating resistance in ohms. A sequence
    is interpreted as radii sampled uniformly from x=0 to x=L.
    """
    if resistivity_ohm_cm <= 0:
        raise ValueError("resistivity_ohm_cm must be positive")
    if length_um <= 0:
        raise ValueError("length_um must be positive")

    if callable(radius_um):
        if samples < 2:
            raise ValueError("samples must be at least 2")
        xs = [length_um * i / (samples - 1) for i in range(samples)]
        radii = [float(radius_um(x)) for x in xs]
    else:
        radii = [float(r) for r in radius_um]
        if len(radii) < 2:
            raise ValueError("radius sequence must contain at least 2 values")
        xs = [length_um * i / (len(radii) - 1) for i in range(len(radii))]

    for radius in radii:
        if radius <= 0:
            raise ValueError("all radius values must be positive")

    total = 0.0
    for i in range(len(radii) - 1):
        dx_cm = (xs[i + 1] - xs[i]) * 1e-4
        f0 = resistivity_ohm_cm / (math.pi * (radii[i] * 1e-4) ** 2)
        f1 = resistivity_ohm_cm / (math.pi * (radii[i + 1] * 1e-4) ** 2)
        total += 0.5 * (f0 + f1) * dx_cm
    return total


def tapered_neck_resistance_ohm(
    resistivity_ohm_cm: float,
    length_um: float,
    radius_start_um: float,
    radius_end_um: float,
    samples: int = 1001,
) -> float:
    if radius_start_um <= 0 or radius_end_um <= 0:
        raise ValueError("taper radii must be positive")
    return nonuniform_neck_resistance_ohm(
        resistivity_ohm_cm,
        length_um,
        lambda x: radius_start_um + (radius_end_um - radius_start_um) * x / length_um,
        samples=samples,
    )


def constricted_neck_resistance_ohm(
    resistivity_ohm_cm: float,
    length_um: float,
    base_radius_um: float,
    constriction_center_um: float,
    constriction_width_um: float,
    constriction_radius_um: float,
    samples: int = 1001,
) -> float:
    if min(base_radius_um, constriction_width_um, constriction_radius_um) <= 0:
        raise ValueError("constriction dimensions must be positive")
    start = constriction_center_um - 0.5 * constriction_width_um
    stop = constriction_center_um + 0.5 * constriction_width_um

    def radius(x: float) -> float:
        if start <= x <= stop:
            return constriction_radius_um
        return base_radius_um

    return nonuniform_neck_resistance_ohm(resistivity_ohm_cm, length_um, radius, samples=samples)


def summarize_neck_model(
    model: str,
    resistivity_ohm_cm: float,
    length_um: float,
    radii_um: Sequence[float],
) -> NeckModelResult:
    if not radii_um:
        raise ValueError("radii_um cannot be empty")
    mean_radius = sum(radii_um) / len(radii_um)
    effective = nonuniform_neck_resistance_ohm(resistivity_ohm_cm, length_um, radii_um)
    lumped = cylindrical_neck_resistance_ohm(resistivity_ohm_cm, length_um, mean_radius)
    return NeckModelResult(
        model=model,
        length_um=length_um,
        mean_radius_um=mean_radius,
        effective_resistance_ohm=effective,
        lumped_cylinder_resistance_ohm=lumped,
        notes="same total length; radius profile summarized by arithmetic mean",
    )


__all__ = [
    "cylindrical_neck_resistance_ohm",
    "constricted_neck_resistance_ohm",
    "nonuniform_neck_resistance_ohm",
    "summarize_neck_model",
    "sphere_area_um2",
    "tapered_neck_resistance_ohm",
]
