from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class CheckStatus(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    INFO = "info"


@dataclass(frozen=True)
class SerialSettings:
    baudrate: int = 115200
    bytesize: int = 8
    parity: str = "N"
    stopbits: float = 1
    timeout_seconds: float = 1.0
    probe_payload: str = "PING"

    def __post_init__(self) -> None:
        if self.baudrate <= 0 or self.baudrate > 4_000_000:
            raise ValueError("baudrate must be between 1 and 4000000")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")


@dataclass(frozen=True)
class DeviceIdentity:
    port: str
    description: str
    manufacturer: str | None = None
    hwid: str | None = None
    vid: str | None = None
    pid: str | None = None
    serial_number: str | None = None
    location: str | None = None
    pnp_status: str = "unknown"
    source: str = "live"


@dataclass(frozen=True)
class DiagnosticCheck:
    name: str
    status: CheckStatus
    detail: str
    recommendation: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DiagnosticReport:
    device: DeviceIdentity
    settings: SerialSettings
    checks: list[DiagnosticCheck]
    scenario: str | None = None
    generated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def overall_status(self) -> CheckStatus:
        statuses = [check.status for check in self.checks]
        if CheckStatus.FAIL in statuses:
            return CheckStatus.FAIL
        if CheckStatus.WARN in statuses:
            return CheckStatus.WARN
        return CheckStatus.PASS

    @property
    def warnings(self) -> list[str]:
        return [check.detail for check in self.checks if check.status == CheckStatus.WARN]

    @property
    def errors(self) -> list[str]:
        return [check.detail for check in self.checks if check.status == CheckStatus.FAIL]

    @property
    def recommendations(self) -> list[str]:
        return [check.recommendation for check in self.checks if check.recommendation]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["overall_status"] = self.overall_status.value
        payload["warnings"] = self.warnings
        payload["errors"] = self.errors
        payload["recommendations"] = self.recommendations
        for check in payload["checks"]:
            check["status"] = check["status"].value
        return payload

