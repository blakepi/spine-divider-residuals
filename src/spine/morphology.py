"""Procedural passive morphologies and lightweight SWC parsing."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path

from spine.compartments import PassiveCompartment
from spine.network import PassiveNetwork, axial_conductance_between_segments_S
from spine.units import nS_to_S, pF_to_F


DEFAULT_CM_PF_PER_UM2 = 0.01
DEFAULT_GBAR_NS_PER_UM2 = 3e-6
DEFAULT_E_LEAK_V = -0.070
DEFAULT_RHO_OHM_CM = 100.0


@dataclass(frozen=True)
class MorphologyBuildResult:
    network: PassiveNetwork
    soma_index: int
    terminal_indices: list[int]
    path_lengths_um: dict[int, float]


def cylinder_area_um2(length_um: float, radius_um: float) -> float:
    if length_um <= 0 or radius_um <= 0:
        raise ValueError("length_um and radius_um must be positive")
    return 2.0 * math.pi * radius_um * length_um


def sphere_area_um2(radius_um: float) -> float:
    if radius_um <= 0:
        raise ValueError("radius_um must be positive")
    return 4.0 * math.pi * radius_um**2


def passive_compartment_from_geometry(
    name: str,
    length_um: float,
    radius_um: float,
    kind: str = "dendrite",
    branch_order: int = 0,
    x_um: float = 0.0,
    y_um: float = 0.0,
    z_um: float = 0.0,
    cm_pF_per_um2: float = DEFAULT_CM_PF_PER_UM2,
    gbar_nS_per_um2: float = DEFAULT_GBAR_NS_PER_UM2,
    leak_reversal_V: float = DEFAULT_E_LEAK_V,
) -> PassiveCompartment:
    area = cylinder_area_um2(length_um, radius_um)
    return PassiveCompartment(
        name=name,
        capacitance_F=pF_to_F(cm_pF_per_um2 * area),
        leak_conductance_S=nS_to_S(gbar_nS_per_um2 * area),
        leak_reversal_V=leak_reversal_V,
        area_um2=area,
        length_um=length_um,
        radius_um=radius_um,
        x_um=x_um,
        y_um=y_um,
        z_um=z_um,
        branch_order=branch_order,
        kind=kind,
    )


def lumped_soma(
    name: str = "soma",
    capacitance_pF: float = 220.0,
    leak_nS: float = 7.0,
    radius_um: float = 10.0,
    leak_reversal_V: float = DEFAULT_E_LEAK_V,
) -> PassiveCompartment:
    return PassiveCompartment(
        name=name,
        capacitance_F=pF_to_F(capacitance_pF),
        leak_conductance_S=nS_to_S(leak_nS),
        leak_reversal_V=leak_reversal_V,
        area_um2=sphere_area_um2(radius_um),
        length_um=2.0 * radius_um,
        radius_um=radius_um,
        kind="soma",
    )


def procedural_cable(
    length_um: float,
    radius_um: float,
    nseg: int,
    include_soma: bool = True,
    rho_ohm_cm: float = DEFAULT_RHO_OHM_CM,
) -> MorphologyBuildResult:
    if nseg < 1:
        raise ValueError("nseg must be at least 1")
    network = PassiveNetwork()
    path_lengths: dict[int, float] = {}
    previous = None
    soma_index = -1
    if include_soma:
        soma_index = network.add_compartment(lumped_soma())
        previous = soma_index
        path_lengths[soma_index] = 0.0
    dx = length_um / nseg
    indices: list[int] = []
    for i in range(nseg):
        index = network.add_compartment(
            passive_compartment_from_geometry(
                name=f"dend_{i}",
                length_um=dx,
                radius_um=radius_um,
                x_um=(i + 0.5) * dx,
            )
        )
        path_lengths[index] = (i + 0.5) * dx
        indices.append(index)
        if previous is not None:
            prev_comp = network.compartments[previous]
            conductance = axial_conductance_between_segments_S(
                rho_ohm_cm,
                prev_comp.length_um,
                max(prev_comp.radius_um, radius_um),
                dx,
                radius_um,
            )
            network.add_connection(previous, index, conductance)
        previous = index
    return MorphologyBuildResult(network, soma_index, [indices[-1]], path_lengths)


def procedural_branch_tree(
    trunk_length_um: float = 120.0,
    branch_length_um: float = 80.0,
    radius_um: float = 0.5,
    trunk_segments: int = 6,
    branch_segments: int = 4,
    asymmetric: bool = False,
    rho_ohm_cm: float = DEFAULT_RHO_OHM_CM,
) -> MorphologyBuildResult:
    network = PassiveNetwork()
    path_lengths: dict[int, float] = {}
    soma = network.add_compartment(lumped_soma())
    path_lengths[soma] = 0.0
    previous = soma
    dx = trunk_length_um / trunk_segments
    trunk_indices: list[int] = []
    for i in range(trunk_segments):
        idx = network.add_compartment(
            passive_compartment_from_geometry(f"trunk_{i}", dx, radius_um, x_um=(i + 0.5) * dx)
        )
        path_lengths[idx] = (i + 0.5) * dx
        prev = network.compartments[previous]
        network.add_connection(
            previous,
            idx,
            axial_conductance_between_segments_S(rho_ohm_cm, prev.length_um, max(prev.radius_um, radius_um), dx, radius_um),
        )
        previous = idx
        trunk_indices.append(idx)
    branch_root = trunk_indices[-1]
    terminals: list[int] = []
    for side, sign in [("left", -1.0), ("right", 1.0)]:
        length = branch_length_um * (1.4 if asymmetric and side == "right" else 1.0)
        bdx = length / branch_segments
        previous = branch_root
        for j in range(branch_segments):
            idx = network.add_compartment(
                passive_compartment_from_geometry(
                    f"{side}_{j}",
                    bdx,
                    radius_um * (0.85 if side == "left" else 0.75),
                    branch_order=1,
                    x_um=trunk_length_um + (j + 0.5) * bdx,
                    y_um=sign * (j + 0.5) * bdx,
                )
            )
            prev = network.compartments[previous]
            path_lengths[idx] = path_lengths[previous] + 0.5 * prev.length_um + 0.5 * bdx
            network.add_connection(
                previous,
                idx,
                axial_conductance_between_segments_S(
                    rho_ohm_cm, prev.length_um, prev.radius_um, bdx, network.compartments[idx].radius_um
                ),
            )
            previous = idx
        terminals.append(previous)
    return MorphologyBuildResult(network, soma, terminals, path_lengths)


def parse_swc_text(text: str, rho_ohm_cm: float = DEFAULT_RHO_OHM_CM) -> MorphologyBuildResult:
    rows: dict[int, tuple[int, float, float, float, float, int]] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 7:
            raise ValueError(f"invalid SWC row: {raw}")
        node_id = int(parts[0])
        node_type = int(parts[1])
        x, y, z, radius = map(float, parts[2:6])
        parent = int(parts[6])
        rows[node_id] = (node_type, x, y, z, radius, parent)
    network = PassiveNetwork()
    id_to_index: dict[int, int] = {}
    path_lengths: dict[int, float] = {}
    soma_index = -1
    for node_id, (node_type, x, y, z, radius, parent) in rows.items():
        if parent == -1 or parent not in rows:
            length = max(2.0 * radius, 1.0)
            area = sphere_area_um2(radius)
            comp = PassiveCompartment(
                name=f"swc_{node_id}",
                capacitance_F=pF_to_F(DEFAULT_CM_PF_PER_UM2 * area),
                leak_conductance_S=nS_to_S(DEFAULT_GBAR_NS_PER_UM2 * area),
                area_um2=area,
                length_um=length,
                radius_um=radius,
                x_um=x,
                y_um=y,
                z_um=z,
                kind="soma" if node_type == 1 else "dendrite",
            )
        else:
            _, px, py, pz, _, _ = rows[parent]
            length = math.dist((x, y, z), (px, py, pz))
            comp = passive_compartment_from_geometry(
                f"swc_{node_id}", max(length, 1e-6), radius, x_um=x, y_um=y, z_um=z
            )
        idx = network.add_compartment(comp)
        id_to_index[node_id] = idx
        if parent == -1:
            soma_index = idx
            path_lengths[idx] = 0.0
    for node_id, (_, _x, _y, _z, _radius, parent) in rows.items():
        if parent == -1 or parent not in rows:
            continue
        i = id_to_index[parent]
        j = id_to_index[node_id]
        ci = network.compartments[i]
        cj = network.compartments[j]
        network.add_connection(
            i,
            j,
            axial_conductance_between_segments_S(
                rho_ohm_cm, ci.length_um, ci.radius_um, cj.length_um, cj.radius_um
            ),
        )
        path_lengths[j] = path_lengths.get(i, 0.0) + 0.5 * ci.length_um + 0.5 * cj.length_um
    connected_parents = {parent for *_, parent in rows.values() if parent != -1}
    terminals = [id_to_index[node_id] for node_id in rows if node_id not in connected_parents]
    return MorphologyBuildResult(network, soma_index, terminals, path_lengths)


def parse_swc_file(path: str | Path, rho_ohm_cm: float = DEFAULT_RHO_OHM_CM) -> MorphologyBuildResult:
    return parse_swc_text(Path(path).read_text(encoding="utf-8"), rho_ohm_cm=rho_ohm_cm)
