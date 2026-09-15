"""
Capability-guarded Inter-Process Communication (IPC) for AI-OS.
Supports message queues, shared memory regions, pub-sub topic routing, and overflow protection.
"""

import fnmatch
from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set
from ai_os.kernel.types import CapabilityType
from ai_os.kernel.security import SecurityManager

if TYPE_CHECKING:
    from ai_os.kernel.telemetry import TelemetrySubsystem


@dataclass
class IPCMessage:
    sender_pid: int
    receiver_pid: int
    channel: str
    payload: Any


class SharedMemoryRegion:
    """
    Represents a shared memory region accessible by multiple capability-authorized processes.
    """

    def __init__(self, region_id: str, size_bytes: int) -> None:
        self.region_id = region_id
        self.size_bytes = size_bytes
        self.buffer = bytearray(size_bytes)
        self.attached_pids: Set[int] = set()

    def attach(self, pid: int) -> bool:
        """Attach process PID to the shared memory region."""
        self.attached_pids.add(pid)
        return True

    def detach(self, pid: int) -> bool:
        """Detach process PID from the shared memory region."""
        if pid in self.attached_pids:
            self.attached_pids.remove(pid)
            return True
        return False

    def read(self, pid: int, offset: int = 0, length: Optional[int] = None) -> Optional[bytes]:
        """Read bytes from shared region if PID is attached."""
        if pid not in self.attached_pids:
            return None
        if offset < 0 or offset >= self.size_bytes:
            return None
        end = self.size_bytes if length is None else min(self.size_bytes, offset + length)
        return bytes(self.buffer[offset:end])

    def write(self, pid: int, data: bytes, offset: int = 0) -> bool:
        """Write bytes to shared region if PID is attached."""
        if pid not in self.attached_pids:
            return False
        if offset < 0 or offset + len(data) > self.size_bytes:
            return False
        self.buffer[offset : offset + len(data)] = data
        return True


class PubSubChannel:
    """
    Publish-subscribe IPC channel with topic pattern matching and capability controls.
    """

    def __init__(
        self,
        channel_id: str,
        security_manager: SecurityManager,
        telemetry: Optional["TelemetrySubsystem"] = None,
        max_queue_size: int = 100,
    ) -> None:
        self.channel_id = channel_id
        self.security_manager = security_manager
        self.telemetry = telemetry
        self.max_queue_size = max_queue_size
        # Maps PID -> Set[topic_pattern]
        self.subscriptions: Dict[int, Set[str]] = {}
        # Maps PID -> deque of (topic, payload) messages
        self.inboxes: Dict[int, deque] = {}

    def subscribe(self, pid: int, topic_pattern: str) -> bool:
        """Subscribe process PID to a topic pattern."""
        if not self.security_manager.check_capability(pid, CapabilityType.IPC_RECEIVE, self.channel_id):
            return False

        if pid not in self.subscriptions:
            self.subscriptions[pid] = set()
            self.inboxes[pid] = deque()

        self.subscriptions[pid].add(topic_pattern)
        return True

    def unsubscribe(self, pid: int, topic_pattern: str) -> bool:
        """Unsubscribe process PID from a topic pattern."""
        if pid in self.subscriptions and topic_pattern in self.subscriptions[pid]:
            self.subscriptions[pid].remove(topic_pattern)
            return True
        return False

    def publish(self, publisher_pid: int, topic: str, payload: Any) -> int:
        """Publish payload on topic to matching subscriber inboxes with overflow protection."""
        if not self.security_manager.check_capability(publisher_pid, CapabilityType.IPC_SEND, self.channel_id):
            return 0

        subscribers_notified = 0
        for pid, patterns in self.subscriptions.items():
            if not self.security_manager.check_capability(pid, CapabilityType.IPC_RECEIVE, self.channel_id):
                continue

            for pat in patterns:
                if fnmatch.fnmatch(topic, pat):
                    inbox = self.inboxes[pid]
                    if len(inbox) >= self.max_queue_size:
                        inbox.popleft()  # Drop oldest
                        if self.telemetry:
                            self.telemetry.log_event(
                                "IPC_OVERFLOW",
                                pid=pid,
                                details={"channel_id": self.channel_id, "policy": "drop_oldest"},
                            )

                    inbox.append((topic, payload))
                    subscribers_notified += 1
                    break

        if self.telemetry:
            self.telemetry.log_event(
                "IPC_PUBSUB_EVENT",
                pid=publisher_pid,
                details={
                    "channel_id": self.channel_id,
                    "topic": topic,
                    "subscribers_notified": subscribers_notified,
                },
            )

        return subscribers_notified

    def receive(self, pid: int) -> Optional[tuple]:
        """Fetch next (topic, payload) tuple for subscriber PID."""
        inbox = self.inboxes.get(pid)
        if not inbox or len(inbox) == 0:
            return None
        return inbox.popleft()


class IPCManager:
    """
    Manages named capability-restricted IPC channels, message queues, shared memory regions, and pub-sub channels with overflow protection.
    """

    def __init__(
        self,
        security_manager: SecurityManager,
        telemetry: Optional["TelemetrySubsystem"] = None,
        max_queue_size: int = 100,
    ) -> None:
        self.security_manager = security_manager
        self.telemetry = telemetry
        self.max_queue_size = max_queue_size
        # Maps channel_name -> deque of IPCMessage
        self._channels: Dict[str, deque] = {}
        # Maps PID -> deque of IPCMessage directed to specific process
        self._inboxes: Dict[int, deque] = {}
        # Maps region_id -> SharedMemoryRegion
        self.shared_regions: Dict[str, SharedMemoryRegion] = {}
        # Maps channel_id -> PubSubChannel
        self.pubsub_channels: Dict[str, PubSubChannel] = {}

    def get_pubsub_channel(self, channel_id: str) -> PubSubChannel:
        """Retrieve or create a PubSubChannel by channel_id."""
        if channel_id not in self.pubsub_channels:
            self.pubsub_channels[channel_id] = PubSubChannel(
                channel_id, self.security_manager, self.telemetry, self.max_queue_size
            )
        return self.pubsub_channels[channel_id]

    def send_message(self, sender_pid: int, receiver_pid: int, channel: str, payload: Any) -> bool:
        """Send message over channel to receiver_pid, gated by IPC_SEND capability and overflow policy."""
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

        channel_queue = self._channels[channel]
        if len(channel_queue) >= self.max_queue_size:
            channel_queue.popleft()  # Drop oldest
            if self.telemetry:
                self.telemetry.log_event(
                    "IPC_OVERFLOW",
                    pid=sender_pid,
                    details={"channel": channel, "policy": "drop_oldest"},
                )

        channel_queue.append(msg)

        if receiver_pid not in self._inboxes:
            self._inboxes[receiver_pid] = deque()

        inbox = self._inboxes[receiver_pid]
        if len(inbox) >= self.max_queue_size:
            inbox.popleft()  # Drop oldest
            if self.telemetry:
                self.telemetry.log_event(
                    "IPC_OVERFLOW",
                    pid=receiver_pid,
                    details={"inbox_pid": receiver_pid, "policy": "drop_oldest"},
                )

        inbox.append(msg)
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

    def create_shared_memory(self, region_id: str, size_bytes: int, creator_pid: int) -> Optional[SharedMemoryRegion]:
        """Create and map a shared memory region, gated by IPC_SEND capability."""
        if not self.security_manager.check_capability(creator_pid, CapabilityType.IPC_SEND, region_id):
            return None

        if region_id in self.shared_regions:
            return self.shared_regions[region_id]

        region = SharedMemoryRegion(region_id, size_bytes)
        region.attach(creator_pid)
        self.shared_regions[region_id] = region

        if self.telemetry:
            self.telemetry.log_event(
                "IPC_SHARED_MEMORY_MAP",
                pid=creator_pid,
                details={"region_id": region_id, "size_bytes": size_bytes},
            )

        return region

    def attach_shared_memory(self, region_id: str, pid: int) -> bool:
        """Attach process PID to an existing shared memory region, gated by capability."""
        if not self.security_manager.check_capability(pid, CapabilityType.IPC_RECEIVE, region_id):
            return False

        region = self.shared_regions.get(region_id)
        if not region:
            return False

        ok = region.attach(pid)
        if ok and self.telemetry:
            self.telemetry.log_event(
                "IPC_SHARED_MEMORY_MAP",
                pid=pid,
                details={"region_id": region_id},
            )
        return ok

    def detach_shared_memory(self, region_id: str, pid: int) -> bool:
        """Detach process PID from a shared memory region."""
        region = self.shared_regions.get(region_id)
        if not region:
            return False

        ok = region.detach(pid)
        if ok and self.telemetry:
            self.telemetry.log_event(
                "IPC_SHARED_MEMORY_UNMAP",
                pid=pid,
                details={"region_id": region_id},
            )
        return ok
