from types import SimpleNamespace

from usb_serial_driver_diagnostics_lab import windows_inventory
from usb_serial_driver_diagnostics_lab.windows_inventory import (
    collect_windows_pnp_devices,
    parse_cim_devices,
    parse_vid_pid,
)


def test_parse_vid_pid_accepts_windows_device_id() -> None:
    assert parse_vid_pid("USB\\VID_1209&PID_00AF\\SIM") == ("1209", "00AF")


def test_parse_vid_pid_accepts_pyserial_hwid() -> None:
    assert parse_vid_pid("USB VID:PID=1209:0001 SER=SIM") == ("1209", "0001")


def test_parse_cim_single_device() -> None:
    payload = '{"Name":"USB Serial Port (COM7)","Manufacturer":"Example","PNPClass":"Ports","Status":"OK","PNPDeviceID":"USB\\\\VID_1209&PID_0001\\\\SIM"}'
    devices = parse_cim_devices(payload)
    assert devices == [
        {
            "name": "USB Serial Port (COM7)",
            "manufacturer": "Example",
            "pnp_class": "Ports",
            "status": "OK",
            "device_id": "USB\\VID_1209&PID_0001\\SIM",
            "vid": "1209",
            "pid": "0001",
        }
    ]


def test_parse_cim_empty_payload() -> None:
    assert parse_cim_devices("") == []


def test_collect_windows_pnp_skips_non_windows(monkeypatch) -> None:
    monkeypatch.setattr(windows_inventory.platform, "system", lambda: "Linux")
    assert collect_windows_pnp_devices() == []


def test_collect_windows_pnp_parses_powershell_output(monkeypatch) -> None:
    monkeypatch.setattr(windows_inventory.platform, "system", lambda: "Windows")
    monkeypatch.setattr(
        windows_inventory.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0,
            stdout='[{"Name":"USB Serial Port (COM8)","Manufacturer":"Example","PNPClass":"Ports","Status":"OK","PNPDeviceID":"USB\\\\VID_1209&PID_0008\\\\SIM"}]',
        ),
    )
    devices = collect_windows_pnp_devices()
    assert devices[0]["vid"] == "1209"
    assert devices[0]["pid"] == "0008"


def test_collect_windows_pnp_handles_command_failure(monkeypatch) -> None:
    monkeypatch.setattr(windows_inventory.platform, "system", lambda: "Windows")
    monkeypatch.setattr(
        windows_inventory.subprocess,
        "run",
        lambda *_args, **_kwargs: SimpleNamespace(returncode=1, stdout=""),
    )
    assert collect_windows_pnp_devices() == []
