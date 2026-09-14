"""
Agent-friendly RPC and system state introspection interface for AI-OS.
"""

from typing import Any, Dict, List, Optional
from ai_os.kernel.core import KernelCore
from ai_os.kernel.types import SyscallCode, SyscallRequest, SyscallResponse


class AgentAPI:
    """
    Dedicated interface for autonomous agents to inspect, query, and interact with AI-OS.
    """

    def __init__(self, kernel: KernelCore) -> None:
        self.kernel = kernel

    def get_system_status(self) -> Dict[str, Any]:
        """Return high-level summary of kernel health, processes, and memory usage."""
        processes = self.kernel.scheduler.list_processes()
        return {
            "booted": self.kernel.is_booted,
            "process_count": len(processes),
            "active_pid": self.kernel.scheduler.current_process.pid
            if self.kernel.scheduler.current_process
            else None,
            "telemetry_event_count": len(self.kernel.telemetry.get_events()),
        }

    def inspect_process(self, pid: int) -> Optional[Dict[str, Any]]:
        """Retrieve detailed process control block and resource state."""
        pcb = self.kernel.scheduler.get_process(pid)
        if not pcb:
            return None

        mem_space = self.kernel.memory.get_space(pid)
        res_usage = self.kernel.security.get_resource_usage(pid)

        return {
            "pid": pcb.pid,
            "name": pcb.name,
            "state": pcb.state.name,
            "priority": pcb.priority,
            "cpu_ticks_consumed": pcb.cpu_ticks_consumed,
            "allocated_memory_bytes": mem_space.allocated_bytes if mem_space else 0,
            "resource_usage": res_usage,
            "capabilities": [
                f"{c.cap_type.value}:{c.resource}" for c in pcb.capabilities
            ],
        }

    def list_processes(self) -> List[Dict[str, Any]]:
        """List all active and terminated process control blocks."""
        return [
            {
                "pid": pcb.pid,
                "name": pcb.name,
                "state": pcb.state.name,
                "priority": pcb.priority,
            }
            for pcb in self.kernel.scheduler.list_processes()
        ]

    def execute_syscall(
        self, pid: int, code: str, args: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a syscall on behalf of an agent-controlled process."""
        try:
            syscall_code = SyscallCode(code)
        except ValueError:
            return {"success": False, "error": f"Invalid Syscall Code: {code}"}

        req = SyscallRequest(pid=pid, code=syscall_code, args=args or {})
        resp: SyscallResponse = self.kernel.syscall(req)

        return {
            "success": resp.success,
            "data": resp.data,
            "error": resp.error,
        }

    def get_telemetry_logs(
        self, event_type: Optional[str] = None, pid: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Fetch audit and observability events."""
        events = self.kernel.telemetry.get_events(event_type=event_type, pid=pid)
        return [
            {
                "event_type": e.event_type,
                "pid": e.pid,
                "details": e.details,
                "timestamp": e.timestamp,
            }
            for e in events
        ]
