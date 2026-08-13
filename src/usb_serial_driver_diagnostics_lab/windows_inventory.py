from __future__ import annotations

import json
import platform
import subprocess
from typing import Any


def parse_vid_pid(hwid: str | None) -> tuple[str | None, str | None]:
    if not hwid:
        return None, None
    upper = hwid.upper()
    marker = "VID_"
    alt_marker = "VID:PID="
    if alt_marker in upper:
        pair = upper.split(alt_marker, 1)[1].split()[0]
        if ":" in pair:
            vid, pid = pair.split(":", 1)
            return vid[:4], pid[:4]
    if marker not in upper or "PID_" not in upper:
        return None, None
    vid = upper.split("VID_", 1)[1][:4]
    pid = upper.split("PID_", 1)[1][:4]
    return vid, pid


def parse_cim_devices(raw_json: str) -> list[dict[str, Any]]:
    if not raw_json.strip():
        return []
    payload = json.loads(raw_json)
    rows = payload if isinstance(payload, list) else [payload]
    devices: list[dict[str, Any]] = []
    for row in rows:
        device_id = row.get("PNPDeviceID") or row.get("DeviceID") or ""
        vid, pid = parse_vid_pid(device_id)
        devices.append(
            {
                "name": row.get("Name"),
                "manufacturer": row.get("Manufacturer"),
                "pnp_class": row.get("PNPClass"),
                "status": row.get("Status") or "unknown",
                "device_id": device_id,
                "vid": vid,
                "pid": pid,
            }
        )
    return devices


def collect_windows_pnp_devices(timeout_seconds: float = 3.0) -> list[dict[str, Any]]:
    if platform.system() != "Windows":
        return []
    script = (
        "Get-CimInstance Win32_PnPEntity | "
        "Where-Object { $_.Name -match 'COM|USB|Serial' -or $_.PNPClass -eq 'Ports' } | "
        "Select-Object Name,Manufacturer,PNPClass,Status,PNPDeviceID | "
        "ConvertTo-Json -Depth 3"
    )
    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if completed.returncode != 0:
        return []
    return parse_cim_devices(completed.stdout)

