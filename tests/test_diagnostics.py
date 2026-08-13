from types import SimpleNamespace
import sys

import pytest

from usb_serial_driver_diagnostics_lab.diagnostics import (
    classify_open_error,
    discover_ports,
    identity_from_pyserial_port,
    run_live_probe,
    run_live_scan,
    run_simulation,
    summarize_reports,
)
from usb_serial_driver_diagnostics_lab.models import CheckStatus, DeviceIdentity


def test_error_classifier_detects_busy_port() -> None:
    status, detail, recommendation = classify_open_error("Access is denied")
    assert status == CheckStatus.FAIL
    assert "busy" in detail.lower()
    assert "Close" in recommendation


def test_error_classifier_detects_timeout() -> None:
    status, detail, _recommendation = classify_open_error("operation timeout")
    assert status == CheckStatus.WARN
    assert "timed out" in detail


def test_identity_from_pyserial_port_parses_vid_pid() -> None:
    port = SimpleNamespace(
        device="COM3",
        description="USB Serial",
        manufacturer="Example",
        hwid="USB VID:PID=1209:0042",
        vid=None,
        pid=None,
        serial_number="SIM",
        location="Port_#0003",
    )
    identity = identity_from_pyserial_port(port)
    assert identity.vid == "1209"
    assert identity.pid == "0042"


def test_summary_counts_report_statuses() -> None:
    summary = summarize_reports(
        [
            run_simulation("healthy"),
            run_simulation("timeout"),
            run_simulation("driver_missing"),
        ]
    )
    assert summary == {"pass": 1, "warn": 1, "fail": 1}


def test_unknown_scenario_raises_clear_error() -> None:
    with pytest.raises(ValueError, match="Unknown scenario"):
        run_simulation("not_real")


def test_discover_ports_returns_list() -> None:
    assert isinstance(discover_ports(), list)


def test_live_scan_reports_empty_inventory(monkeypatch) -> None:
    monkeypatch.setattr("usb_serial_driver_diagnostics_lab.diagnostics.discover_ports", lambda: [])
    reports = run_live_scan()
    assert reports[0].overall_status == CheckStatus.WARN
    assert reports[0].device.port == "none"


class _FakeSerial:
    def __init__(self, *_args, response=b"PONG", **_kwargs) -> None:
        self.response = response

    def __enter__(self):
        return self

    def __exit__(self, *_args) -> None:
        return None

    def write(self, payload: bytes) -> int:
        return len(payload)

    def read(self, _size: int) -> bytes:
        return self.response


def test_live_probe_success(monkeypatch) -> None:
    monkeypatch.setitem(sys.modules, "serial", SimpleNamespace(Serial=_FakeSerial))
    device = DeviceIdentity(port="COM1", description="Synthetic", vid="1209", pid="0001")
    report = run_live_probe(device)
    assert report.overall_status == CheckStatus.PASS


def test_live_probe_timeout_warning(monkeypatch) -> None:
    class TimeoutSerial(_FakeSerial):
        def __init__(self, *_args, **_kwargs) -> None:
            super().__init__(response=b"")

    monkeypatch.setitem(sys.modules, "serial", SimpleNamespace(Serial=TimeoutSerial))
    device = DeviceIdentity(port="COM2", description="Synthetic", vid="1209", pid="0002")
    report = run_live_probe(device)
    assert report.overall_status == CheckStatus.WARN


def test_live_probe_open_error(monkeypatch) -> None:
    class BusySerial:
        def __init__(self, *_args, **_kwargs) -> None:
            raise OSError("Access is denied")

    monkeypatch.setitem(sys.modules, "serial", SimpleNamespace(Serial=BusySerial))
    device = DeviceIdentity(port="COM3", description="Synthetic")
    report = run_live_probe(device)
    assert report.overall_status == CheckStatus.FAIL
    assert any("busy" in error.lower() for error in report.errors)
