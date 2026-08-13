from usb_serial_driver_diagnostics_lab.diagnostics import list_scenarios, run_simulation
from usb_serial_driver_diagnostics_lab.models import CheckStatus, SerialSettings


def test_all_required_scenarios_exist() -> None:
    assert set(list_scenarios()) == {
        "communication_failure",
        "disconnected",
        "driver_missing",
        "healthy",
        "port_busy",
        "timeout",
        "unknown_vid_pid",
    }


def test_healthy_scenario_passes() -> None:
    report = run_simulation("healthy", SerialSettings(baudrate=9600))
    assert report.overall_status == CheckStatus.PASS
    assert report.device.port == "COM7"
    assert report.settings.baudrate == 9600


def test_busy_port_is_classified_as_failure() -> None:
    report = run_simulation("port_busy")
    assert report.overall_status == CheckStatus.FAIL
    assert any("busy" in error.lower() for error in report.errors)
    assert any("Close terminal tools" in item for item in report.recommendations)


def test_unknown_vid_pid_warns_without_failing() -> None:
    report = run_simulation("unknown_vid_pid")
    assert report.overall_status == CheckStatus.WARN
    assert report.device.vid == "FFFF"

