# ADR 0003: TASK-002 — Pub-Sub IPC Channel with Topic Routing

- **Status**: Accepted
- **Author**: Jules (AI Agent)
- **Date**: 2026-09-14

## Context & Motivation
TASK-002 requires adding a publish-subscribe IPC channel primitive (`PubSubChannel`) with topic-based pattern routing (`fnmatch`) and capability controls.

## Architectural Changes
1. Added `PubSubChannel` class to `ai_os/kernel/ipc.py` providing topic subscription, wildcard pattern matching (`fnmatch`), unsubscription, capability-checked message publishing, and subscriber inboxes.
2. Added `get_pubsub_channel()` to `IPCManager` in `ai_os/kernel/ipc.py`.
3. Integrated telemetry audit logging (`IPC_PUBSUB_EVENT`) on every publish event.

## Safety & Invariant Verification
- Publishers must hold `IPC_SEND` capability matching the `channel_id`.
- Subscribers must hold `IPC_RECEIVE` capability matching the `channel_id` to subscribe and receive routed messages.
- Topic routing uses non-blocking wildcard pattern matching (`fnmatch`), guaranteeing zero deadlock risk.

## Verification & Test Results
- Added unit tests in `tests/test_kernel.py` (`test_ipc_pubsub_channel`).
- Verified 100% test pass rate.
