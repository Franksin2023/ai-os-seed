# ADR 0006: TASK-005 — IPC Message Priority Queue with Deadline Scheduling

- **Status**: Accepted
- **Author**: Jules (AI Agent)
- **Date**: 2026-09-14

## Context & Motivation
TASK-005 requires adding priority levels and deadline-based scheduling to IPC messages to ensure critical system and process messages are delivered ahead of low-priority traffic.

## Architectural Changes
1. Added `priority` (int, default 10) and `deadline` (optional float) fields to `IPCMessage` in `ai_os/kernel/ipc.py`.
2. Updated `IPCManager.send_message()` to sort message queues by `(priority, deadline, created_at)`. Lower priority numbers are dequeued first.
3. Integrated `IPC_PRIORITY_MESSAGE` telemetry audit events when messages are enqueued.

## Safety & Invariant Verification
- Ensures high-priority messages bypass lower-priority queues without causing thread deadlocks or process starvation.
- Capability checks (`IPC_SEND`/`IPC_RECEIVE`) remain fully enforced.

## Verification & Test Results
- Created test file `tests/test_ipc_priority_queue.py` verifying priority ordering, deadline sorting, and telemetry logging.
- Verified 100% test pass rate.
