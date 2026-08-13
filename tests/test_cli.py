import json

from usb_serial_driver_diagnostics_lab import cli
from usb_serial_driver_diagnostics_lab.diagnostics import run_simulation


def test_cli_lists_scenarios(capsys) -> None:
    assert cli.main(["list-scenarios"]) == 0
    output = capsys.readouterr().out
    assert "healthy" in output
    assert "driver_missing" in output


def test_cli_simulate_writes_reports(tmp_path, capsys) -> None:
    json_path = tmp_path / "timeout.json"
    html_path = tmp_path / "timeout.html"

    result = cli.main(
        [
            "simulate",
            "--scenario",
            "timeout",
            "--json",
            str(json_path),
            "--html",
            str(html_path),
        ]
    )

    assert result == 0
    assert json_path.exists()
    assert html_path.exists()
    printed = json.loads(capsys.readouterr().out)
    assert printed["summary"] == {"fail": 0, "pass": 0, "warn": 1}


def test_cli_scan_uses_live_scan_handler(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "run_live_scan", lambda settings: [run_simulation("healthy", settings)])

    assert cli.main(["scan", "--baudrate", "57600"]) == 0

    printed = json.loads(capsys.readouterr().out)
    assert printed["devices"][0]["settings"]["baudrate"] == 57600

