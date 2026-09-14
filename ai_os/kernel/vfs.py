"""
In-memory Virtual File System (VFS) with capability checks for AI-OS.
"""

import posixpath
from typing import Dict, List, Optional, Union
from ai_os.kernel.types import CapabilityType
from ai_os.kernel.security import SecurityManager


class VFSNode:
    """Base class for VFS file system entries."""

    def __init__(self, name: str) -> None:
        self.name = name


class VFSFile(VFSNode):
    """Represents an in-memory file."""

    def __init__(self, name: str, content: bytes = b"") -> None:
        super().__init__(name)
        self.content = bytearray(content)

    def read(self) -> bytes:
        return bytes(self.content)

    def write(self, data: bytes) -> None:
        self.content = bytearray(data)


class VFSDirectory(VFSNode):
    """Represents an in-memory directory."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.children: Dict[str, Union[VFSFile, "VFSDirectory"]] = {}


class VFS:
    """
    In-memory Virtual File System supporting capability-checked read, write, list, and directory creation.
    """

    def __init__(self, security_manager: SecurityManager) -> None:
        self.root = VFSDirectory("/")
        self.security_manager = security_manager

    def _normalize_path(self, path: str) -> str:
        normalized = posixpath.normpath(path)
        if not normalized.startswith("/"):
            normalized = "/" + normalized
        return normalized

    def _navigate_dir(self, path: str, create_if_missing: bool = False) -> Optional[VFSDirectory]:
        """Navigate to or create a directory path."""
        normalized = self._normalize_path(path)
        if normalized == "/":
            return self.root

        parts = [p for p in normalized.split("/") if p]
        curr = self.root

        for part in parts:
            if part not in curr.children:
                if create_if_missing:
                    new_dir = VFSDirectory(part)
                    curr.children[part] = new_dir
                    curr = new_dir
                else:
                    return None
            else:
                child = curr.children[part]
                if isinstance(child, VFSDirectory):
                    curr = child
                else:
                    return None
        return curr

    def _navigate(self, path: str) -> Optional[VFSNode]:
        """Navigate to existing node (file or directory)."""
        normalized = self._normalize_path(path)
        if normalized == "/":
            return self.root

        parts = [p for p in normalized.split("/") if p]
        curr = self.root

        for idx, part in enumerate(parts):
            if part not in curr.children:
                return None
            child = curr.children[part]
            if idx == len(parts) - 1:
                return child
            if isinstance(child, VFSDirectory):
                curr = child
            else:
                return None
        return None

    def read_file(self, pid: int, path: str) -> Optional[bytes]:
        norm = self._normalize_path(path)
        if not self.security_manager.check_capability(pid, CapabilityType.VFS_READ, norm):
            return None

        node = self._navigate(norm)
        if isinstance(node, VFSFile):
            return node.read()
        return None

    def write_file(self, pid: int, path: str, content: bytes) -> bool:
        norm = self._normalize_path(path)
        if not self.security_manager.check_capability(pid, CapabilityType.VFS_WRITE, norm):
            return False

        parent_path, filename = posixpath.split(norm)
        parent_node = self._navigate_dir(parent_path, create_if_missing=True)
        if not isinstance(parent_node, VFSDirectory):
            return False

        if filename in parent_node.children:
            existing = parent_node.children[filename]
            if isinstance(existing, VFSFile):
                existing.write(content)
                return True
            return False
        else:
            new_file = VFSFile(filename, content)
            parent_node.children[filename] = new_file
            return True

    def list_dir(self, pid: int, path: str) -> Optional[List[str]]:
        norm = self._normalize_path(path)
        if not self.security_manager.check_capability(pid, CapabilityType.VFS_LIST, norm):
            return None

        node = self._navigate(norm)
        if isinstance(node, VFSDirectory):
            return sorted(list(node.children.keys()))
        return None
