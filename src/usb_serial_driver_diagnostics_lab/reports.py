from __future__ import annotations

import html
import json
from pathlib import Path

from usb_serial_driver_diagnostics_lab.models import DiagnosticReport


def reports_to_dict(reports: list[DiagnosticReport]) -> dict[str, object]:
    return {
        "report_count": len(reports),
        "devices": [report.to_dict() for report in reports],
    }


def write_json_report(reports: list[DiagnosticReport], path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(reports_to_dict(reports), indent=2, sort_keys=True), encoding="utf-8")
    return output


def render_html_report(reports: list[DiagnosticReport]) -> str:
    rows: list[str] = []
    for report in reports:
        checks = "".join(
            "<li>"
            f"<strong>{html.escape(check.name)}</strong>: "
            f"{html.escape(check.status.value)} - {html.escape(check.detail)}"
            "</li>"
            for check in report.checks
        )
        rows.append(
            "<section>"
            f"<h2>{html.escape(report.device.port)} - {html.escape(report.device.description)}</h2>"
            f"<p><strong>Status:</strong> {html.escape(report.overall_status.value)}</p>"
            f"<p><strong>VID/PID:</strong> {html.escape(str(report.device.vid))}/{html.escape(str(report.device.pid))}</p>"
            f"<ul>{checks}</ul>"
            "</section>"
        )
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<title>USB Serial Diagnostics Report</title>"
        "<style>body{font-family:Arial,sans-serif;margin:2rem;line-height:1.45}"
        "section{border:1px solid #ddd;padding:1rem;margin:1rem 0;border-radius:6px}"
        "code{background:#f5f5f5;padding:.1rem .3rem}</style></head><body>"
        "<h1>USB Serial Diagnostics Report</h1>"
        f"{''.join(rows)}"
        "</body></html>"
    )


def write_html_report(reports: list[DiagnosticReport], path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_html_report(reports), encoding="utf-8")
    return output


def load_json_report(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def compare_report_payloads(previous: dict, current: dict) -> dict[str, object]:
    previous_devices = {
        device["device"]["port"]: device
        for device in previous.get("devices", [])
    }
    current_devices = {
        device["device"]["port"]: device
        for device in current.get("devices", [])
    }
    previous_failing = {
        port
        for port, device in previous_devices.items()
        if device.get("overall_status") == "fail"
    }
    current_failing = {
        port
        for port, device in current_devices.items()
        if device.get("overall_status") == "fail"
    }
    return {
        "previous_devices": len(previous_devices),
        "current_devices": len(current_devices),
        "new_ports": sorted(set(current_devices) - set(previous_devices)),
        "missing_ports": sorted(set(previous_devices) - set(current_devices)),
        "new_failures": sorted(current_failing - previous_failing),
        "recovered_ports": sorted(previous_failing - current_failing),
        "unchanged_failures": sorted(previous_failing & current_failing),
    }

