from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from usb_serial_driver_diagnostics_lab.models import (
    CheckStatus,
    DeviceIdentity,
    DiagnosticCheck,
    DiagnosticReport,
    SerialSettings,
)
from usb_serial_driver_diagnostics_lab.simulation import (
    SimulationScenario,
    get_scenario,
    scenario_names,
)
from usb_serial_driver_diagnostics_lab.windows_inventory import parse_vid_pid


def list_scenarios() -> list[str]:
    return scenario_names()


def _check(name: str, status: CheckStatus, detail: str, recommendation: str | None = None, **evidence: Any) -> DiagnosticCheck:
    return DiagnosticCheck(
        name=name,
        status=status,
        detail=detail,
        recommendation=recommendation,
        evidence=evidence,
    )


def build_scenario_checks(scenario: SimulationScenario, settings: SerialSettings) -> list[DiagnosticCheck]:
    checks: list[DiagnosticCheck] = []
    identity = scenario.identity

    if scenario.pnp_ok:
        checks.append(_check("pnp_status", CheckStatus.PASS, "Device is visible in the OS inventory.", pnp_status=identity.pnp_status))
    elif scenario.disconnected:
        checks.append(
            _check(
                "pnp_status",
                CheckStatus.FAIL,
                "Device was expected but is currently disconnected or missing.",
                "Reconnect the USB device, use a known-good cable and refresh Device Manager.",
                pnp_status=identity.pnp_status,
            )
        )
    else:
        checks.append(
            _check(
                "pnp_status",
                CheckStatus.FAIL,
                "Device is present but Windows reports a non-OK PnP status.",
                "Inspect Device Manager and reinstall the vendor driver if needed.",
                pnp_status=identity.pnp_status,
            )
        )

    if scenario.driver_ok:
        checks.append(_check("driver", CheckStatus.PASS, "Driver metadata is sufficient for a controlled serial probe."))
    else:
        checks.append(
            _check(
                "driver",
                CheckStatus.FAIL,
                "Driver appears missing or incomplete for this USB serial device.",
                "Install the public vendor driver and verify VID/PID mapping before opening the port.",
            )
        )

    if scenario.unknown_vid_pid:
        checks.append(
            _check(
                "identity",
                CheckStatus.WARN,
                "VID/PID pair is unknown in the diagnostic inventory.",
                "Confirm the adapter model from trusted public vendor documentation.",
                vid=identity.vid,
                pid=identity.pid,
            )
        )
    else:
        checks.append(_check("identity", CheckStatus.PASS, "VID/PID and description are available.", vid=identity.vid, pid=identity.pid))

    if scenario.can_open:
        checks.append(_check("open_port", CheckStatus.PASS, f"Port opened with baudrate {settings.baudrate}.", timeout=settings.timeout_seconds))
    elif scenario.busy:
        checks.append(
            _check(
                "open_port",
                CheckStatus.FAIL,
                "Port is busy or locked by another process.",
                "Close terminal tools, IDE monitors, vendor utilities and background services using the COM port.",
            )
        )
    else:
        checks.append(
            _check(
                "open_port",
                CheckStatus.FAIL,
                "Port could not be opened safely.",
                "Validate cable, driver state, permissions and whether the device was disconnected during the probe.",
            )
        )

    if scenario.communication_ok:
        checks.append(_check("communication", CheckStatus.PASS, "Probe payload completed successfully.", payload=settings.probe_payload))
    elif scenario.timeout:
        checks.append(
            _check(
                "communication",
                CheckStatus.WARN,
                "Probe timed out without a response.",
                "Check baudrate, parity, firmware prompt state and whether the device expects a different command.",
                timeout=settings.timeout_seconds,
            )
        )
    elif scenario.can_open:
        checks.append(
            _check(
                "communication",
                CheckStatus.FAIL,
                "Port opened, but the device did not produce a valid response.",
                "Capture raw bytes, verify serial settings and confirm protocol expectations with public documentation.",
            )
        )

    return checks


def run_simulation(name: str, settings: SerialSettings | None = None) -> DiagnosticReport:
    effective_settings = settings or SerialSettings()
    scenario = get_scenario(name)
    return DiagnosticReport(
        device=scenario.identity,
        settings=effective_settings,
        checks=build_scenario_checks(scenario, effective_settings),
        scenario=scenario.name,
    )


def identity_from_pyserial_port(port_info: Any) -> DeviceIdentity:
    vid = f"{port_info.vid:04X}" if getattr(port_info, "vid", None) is not None else None
    pid = f"{port_info.pid:04X}" if getattr(port_info, "pid", None) is not None else None
    if not vid or not pid:
        parsed_vid, parsed_pid = parse_vid_pid(getattr(port_info, "hwid", None))
        vid = vid or parsed_vid
        pid = pid or parsed_pid
    return DeviceIdentity(
        port=str(getattr(port_info, "device", "unknown")),
        description=str(getattr(port_info, "description", "USB serial device")),
        manufacturer=getattr(port_info, "manufacturer", None),
        hwid=getattr(port_info, "hwid", None),
        vid=vid,
        pid=pid,
        serial_number=getattr(port_info, "serial_number", None),
        location=getattr(port_info, "location", None),
        pnp_status="unknown",
        source="live",
    )


def discover_ports() -> list[DeviceIdentity]:
    try:
        from serial.tools import list_ports
    except ImportError:
        return []
    return [identity_from_pyserial_port(port) for port in list_ports.comports()]


def classify_open_error(message: str) -> tuple[CheckStatus, str, str]:
    normalized = message.lower()
    if "access is denied" in normalized or "permission" in normalized or "busy" in normalized:
        return (
            CheckStatus.FAIL,
            "Port is busy or access was denied by the OS.",
            "Close other serial monitors or background tools and retry.",
        )
    if "cannot find" in normalized or "no such file" in normalized or "not found" in normalized:
        return (
            CheckStatus.FAIL,
            "Device disappeared or the COM port no longer exists.",
            "Reconnect the device and refresh the port inventory.",
        )
    if "timeout" in normalized:
        return (
            CheckStatus.WARN,
            "The open or communication probe timed out.",
            "Check serial settings and whether firmware is waiting for a different command.",
        )
    return (
        CheckStatus.FAIL,
        "The OS rejected the controlled serial probe.",
        "Inspect driver state, cable quality and adapter compatibility.",
    )


def run_live_probe(device: DeviceIdentity, settings: SerialSettings | None = None) -> DiagnosticReport:
    effective_settings = settings or SerialSettings()
    checks = [
        _check("inventory", CheckStatus.PASS, "Port discovered by pyserial.", vid=device.vid, pid=device.pid),
    ]
    if not device.vid or not device.pid:
        checks.append(
            _check(
                "identity",
                CheckStatus.WARN,
                "VID/PID could not be collected from the port metadata.",
                "Cross-check Device Manager details before assuming the adapter model.",
            )
        )
    else:
        checks.append(_check("identity", CheckStatus.PASS, "VID/PID are available.", vid=device.vid, pid=device.pid))

    try:
        import serial

        with serial.Serial(
            device.port,
            baudrate=effective_settings.baudrate,
            bytesize=effective_settings.bytesize,
            parity=effective_settings.parity,
            stopbits=effective_settings.stopbits,
            timeout=effective_settings.timeout_seconds,
            write_timeout=effective_settings.timeout_seconds,
        ) as handle:
            checks.append(_check("open_port", CheckStatus.PASS, "Port opened successfully."))
            handle.write(effective_settings.probe_payload.encode("ascii", errors="ignore"))
            response = handle.read(16)
            if response:
                checks.append(_check("communication", CheckStatus.PASS, "Device returned bytes during the probe.", bytes_read=len(response)))
            else:
                checks.append(
                    _check(
                        "communication",
                        CheckStatus.WARN,
                        "No bytes were returned before timeout.",
                        "Validate baudrate, parity and device prompt state before deeper protocol troubleshooting.",
                    )
                )
    except Exception as exc:  # noqa: BLE001 - diagnostics must classify OS/library failures.
        status, detail, recommendation = classify_open_error(str(exc))
        checks.append(_check("open_port", status, detail, recommendation, exception=exc.__class__.__name__))

    return DiagnosticReport(device=device, settings=effective_settings, checks=checks)


def run_live_scan(settings: SerialSettings | None = None) -> list[DiagnosticReport]:
    devices = discover_ports()
    if not devices:
        placeholder = DeviceIdentity(
            port="none",
            description="No serial ports discovered",
            pnp_status="not_found",
            source="live",
        )
        return [
            DiagnosticReport(
                device=placeholder,
                settings=settings or SerialSettings(),
                checks=[
                    _check(
                        "inventory",
                        CheckStatus.WARN,
                        "No serial ports were discovered by pyserial.",
                        "Connect a USB serial device and confirm Windows driver installation.",
                    )
                ],
            )
        ]
    return [run_live_probe(device, settings) for device in devices]


def summarize_reports(reports: Iterable[DiagnosticReport]) -> dict[str, int]:
    summary = {"pass": 0, "warn": 0, "fail": 0}
    for report in reports:
        summary[report.overall_status.value] += 1
    return summary

