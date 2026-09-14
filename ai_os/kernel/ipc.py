"""
Capability-guarded Inter-Process Communication (IPC) for AI-OS.
"""

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from ai_os.kernel.types import CapabilityType
from ai_os.kernel.security import SecurityManager


@dataclass
class IPCMessage:
    sender_pid: int
    receiver_pid: int
    channel: str
    payload: Any


class IPCManager:
    """
    Manages named capability-restricted IPC channels and process message queues.
    """

    def __init__(self, security_manager: SecurityManager) -> None:
        self.security_manager = security_manager
        # Maps channel_name -> deque of IPCMessage
        self._channels: Dict[str, deque] = {}
        # Maps PID -> deque of IPCMessage directed to specific process
        self._inboxes: Dict[int, deque] = {}

    def send_message(self, sender_pid: int, receiver_pid: int, channel: str, payload: Any) -> bool:
        """Send message over channel to receiver_pid, gated by IPC_SEND capability."""
        if not self.security_manager.check_capability(sender_pid, CapabilityType.IPC_SEND, channel):
            return False

        msg = IPCMessage(
            sender_pid=sender_pid,
            receiver_pid=receiver_pid,
            channel=channel,
            payload=payload,
        )

        if channel not in self._channels:
            self._channels[channel] = deque()
        self._channels[channel].append(msg)

        if receiver_pid not in self._inboxes:
            self._inboxes[receiver_pid] = deque()
        self._inboxes[receiver_pid].append(msg)

        return True

    def receive_message(self, receiver_pid: int, channel: str) -> Optional[IPCMessage]:
        """Receive oldest message on channel for receiver_pid, gated by IPC_RECEIVE capability."""
        if not self.security_manager.check_capability(receiver_pid, CapabilityType.IPC_RECEIVE, channel):
            return None

        inbox = self._inboxes.get(receiver_pid)
        if not inbox:
            return None

        for idx, msg in enumerate(inbox):
            if msg.channel == channel:
                del inbox[idx]
                return msg

        return None
