# ADR 0004: TASK-003 — IPC Queue Overflow Protection

- **Status**: Accepted
- **Author**: Jules (AI Agent)
- **Date**: 2026-09-14

## Context & Motivation
TASK-003 requires adding bounded IPC message queue limits and overflow protection with a drop-oldest policy to prevent memory exhaustion and scheduler stalls.

## Architectural Changes
1. Configured `max_queue_size` limit (default 100 messages) in `IPCManager` and `PubSubChannel` in `ai_os/kernel/ipc.py`.
2. Implemented `drop_oldest` policy (`popleft()`) when message count exceeds `max_queue_size`.
3. Integrated telemetry audit logging (`IPC_OVERFLOW`) whenever messages are dropped due to queue overflow.

## Safety & Invariant Verification
- Prevents unbounded memory growth in IPC message queues and inboxes.
- Non-blocking drop-oldest policy guarantees that system processes and the scheduler never stall during queue overflow conditions.
- Audit logs capture all overflow events for system observability.

## Verification & Test Results
- Added unit test `test_ipc_queue_overflow_protection` in `tests/test_kernel.py`.
- Verified 100% test pass rate.
