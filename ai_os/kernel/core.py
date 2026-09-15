"""
Microkernel core orchestrator managing system boot, shutdown, and process lifecycles.
"""

from typing import Callable, List, Optional
from ai_os.kernel.types import Capability, CapabilityType, ResourceLimits, SyscallRequest, SyscallResponse
from ai_os.kernel.security import SecurityManager
from ai_os.kernel.memory import MemoryManager
from ai_os.kernel.vfs import VFS
from ai_os.kernel.ipc import IPCManager
from ai_os.kernel.scheduler import Scheduler, PCB
from ai_os.kernel.telemetry import TelemetrySubsystem
from ai_os.kernel.syscall import SyscallDispatcher


class KernelCore:
    """
    Central microkernel core holding and linking all subsystem instances.
    """

    def __init__(self) -> None:
        self.security = SecurityManager()
        self.memory = MemoryManager()
        self.vfs = VFS(self.security)
        self.telemetry = TelemetrySubsystem()
        self.ipc = IPCManager(self.security, self.telemetry)
        self.scheduler = Scheduler()
        self.syscall_dispatcher = SyscallDispatcher(self)
        self.is_booted = False

    def boot(self) -> None:
        """Initialize microkernel core and boot system root process."""
        if self.is_booted:
            return

        self.telemetry.log_event("BOOT_START", details={"status": "initializing"})

        # Initialize root process (PID 0 reserved for kernel init)
        root_caps = [Capability(CapabilityType.ADMIN, "*")]
        self.security.register_process(pid=0, capabilities=root_caps)
        self.memory.create_space(pid=0)

        self.is_booted = True
        self.telemetry.log_event("BOOT_COMPLETE", details={"status": "ready"})

    def shutdown(self) -> None:
        """Gracefully power down kernel."""
        self.telemetry.log_event("SHUTDOWN_START")
        self.is_booted = False

    def create_process(
        self,
        name: str,
        entry_point: Optional[Callable] = None,
        priority: int = 10,
        capabilities: Optional[List[Capability]] = None,
        limits: Optional[ResourceLimits] = None,
    ) -> PCB:
        """Spawn and register a new process in kernel subsystems."""
        pcb = self.scheduler.create_process(
            name=name,
            entry_point=entry_point,
            priority=priority,
            capabilities=capabilities,
            limits=limits,
        )

        self.security.register_process(
            pid=pcb.pid,
            capabilities=capabilities,
            limits=limits,
        )
        self.memory.create_space(
            pid=pcb.pid,
            max_bytes=limits.max_memory_bytes if limits else 1024 * 1024,
        )

        self.telemetry.log_event(
            "PROCESS_CREATE",
            pid=pcb.pid,
            details={"name": name, "priority": priority},
        )
        return pcb

    def terminate_process(self, pid: int) -> bool:
        """Terminate and clean up process resources."""
        ok = self.scheduler.terminate_process(pid)
        if ok:
            self.security.unregister_process(pid)
            self.memory.destroy_space(pid)
            self.telemetry.log_event("PROCESS_TERMINATE", pid=pid)
        return ok

    def syscall(self, request: SyscallRequest) -> SyscallResponse:
        """Execute system call request."""
        if not self.is_booted:
            return SyscallResponse(success=False, error="Kernel Not Booted")
        return self.syscall_dispatcher.dispatch(request)

    def tick(self) -> Optional[PCB]:
        """Execute 1 system CPU tick."""
        if not self.is_booted:
            return None
        return self.scheduler.tick()
