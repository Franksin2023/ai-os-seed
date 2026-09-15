"""
Data types, capability definitions, process states, and syscall structures for AI-OS.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set


class ProcessState(Enum):
    CREATED = auto()
    READY = auto()
    RUNNING = auto()
    BLOCKED = auto()
    SUSPENDED = auto()
    TERMINATED = auto()


class CapabilityType(Enum):
    PROCESS_SPAWN = "process:spawn"
    PROCESS_KILL = "process:kill"
    MEMORY_ALLOC = "memory:alloc"
    MEMORY_READ = "memory:read"
    MEMORY_WRITE = "memory:write"
    VFS_READ = "vfs:read"
    VFS_WRITE = "vfs:write"
    VFS_LIST = "vfs:list"
    IPC_SEND = "ipc:send"
    IPC_RECEIVE = "ipc:receive"
    SYSCALL_EXEC = "syscall:exec"
    ADMIN = "admin:root"
    AGENT_MUTATION = "agent:mutation"
    AGENT_OBSERVATION = "agent:observation"


@dataclass(frozen=True)
class Capability:
    cap_type: CapabilityType
    resource: str = "*"  # Path, process ID, channel name, or wildcards

    def allows(self, required_type: CapabilityType, target_resource: str) -> bool:
        if self.cap_type == CapabilityType.ADMIN:
            return True
        if self.cap_type != required_type:
            return False
        if self.resource == "*" or self.resource == target_resource:
            return True
        if self.resource.endswith("/*") and target_resource.startswith(self.resource[:-1]):
            return True
        return False


class SyscallCode(Enum):
    PROCESS_CREATE = "SYS_PROCESS_CREATE"
    PROCESS_TERMINATE = "SYS_PROCESS_TERMINATE"
    PROCESS_YIELD = "SYS_PROCESS_YIELD"
    MEMORY_ALLOCATE = "SYS_MEMORY_ALLOCATE"
    MEMORY_READ = "SYS_MEMORY_READ"
    MEMORY_WRITE = "SYS_MEMORY_WRITE"
    VFS_READ = "SYS_VFS_READ"
    VFS_WRITE = "SYS_VFS_WRITE"
    VFS_LIST = "SYS_VFS_LIST"
    IPC_SEND = "SYS_IPC_SEND"
    IPC_RECEIVE = "SYS_IPC_RECEIVE"
    TELEMETRY_EMIT = "SYS_TELEMETRY_EMIT"


@dataclass
class SyscallRequest:
    pid: int
    code: SyscallCode
    args: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyscallResponse:
    success: bool
    data: Any = None
    error: Optional[str] = None


@dataclass
class ResourceLimits:
    max_memory_bytes: int = 1024 * 1024  # 1MB
    max_open_files: int = 16
    max_ipc_channels: int = 8
    max_cpu_ticks: int = 1000
