from __future__ import annotations

from dataclasses import dataclass

from usb_serial_driver_diagnostics_lab.models import DeviceIdentity


@dataclass(frozen=True)
class SimulationScenario:
    name: str
    identity: DeviceIdentity
    pnp_ok: bool
    driver_ok: bool
    can_open: bool
    communication_ok: bool
    disconnected: bool = False
    unknown_vid_pid: bool = False
    timeout: bool = False
    busy: bool = False


SCENARIOS: dict[str, SimulationScenario] = {
    "healthy": SimulationScenario(
        name="healthy",
        identity=DeviceIdentity(
            port="COM7",
            description="Synthetic USB Serial Adapter",
            manufacturer="Example Devices",
            hwid="USB VID:PID=1209:0001",
            vid="1209",
            pid="0001",
            serial_number="SIM-USB-0001",
            location="Port_#0007.Hub_#0001",
            pnp_status="OK",
            source="simulation",
        ),
        pnp_ok=True,
        driver_ok=True,
        can_open=True,
        communication_ok=True,
    ),
    "driver_missing": SimulationScenario(
        name="driver_missing",
        identity=DeviceIdentity(
            port="COM12",
            description="Synthetic USB UART Bridge",
            manufacturer=None,
            hwid="USB VID:PID=1209:00AA",
            vid="1209",
            pid="00AA",
            pnp_status="Error",
            source="simulation",
        ),
        pnp_ok=False,
        driver_ok=False,
        can_open=False,
        communication_ok=False,
    ),
    "port_busy": SimulationScenario(
        name="port_busy",
        identity=DeviceIdentity(
            port="COM4",
            description="Synthetic Diagnostic Port",
            manufacturer="Example Devices",
            hwid="USB VID:PID=1209:0002",
            vid="1209",
            pid="0002",
            pnp_status="OK",
            source="simulation",
        ),
        pnp_ok=True,
        driver_ok=True,
        can_open=False,
        communication_ok=False,
        busy=True,
    ),
    "timeout": SimulationScenario(
        name="timeout",
        identity=DeviceIdentity(
            port="COM9",
            description="Synthetic Slow Device",
            manufacturer="Example Devices",
            hwid="USB VID:PID=1209:0003",
            vid="1209",
            pid="0003",
            pnp_status="OK",
            source="simulation",
        ),
        pnp_ok=True,
        driver_ok=True,
        can_open=True,
        communication_ok=False,
        timeout=True,
    ),
    "disconnected": SimulationScenario(
        name="disconnected",
        identity=DeviceIdentity(
            port="COM15",
            description="Previously Seen USB Serial Adapter",
            manufacturer="Example Devices",
            hwid="USB VID:PID=1209:0004",
            vid="1209",
            pid="0004",
            pnp_status="Missing",
            source="simulation",
        ),
        pnp_ok=False,
        driver_ok=True,
        can_open=False,
        communication_ok=False,
        disconnected=True,
    ),
    "unknown_vid_pid": SimulationScenario(
        name="unknown_vid_pid",
        identity=DeviceIdentity(
            port="COM18",
            description="USB Serial Device",
            manufacturer=None,
            hwid="USB VID:PID=FFFF:FFFF",
            vid="FFFF",
            pid="FFFF",
            pnp_status="OK",
            source="simulation",
        ),
        pnp_ok=True,
        driver_ok=True,
        can_open=True,
        communication_ok=True,
        unknown_vid_pid=True,
    ),
    "communication_failure": SimulationScenario(
        name="communication_failure",
        identity=DeviceIdentity(
            port="COM21",
            description="Synthetic USB Modem Control Port",
            manufacturer="Example Devices",
            hwid="USB VID:PID=1209:0005",
            vid="1209",
            pid="0005",
            pnp_status="OK",
            source="simulation",
        ),
        pnp_ok=True,
        driver_ok=True,
        can_open=True,
        communication_ok=False,
    ),
}


def get_scenario(name: str) -> SimulationScenario:
    try:
        return SCENARIOS[name]
    except KeyError as exc:
        valid = ", ".join(sorted(SCENARIOS))
        raise ValueError(f"Unknown scenario '{name}'. Valid scenarios: {valid}") from exc


def scenario_names() -> list[str]:
    return sorted(SCENARIOS)

