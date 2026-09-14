"""
Syscall dispatcher and security validator for AI-OS.
"""

from typing import TYPE_CHECKING, Any, Dict, Optional
from ai_os.kernel.types import (
    CapabilityType,
    SyscallCode,
    SyscallRequest,
    SyscallResponse,
)

if TYPE_CHECKING:
    from ai_os.kernel.core import KernelCore


class SyscallDispatcher:
    """
    Validates capabilities and dispatches system calls to microkernel subsystems.
    """

    def __init__(self, kernel: "KernelCore") -> None:
        self.kernel = kernel

    def dispatch(self, request: SyscallRequest) -> SyscallResponse:
        pid = request.pid
        code = request.code
        args = request.args or {}

        # Verify kernel process or valid process registration
        pcb = self.kernel.scheduler.get_process(pid)
        if not pcb:
            self.kernel.telemetry.log_event(
                "SYSCALL_REJECTED",
                pid=pid,
                details={"reason": "INVALID_PID", "code": code.value},
            )
            return SyscallResponse(
                success=False, error=f"Invalid Process ID: {pid}"
            )

        # Dispatch table mapping SyscallCode to handlers
        handler_map = {
            SyscallCode.PROCESS_CREATE: self._handle_process_create,
            SyscallCode.PROCESS_TERMINATE: self._handle_process_terminate,
            SyscallCode.PROCESS_YIELD: self._handle_process_yield,
            SyscallCode.MEMORY_ALLOCATE: self._handle_memory_allocate,
            SyscallCode.MEMORY_READ: self._handle_memory_read,
            SyscallCode.MEMORY_WRITE: self._handle_memory_write,
            SyscallCode.VFS_READ: self._handle_vfs_read,
            SyscallCode.VFS_WRITE: self._handle_vfs_write,
            SyscallCode.VFS_LIST: self._handle_vfs_list,
            SyscallCode.IPC_SEND: self._handle_ipc_send,
            SyscallCode.IPC_RECEIVE: self._handle_ipc_receive,
            SyscallCode.TELEMETRY_EMIT: self._handle_telemetry_emit,
        }

        handler = handler_map.get(code)
        if not handler:
            return SyscallResponse(
                success=False, error=f"Unsupported Syscall Code: {code}"
            )

        res = handler(pid, args)

        self.kernel.telemetry.log_event(
            "SYSCALL_EXECUTE",
            pid=pid,
            details={"code": code.value, "success": res.success, "error": res.error},
        )

        return res

    def _handle_process_create(self, pid: int, args: Dict[str, Any]) -> SyscallResponse:
        if not self.kernel.security.check_capability(pid, CapabilityType.PROCESS_SPAWN):
            return SyscallResponse(success=False, error="Capability Denied: PROCESS_SPAWN")

        name = args.get("name", "unnamed_proc")
        priority = args.get("priority", 10)
        caps = args.get("capabilities", [])
        limits = args.get("limits")

        new_pcb = self.kernel.create_process(
            name=name,
            priority=priority,
            capabilities=caps,
            limits=limits,
        )
        return SyscallResponse(success=True, data={"pid": new_pcb.pid})

    def _handle_process_terminate(self, pid: int, args: Dict[str, Any]) -> SyscallResponse:
        target_pid = args.get("target_pid", pid)
        if target_pid != pid and not self.kernel.security.check_capability(
            pid, CapabilityType.PROCESS_KILL, str(target_pid)
        ):
            return SyscallResponse(success=False, error="Capability Denied: PROCESS_KILL")

        success = self.kernel.terminate_process(target_pid)
        return SyscallResponse(success=success)

    def _handle_process_yield(self, pid: int, args: Dict[str, Any]) -> SyscallResponse:
        next_pcb = self.kernel.scheduler.schedule()
        return SyscallResponse(
            success=True, data={"next_pid": next_pcb.pid if next_pcb else None}
        )

    def _handle_memory_allocate(self, pid: int, args: Dict[str, Any]) -> SyscallResponse:
        if not self.kernel.security.check_capability(pid, CapabilityType.MEMORY_ALLOC):
            return SyscallResponse(success=False, error="Capability Denied: MEMORY_ALLOC")

        addr = args.get("address", 0)
        size = args.get("size", 0)

        space = self.kernel.memory.get_space(pid)
        if not space:
            return SyscallResponse(success=False, error="No memory space for PID")

        ok = space.allocate(addr, size)
        return SyscallResponse(success=ok)

    def _handle_memory_read(self, pid: int, args: Dict[str, Any]) -> SyscallResponse:
        if not self.kernel.security.check_capability(pid, CapabilityType.MEMORY_READ):
            return SyscallResponse(success=False, error="Capability Denied: MEMORY_READ")

        addr = args.get("address", 0)
        size = args.get("size")

        space = self.kernel.memory.get_space(pid)
        if not space:
            return SyscallResponse(success=False, error="No memory space for PID")

        data = space.read(addr, size)
        if data is None:
            return SyscallResponse(success=False, error="Memory Read Error")
        return SyscallResponse(success=True, data=data)

    def _handle_memory_write(self, pid: int, args: Dict[str, Any]) -> SyscallResponse:
        if not self.kernel.security.check_capability(pid, CapabilityType.MEMORY_WRITE):
            return SyscallResponse(success=False, error="Capability Denied: MEMORY_WRITE")

        addr = args.get("address", 0)
        data = args.get("data", b"")

        space = self.kernel.memory.get_space(pid)
        if not space:
            return SyscallResponse(success=False, error="No memory space for PID")

        ok = space.write(addr, data)
        return SyscallResponse(success=ok)

    def _handle_vfs_read(self, pid: int, args: Dict[str, Any]) -> SyscallResponse:
        path = args.get("path", "")
        content = self.kernel.vfs.read_file(pid, path)
        if content is None:
            return SyscallResponse(success=False, error="VFS Read Error / Capability Denied")
        return SyscallResponse(success=True, data=content)

    def _handle_vfs_write(self, pid: int, args: Dict[str, Any]) -> SyscallResponse:
        path = args.get("path", "")
        content = args.get("content", b"")
        ok = self.kernel.vfs.write_file(pid, path, content)
        if not ok:
            return SyscallResponse(success=False, error="VFS Write Error / Capability Denied")
        return SyscallResponse(success=True)

    def _handle_vfs_list(self, pid: int, args: Dict[str, Any]) -> SyscallResponse:
        path = args.get("path", "/")
        files = self.kernel.vfs.list_dir(pid, path)
        if files is None:
            return SyscallResponse(success=False, error="VFS List Error / Capability Denied")
        return SyscallResponse(success=True, data=files)

    def _handle_ipc_send(self, pid: int, args: Dict[str, Any]) -> SyscallResponse:
        receiver_pid = args.get("receiver_pid")
        channel = args.get("channel", "default")
        payload = args.get("payload")

        if receiver_pid is None:
            return SyscallResponse(success=False, error="Missing receiver_pid")

        ok = self.kernel.ipc.send_message(
            sender_pid=pid, receiver_pid=receiver_pid, channel=channel, payload=payload
        )
        if not ok:
            return SyscallResponse(success=False, error="IPC Send Error / Capability Denied")
        return SyscallResponse(success=True)

    def _handle_ipc_receive(self, pid: int, args: Dict[str, Any]) -> SyscallResponse:
        channel = args.get("channel", "default")
        msg = self.kernel.ipc.receive_message(receiver_pid=pid, channel=channel)
        if not msg:
            return SyscallResponse(success=False, error="No IPC message available")
        return SyscallResponse(
            success=True,
            data={
                "sender_pid": msg.sender_pid,
                "channel": msg.channel,
                "payload": msg.payload,
            },
        )

    def _handle_telemetry_emit(self, pid: int, args: Dict[str, Any]) -> SyscallResponse:
        event_type = args.get("event_type", "USER_EVENT")
        details = args.get("details", {})
        self.kernel.telemetry.log_event(event_type, pid=pid, details=details)
        return SyscallResponse(success=True)
