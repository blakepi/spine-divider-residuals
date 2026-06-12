"""Sparse graph-based passive compartment network."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from spine.compartments import AxialConnection, PassiveCompartment


@dataclass(frozen=True)
class SparseCOOMatrix:
    shape: tuple[int, int]
    rows: tuple[int, ...]
    cols: tuple[int, ...]
    data: tuple[complex, ...]

    def to_dense(self) -> np.ndarray:
        dense = np.zeros(self.shape, dtype=complex)
        for row, col, value in zip(self.rows, self.cols, self.data):
            dense[row, col] += value
        if np.max(np.abs(dense.imag)) == 0:
            return dense.real
        return dense

    def matvec(self, vector: np.ndarray) -> np.ndarray:
        out = np.zeros(self.shape[0], dtype=complex)
        for row, col, value in zip(self.rows, self.cols, self.data):
            out[row] += value * vector[col]
        if np.max(np.abs(out.imag)) == 0:
            return out.real
        return out


class PassiveNetwork:
    """Passive tree/network assembled from compartments and axial edges."""

    def __init__(self) -> None:
        self.compartments: list[PassiveCompartment] = []
        self.connections: list[AxialConnection] = []

    def add_compartment(self, compartment: PassiveCompartment) -> int:
        self.compartments.append(compartment)
        return len(self.compartments) - 1

    def add_connection(self, i: int, j: int, conductance_S: float, label: str = "axial") -> None:
        self._check_index(i)
        self._check_index(j)
        self.connections.append(AxialConnection(i=i, j=j, conductance_S=conductance_S, label=label))

    def copy(self) -> "PassiveNetwork":
        copied = PassiveNetwork()
        copied.compartments = list(self.compartments)
        copied.connections = list(self.connections)
        return copied

    def _check_index(self, index: int) -> None:
        if index < 0 or index >= len(self.compartments):
            raise IndexError(f"compartment index out of range: {index}")

    @property
    def n(self) -> int:
        return len(self.compartments)

    def capacitance_matrix(self) -> np.ndarray:
        return np.diag([comp.capacitance_F for comp in self.compartments])

    def capacitance_vector(self) -> np.ndarray:
        return np.array([comp.capacitance_F for comp in self.compartments], dtype=float)

    def source_vector(self) -> np.ndarray:
        return np.array(
            [comp.leak_conductance_S * comp.leak_reversal_V for comp in self.compartments],
            dtype=float,
        )

    def resting_voltage_vector(self) -> np.ndarray:
        return np.array([comp.leak_reversal_V for comp in self.compartments], dtype=float)

    def assemble_sparse_admittance(
        self, extra_conductance: dict[int, float] | None = None
    ) -> SparseCOOMatrix:
        extra_conductance = extra_conductance or {}
        diag = [comp.leak_conductance_S + extra_conductance.get(i, 0.0) for i, comp in enumerate(self.compartments)]
        rows: list[int] = []
        cols: list[int] = []
        data: list[complex] = []
        for connection in self.connections:
            i = connection.i
            j = connection.j
            g = connection.conductance_S
            diag[i] += g
            diag[j] += g
            rows.extend([i, j])
            cols.extend([j, i])
            data.extend([-g, -g])
        for i, value in enumerate(diag):
            rows.append(i)
            cols.append(i)
            data.append(value)
        return SparseCOOMatrix((self.n, self.n), tuple(rows), tuple(cols), tuple(data))

    def assemble_dense_admittance(self, extra_conductance: dict[int, float] | None = None) -> np.ndarray:
        return self.assemble_sparse_admittance(extra_conductance).to_dense()

    def solve_dc(self, injection_A: np.ndarray) -> np.ndarray:
        return np.linalg.solve(self.assemble_dense_admittance(), injection_A)

    def solve_frequency(self, frequency_hz: float, injection_A: np.ndarray) -> np.ndarray:
        omega = 2.0 * np.pi * frequency_hz
        matrix = self.assemble_dense_admittance().astype(complex)
        matrix = matrix + 1j * omega * self.capacitance_matrix()
        return np.linalg.solve(matrix, injection_A.astype(complex))

    def simulate_linear_current(
        self,
        current_fn: Callable[[float], np.ndarray],
        dt_s: float,
        stop_s: float,
        initial_delta_V: np.ndarray | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        if dt_s <= 0 or stop_s <= 0:
            raise ValueError("dt_s and stop_s must be positive")
        times = np.arange(0.0, stop_s + 0.5 * dt_s, dt_s)
        voltage = np.zeros((len(times), self.n), dtype=float)
        if initial_delta_V is not None:
            voltage[0, :] = initial_delta_V
        c_over_dt = self.capacitance_matrix() / dt_s
        admittance = self.assemble_dense_admittance()
        lhs = c_over_dt + admittance
        for k in range(1, len(times)):
            rhs = c_over_dt @ voltage[k - 1, :] + current_fn(float(times[k]))
            voltage[k, :] = np.linalg.solve(lhs, rhs)
        return times, voltage


def axial_resistance_between_segments_ohm(
    rho_ohm_cm: float,
    length_i_um: float,
    radius_i_um: float,
    length_j_um: float,
    radius_j_um: float,
) -> float:
    if min(rho_ohm_cm, length_i_um, radius_i_um, length_j_um, radius_j_um) <= 0:
        raise ValueError("axial resistance inputs must be positive")
    half_i_cm = 0.5 * length_i_um * 1e-4
    half_j_cm = 0.5 * length_j_um * 1e-4
    radius_i_cm = radius_i_um * 1e-4
    radius_j_cm = radius_j_um * 1e-4
    return rho_ohm_cm * (
        half_i_cm / (np.pi * radius_i_cm**2)
        + half_j_cm / (np.pi * radius_j_cm**2)
    )


def axial_conductance_between_segments_S(
    rho_ohm_cm: float,
    length_i_um: float,
    radius_i_um: float,
    length_j_um: float,
    radius_j_um: float,
) -> float:
    return 1.0 / axial_resistance_between_segments_ohm(
        rho_ohm_cm, length_i_um, radius_i_um, length_j_um, radius_j_um
    )
