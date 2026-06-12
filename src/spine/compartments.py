"""Passive compartment data structures."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PassiveCompartment:
    name: str
    capacitance_F: float
    leak_conductance_S: float
    leak_reversal_V: float = -0.070
    area_um2: float = 0.0
    length_um: float = 0.0
    radius_um: float = 0.0
    x_um: float = 0.0
    y_um: float = 0.0
    z_um: float = 0.0
    branch_order: int = 0
    kind: str = "dendrite"

    def __post_init__(self) -> None:
        if self.capacitance_F <= 0:
            raise ValueError("capacitance_F must be positive")
        if self.leak_conductance_S < 0:
            raise ValueError("leak_conductance_S must be nonnegative")


@dataclass(frozen=True)
class AxialConnection:
    i: int
    j: int
    conductance_S: float
    label: str = "axial"

    def __post_init__(self) -> None:
        if self.i == self.j:
            raise ValueError("axial connection cannot connect a node to itself")
        if self.conductance_S <= 0:
            raise ValueError("conductance_S must be positive")
