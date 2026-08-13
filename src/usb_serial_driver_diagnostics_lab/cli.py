from __future__ import annotations

import argparse
import json
from pathlib import Path

from usb_serial_driver_diagnostics_lab.diagnostics import (
    list_scenarios,
    run_live_scan,
    run_simulation,
    summarize_reports,
)
from usb_serial_driver_diagnostics_lab.models import SerialSettings
from usb_serial_driver_diagnostics_lab.reports import reports_to_dict, write_html_report, write_json_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="usb-serial-diagnostics",
        description="Diagnose USB serial ports with live probes or synthetic simulation scenarios.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-scenarios", help="List simulation scenarios.")
    list_parser.set_defaults(func=handle_list_scenarios)

    simulate = subparsers.add_parser("simulate", help="Run a synthetic hardware-free diagnostic scenario.")
    simulate.add_argument("--scenario", choices=list_scenarios(), default="healthy")
    add_common_probe_args(simulate)
    simulate.set_defaults(func=handle_simulate)

    scan = subparsers.add_parser("scan", help="Discover and probe local serial ports.")
    add_common_probe_args(scan)
    scan.set_defaults(func=handle_scan)
    return parser


def add_common_probe_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--baudrate", type=int, default=115200)
    parser.add_argument("--timeout", type=float, default=1.0, dest="timeout_seconds")
    parser.add_argument("--payload", default="PING", dest="probe_payload")
    parser.add_argument("--json", type=Path, dest="json_path")
    parser.add_argument("--html", type=Path, dest="html_path")


def settings_from_args(args: argparse.Namespace) -> SerialSettings:
    return SerialSettings(
        baudrate=args.baudrate,
        timeout_seconds=args.timeout_seconds,
        probe_payload=args.probe_payload,
    )


def persist_outputs(reports, args: argparse.Namespace) -> None:
    if args.json_path:
        write_json_report(reports, args.json_path)
    if args.html_path:
        write_html_report(reports, args.html_path)


def print_summary(reports) -> None:
    payload = reports_to_dict(reports)
    payload["summary"] = summarize_reports(reports)
    print(json.dumps(payload, indent=2, sort_keys=True))


def handle_list_scenarios(_args: argparse.Namespace) -> int:
    for scenario in list_scenarios():
        print(scenario)
    return 0


def handle_simulate(args: argparse.Namespace) -> int:
    reports = [run_simulation(args.scenario, settings_from_args(args))]
    persist_outputs(reports, args)
    print_summary(reports)
    return 0


def handle_scan(args: argparse.Namespace) -> int:
    reports = run_live_scan(settings_from_args(args))
    persist_outputs(reports, args)
    print_summary(reports)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

