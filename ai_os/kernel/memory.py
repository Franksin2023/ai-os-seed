"""
Per-process isolated virtual memory subsystem for AI-OS.
"""

from typing import Dict, Optional


class MemorySpace:
    """Isolated page/region-based address space for a single process."""

    def __init__(self, pid: int, max_bytes: int = 1024 * 1024) -> None:
        self.pid = pid
        self.max_bytes = max_bytes
        self._memory: Dict[int, bytearray] = {}  # address -> bytearray block
        self._allocated_bytes = 0

    def allocate(self, address: int, size: int) -> bool:
        """Allocate a memory region of `size` bytes at `address`."""
        if address < 0 or size <= 0:
            return False
        if self._allocated_bytes + size > self.max_bytes:
            return False
        if address in self._memory:
            return False  # Address collision

        self._memory[address] = bytearray(size)
        self._allocated_bytes += size
        return True

    def write(self, address: int, data: bytes) -> bool:
        """Write bytes to allocated memory block at `address`."""
        if address not in self._memory:
            return False
        block = self._memory[address]
        if len(data) > len(block):
            return False
        block[: len(data)] = data
        return True

    def read(self, address: int, size: Optional[int] = None) -> Optional[bytes]:
        """Read bytes from memory block at `address`."""
        if address not in self._memory:
            return None
        block = self._memory[address]
        if size is None or size > len(block):
            return bytes(block)
        return bytes(block[:size])

    def free(self, address: int) -> bool:
        """Free memory region at `address`."""
        if address in self._memory:
            self._allocated_bytes -= len(self._memory[address])
            del self._memory[address]
            return True
        return False

    @property
    def allocated_bytes(self) -> int:
        return self._allocated_bytes


class MemoryManager:
    """Kernel memory manager holding address spaces for all active processes."""

    def __init__(self) -> None:
        self._spaces: Dict[int, MemorySpace] = {}

    def create_space(self, pid: int, max_bytes: int = 1024 * 1024) -> MemorySpace:
        space = MemorySpace(pid=pid, max_bytes=max_bytes)
        self._spaces[pid] = space
        return space

    def destroy_space(self, pid: int) -> None:
        self._spaces.pop(pid, None)

    def get_space(self, pid: int) -> Optional[MemorySpace]:
        return self._spaces.get(pid)
