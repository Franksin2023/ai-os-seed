"""
Unit tests for TASK-005 IPC Message Priority Queue with Deadline Scheduling.
"""

import time
import pytest
from ai_os.kernel.core import KernelCore
from ai_os.kernel.types import Capability, CapabilityType


def test_ipc_priority_queue():
    kernel = KernelCore()
    kernel.boot()

    cap_send = Capability(CapabilityType.IPC_SEND, "priority_channel")
    cap_recv = Capability(CapabilityType.IPC_RECEIVE, "priority_channel")

    p1 = kernel.create_process(name="p1", capabilities=[cap_send])
    p2 = kernel.create_process(name="p2", capabilities=[cap_recv])

    now = time.time()

    # Send low priority message (priority 10)
    assert kernel.ipc.send_message(p1.pid, p2.pid, "priority_channel", "low_prio", priority=10) is True

    # Send urgent high priority message (priority 1)
    assert kernel.ipc.send_message(p1.pid, p2.pid, "priority_channel", "high_prio", priority=1) is True

    # Send medium priority message with urgent deadline (priority 5, deadline now + 1)
    assert kernel.ipc.send_message(p1.pid, p2.pid, "priority_channel", "medium_urgent", priority=5, deadline=now + 1.0) is True

    # Receive 1st message: should be high_prio (priority 1)
    m1 = kernel.ipc.receive_message(p2.pid, "priority_channel")
    assert m1 is not None
    assert m1.payload == "high_prio"

    # Receive 2nd message: should be medium_urgent (priority 5)
    m2 = kernel.ipc.receive_message(p2.pid, "priority_channel")
    assert m2 is not None
    assert m2.payload == "medium_urgent"

    # Receive 3rd message: should be low_prio (priority 10)
    m3 = kernel.ipc.receive_message(p2.pid, "priority_channel")
    assert m3 is not None
    assert m3.payload == "low_prio"

    # Telemetry verification
    prio_events = kernel.telemetry.get_events(event_type="IPC_PRIORITY_MESSAGE")
    assert len(prio_events) == 3
