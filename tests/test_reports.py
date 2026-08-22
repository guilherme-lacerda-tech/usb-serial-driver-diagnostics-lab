import json

from usb_serial_driver_diagnostics_lab.diagnostics import run_simulation
from usb_serial_driver_diagnostics_lab.reports import (
    compare_report_payloads,
    render_html_report,
    reports_to_dict,
    write_html_report,
    write_json_report,
)


def test_json_report_contains_expected_sections(tmp_path) -> None:
    report = run_simulation("timeout")
    path = write_json_report([report], tmp_path / "report.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["report_count"] == 1
    assert payload["devices"][0]["device"]["port"] == "COM9"
    assert payload["devices"][0]["warnings"]


def test_html_report_escapes_and_renders_device() -> None:
    report = run_simulation("healthy")
    html = render_html_report([report])
    assert "<h1>USB Serial Diagnostics Report</h1>" in html
    assert "COM7" in html


def test_html_report_file_is_written(tmp_path) -> None:
    path = write_html_report([run_simulation("communication_failure")], tmp_path / "report.html")
    assert path.exists()
    assert "communication" in path.read_text(encoding="utf-8")


def test_reports_to_dict_includes_overall_status() -> None:
    payload = reports_to_dict([run_simulation("driver_missing")])
    device = payload["devices"][0]
    assert device["overall_status"] == "fail"
    assert device["errors"]


def test_report_generation_surfaces_file_errors(tmp_path) -> None:
    directory = tmp_path / "as-directory"
    directory.mkdir()
    try:
        write_json_report([run_simulation("healthy")], directory)
    except OSError as exc:
        assert exc
    else:
        raise AssertionError("expected writing a report to a directory path to fail")


def test_compare_report_payloads_tracks_failures_and_recovery() -> None:
    previous = {
        "devices": [
            {"device": {"port": "COM1"}, "overall_status": "fail"},
            {"device": {"port": "COM2"}, "overall_status": "pass"},
        ]
    }
    current = {
        "devices": [
            {"device": {"port": "COM1"}, "overall_status": "pass"},
            {"device": {"port": "COM3"}, "overall_status": "fail"},
        ]
    }

    assert compare_report_payloads(previous, current) == {
        "previous_devices": 2,
        "current_devices": 2,
        "new_ports": ["COM3"],
        "missing_ports": ["COM2"],
        "new_failures": ["COM3"],
        "recovered_ports": ["COM1"],
        "unchanged_failures": [],
    }

