"""
Process control block and priority scheduler for AI-OS.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
from ai_os.kernel.types import ProcessState, Capability, ResourceLimits


@dataclass
class PCB:
    """Process Control Block."""

    pid: int
    name: str
    entry_point: Optional[Callable] = None
    priority: int = 10  # Lower number = higher priority
    state: ProcessState = ProcessState.CREATED
    capabilities: List[Capability] = field(default_factory=list)
    limits: ResourceLimits = field(default_factory=ResourceLimits)
    cpu_ticks_consumed: int = 0


class Scheduler:
    """
    Time-slicing process scheduler with priority queue support.
    """

    def __init__(self) -> None:
        self._processes: Dict[int, PCB] = {}
        self._ready_queue: List[int] = []
        self._current_pid: Optional[int] = None
        self._next_pid = 1

    def create_process(
        self,
        name: str,
        entry_point: Optional[Callable] = None,
        priority: int = 10,
        capabilities: Optional[List[Capability]] = None,
        limits: Optional[ResourceLimits] = None,
    ) -> PCB:
        pid = self._next_pid
        self._next_pid += 1

        pcb = PCB(
            pid=pid,
            name=name,
            entry_point=entry_point,
            priority=priority,
            state=ProcessState.READY,
            capabilities=capabilities or [],
            limits=limits or ResourceLimits(),
        )

        self._processes[pid] = pcb
        self._ready_queue.append(pid)
        self._sort_ready_queue()
        return pcb

    def terminate_process(self, pid: int) -> bool:
        pcb = self._processes.get(pid)
        if not pcb:
            return False
        pcb.state = ProcessState.TERMINATED
        if pid in self._ready_queue:
            self._ready_queue.remove(pid)
        if self._current_pid == pid:
            self._current_pid = None
        return True

    def _sort_ready_queue(self) -> None:
        self._ready_queue.sort(key=lambda pid: self._processes[pid].priority)

    def schedule(self) -> Optional[PCB]:
        """Context switch to next READY process."""
        if self._current_pid and self._current_pid in self._processes:
            curr_pcb = self._processes[self._current_pid]
            if curr_pcb.state == ProcessState.RUNNING:
                curr_pcb.state = ProcessState.READY
                self._ready_queue.append(self._current_pid)

        if not self._ready_queue:
            self._current_pid = None
            return None

        self._sort_ready_queue()
        next_pid = self._ready_queue.pop(0)
        next_pcb = self._processes[next_pid]
        next_pcb.state = ProcessState.RUNNING
        self._current_pid = next_pid
        return next_pcb

    def tick(self) -> Optional[PCB]:
        """Simulate single clock tick for currently executing process."""
        if not self._current_pid or self._current_pid not in self._processes:
            return self.schedule()

        pcb = self._processes[self._current_pid]
        pcb.cpu_ticks_consumed += 1

        # Check resource limit for CPU ticks
        if pcb.cpu_ticks_consumed >= pcb.limits.max_cpu_ticks:
            pcb.state = ProcessState.SUSPENDED
            self._current_pid = None
            return self.schedule()

        return pcb

    def get_process(self, pid: int) -> Optional[PCB]:
        return self._processes.get(pid)

    @property
    def current_process(self) -> Optional[PCB]:
        if self._current_pid:
            return self._processes.get(self._current_pid)
        return None

    def list_processes(self) -> List[PCB]:
        return list(self._processes.values())
