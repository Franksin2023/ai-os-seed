# ADR 0000: Initial OS Seed Architecture

- **Status**: Accepted
- **Author**: Jules (AI Agent)
- **Date**: 2026-09-14

## Context & Motivation
`AI-OS-SEED` was initialized to provide a clean, verifiable, secure, capability-based microkernel operating system written in Python. This seed serves as the foundational substrate for future AI agents to inspect, operate, evaluate, and safely evolve over time.

## Architectural Design

The microkernel comprises nine decoupled, modular subsystems located in `ai_os/kernel/`:

1. **Types (`types.py`)**: Defines PIDs, process states, capability definitions (`Capability`, `CapabilityType`), system call codes, and structured request/response objects.
2. **Security & Access Control (`security.py`)**: Implements capability-based permission checks, sandboxed VFS path resolution, and resource quota monitoring.
3. **Memory Management (`memory.py`)**: Provides per-process address space isolation, page allocation, and bounds-checked read/write operations.
4. **Virtual File System (`vfs.py`)**: Implements an in-memory hierarchical VFS with capability-restricted path access.
5. **Inter-Process Communication (`ipc.py`)**: Manages capability-guarded message channels and queues between isolated processes.
6. **Process Scheduler (`scheduler.py`)**: Implements time-slicing preemptive execution, process priority management, and state transitions.
7. **Syscall Gateway (`syscall.py`)**: Serves as the single controlled entrypoint from process space into kernel space with strict capability verification.
8. **Telemetry & Audit (`telemetry.py`)**: Records structured audit logs, state snapshots, and system call events for complete agent observability.
9. **Kernel Core & Agent API (`core.py`, `agent_api.py`)**: Orchestrates system boot/shutdown, subsystem lifecycle, and provides an RPC interface for agent inspection and operation.

## Safety & Invariant Verification
- Capabilities are strictly checked on every syscall, VFS access, and IPC transmission.
- Process memory spaces are fully isolated; processes cannot access or alter other processes' memory without appropriate capability authorization.
- System POST and health checks run automatically at boot via `boot.py`.

## Verification & Test Results
- Full unit test coverage covering boot POST, capability enforcement, memory isolation, VFS, IPC, process scheduling, syscall dispatch, telemetry, and agent API interface.
- 100% test pass rate using `pytest`.
