# ADR 0002: TASK-001 — Shared Memory IPC Primitive

- **Status**: Accepted
- **Author**: Jules (AI Agent)
- **Date**: 2026-09-14

## Context & Motivation
TASK-001 requires adding a shared memory IPC primitive allowing multiple capability-authorized processes to map and exchange data through a shared memory region.

## Architectural Changes
1. Added `SharedMemoryRegion` class to `ai_os/kernel/ipc.py` providing bounded byte buffers, attachment tracking (`attached_pids`), and read/write bounds checking.
2. Added `create_shared_memory()`, `attach_shared_memory()`, and `detach_shared_memory()` to `IPCManager` in `ai_os/kernel/ipc.py`.
3. Integrated capability checks (`IPC_SEND`, `IPC_RECEIVE`) to gate creation and attachment to shared memory regions.

## Safety & Invariant Verification
- Processes must hold valid capabilities matching the region ID to create or attach to a shared memory region.
- Unattached processes cannot read from or write to shared memory buffers.
- All writes are strictly bounds-checked against the allocated buffer size (`size_bytes`).

## Verification & Test Results
- Added unit tests in `tests/test_kernel.py` (`test_ipc_shared_memory`).
- Verified zero regressions and 100% test pass rate.
