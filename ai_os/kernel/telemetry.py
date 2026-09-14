"""
Observability and audit telemetry logging subsystem for AI-OS.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class AuditEvent:
    event_type: str
    pid: Optional[int]
    details: Dict[str, Any]
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class TelemetrySubsystem:
    """
    Structured telemetry logger capturing syscalls, security violations, and kernel events.
    """

    def __init__(self) -> None:
        self._events: List[AuditEvent] = []

    def log_event(
        self, event_type: str, pid: Optional[int] = None, details: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        event = AuditEvent(
            event_type=event_type,
            pid=pid,
            details=details or {},
        )
        self._events.append(event)
        return event

    def get_events(
        self, event_type: Optional[str] = None, pid: Optional[int] = None
    ) -> List[AuditEvent]:
        filtered = self._events
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        if pid is not None:
            filtered = [e for e in filtered if e.pid == pid]
        return list(filtered)

    def clear(self) -> None:
        self._events.clear()
