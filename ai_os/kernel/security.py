"""
Capability-based access control and security manager for AI-OS.
"""

from typing import Dict, List, Optional, Set
from ai_os.kernel.types import Capability, CapabilityType, ResourceLimits


class SecurityManager:
    """
    Enforces Capability-Based Access Control (CBAC) and resource quotas.
    """

    def __init__(self) -> None:
        # Maps PID -> Set of assigned Capabilities
        self._capabilities: Dict[int, Set[Capability]] = {}
        # Maps PID -> ResourceLimits
        self._resource_limits: Dict[int, ResourceLimits] = {}
        # Track current resource usage: PID -> dict
        self._resource_usage: Dict[int, Dict[str, int]] = {}

    def register_process(
        self,
        pid: int,
        capabilities: Optional[List[Capability]] = None,
        limits: Optional[ResourceLimits] = None,
    ) -> None:
        """Register security policies and capabilities for a process."""
        self._capabilities[pid] = set(capabilities) if capabilities else set()
        self._resource_limits[pid] = limits if limits else ResourceLimits()
        self._resource_usage[pid] = {
            "memory_bytes": 0,
            "open_files": 0,
            "ipc_channels": 0,
            "cpu_ticks": 0,
        }

    def unregister_process(self, pid: int) -> None:
        """Clean up process capabilities and security tracking."""
        self._capabilities.pop(pid, None)
        self._resource_limits.pop(pid, None)
        self._resource_usage.pop(pid, None)

    def grant_capability(self, pid: int, capability: Capability) -> None:
        """Grant a new capability to a process."""
        if pid not in self._capabilities:
            self._capabilities[pid] = set()
        self._capabilities[pid].add(capability)

    def revoke_capability(self, pid: int, capability: Capability) -> None:
        """Revoke a capability from a process."""
        if pid in self._capabilities:
            self._capabilities[pid].discard(capability)

    def check_capability(
        self, pid: int, cap_type: CapabilityType, target_resource: str = "*"
    ) -> bool:
        """
        Verify if process PID holds a capability allowing cap_type on target_resource.
        """
        caps = self._capabilities.get(pid, set())
        for cap in caps:
            if cap.allows(cap_type, target_resource):
                return True
        return False

    def check_resource_limit(self, pid: int, resource_key: str, requested_amount: int) -> bool:
        """Check whether allocating requested_amount will exceed resource limits."""
        limits = self._resource_limits.get(pid)
        usage = self._resource_usage.get(pid)
        if not limits or not usage:
            return False

        current = usage.get(resource_key, 0)
        max_allowed = getattr(limits, f"max_{resource_key}", None)
        if max_allowed is None:
            return True

        return (current + requested_amount) <= max_allowed

    def update_resource_usage(self, pid: int, resource_key: str, delta: int) -> None:
        """Update current resource usage tracker for PID."""
        if pid in self._resource_usage:
            self._resource_usage[pid][resource_key] = max(
                0, self._resource_usage[pid].get(resource_key, 0) + delta
            )

    def get_resource_usage(self, pid: int) -> Dict[str, int]:
        """Return current resource usage copy for PID."""
        return dict(self._resource_usage.get(pid, {}))
