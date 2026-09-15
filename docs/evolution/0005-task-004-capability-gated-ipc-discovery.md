# ADR 0005: TASK-004 — Capability-Gated IPC Endpoint Discovery

- **Status**: Accepted
- **Author**: Jules (AI Agent)
- **Date**: 2026-09-14

## Context & Motivation
TASK-004 requires adding capability-based access control for registering, discovering, and looking up IPC endpoints in the microkernel.

## Architectural Changes
1. Added `IPCEndpoint` dataclass to `ai_os/kernel/ipc.py` holding `endpoint_id`, `owner_pid`, `required_capability`, and `description`.
2. Added `register_endpoint()`, `discover_endpoints()`, and `lookup_endpoint()` methods to `IPCManager`.
3. Gated endpoint discovery behind `SYSCALL_EXEC` and matching endpoint capability checks.
4. Integrated `IPC_ENDPOINT_DENIED` telemetry audit events whenever unauthorized processes attempt registration or discovery.

## Safety & Invariant Verification
- Unprivileged processes without `SYSCALL_EXEC` or matching endpoint capabilities cannot discover or inspect protected IPC endpoints.
- Unauthorized registration or discovery attempts trigger telemetry audit logs.

## Verification & Test Results
- Added unit test `test_ipc_endpoint_discovery` in `tests/test_kernel.py`.
- Verified 100% test pass rate.
