"""SPINE command line entry point."""

from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path

from spine.config import load_config
from spine.impedance import dendritic_input_resistance_ohm, smi
from spine.io import export_voltage_csv
from spine.metrics import compute_voltage_metrics
from spine.passive import parameters_from_config, simulate_three_compartment
from spine.plotting import plot_voltage_trace
from spine.units import ohm_to_megaohm, V_to_mV


def main() -> int:
    parser = argparse.ArgumentParser(description="SPINE manuscript-faithful passive core")
    subparsers = parser.add_subparsers(dest="command")

    load_parser = subparsers.add_parser("load-config", help="Load and report a config track")
    load_parser.add_argument("config", help="Path to a TOML configuration")

    smoke_parser = subparsers.add_parser("smoke", help="Run a small Phase 01 passive simulation")
    smoke_parser.add_argument("config", help="Path to a manuscript_faithful TOML configuration")
    smoke_parser.add_argument("--neck-length-um", type=float, default=0.75)
    smoke_parser.add_argument("--neck-radius-um", type=float, default=0.12)
    smoke_parser.add_argument("--output-csv", default="results/phase01_smoke_trace.csv")
    smoke_parser.add_argument("--output-plot", default=None)

    args = parser.parse_args()
    if args.command == "load-config":
        config = load_config(args.config)
        print(f"Loaded SPINE config track: {config.track}")
    elif args.command == "smoke":
        config = load_config(args.config)
        parameters = parameters_from_config(config)
        result = simulate_three_compartment(
            parameters,
            neck_length_um=args.neck_length_um,
            neck_radius_um=args.neck_radius_um,
        )
        metrics = compute_voltage_metrics(result)
        rin = dendritic_input_resistance_ohm(parameters)
        output = export_voltage_csv(result, Path(args.output_csv))
        print(f"track={config.track}")
        print(f"neck_resistance_Mohm={ohm_to_megaohm(result.neck_resistance_ohm):.6g}")
        print(f"R_in_d_Mohm={ohm_to_megaohm(rin.steady_state_ohm):.6g}")
        print(f"SMI={smi(result.neck_resistance_ohm, rin.steady_state_ohm):.6g}")
        print(f"A_h_mV={V_to_mV(metrics.amplitude_head_V):.6g}")
        print(f"Gamma_h_to_d={metrics.gamma_head_to_dendrite:.6g}")
        print(f"output_csv={output}")
        if args.output_plot:
            plot_path = plot_voltage_trace(result, Path(args.output_plot))
            print(f"output_plot={plot_path}")
        _ = asdict(metrics)
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
