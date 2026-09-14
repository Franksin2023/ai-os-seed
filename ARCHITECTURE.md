# ARCHITECTURE.md - System Architecture Specifications

This document defines the microkernel architecture, subsystem responsibilities, security model, and component interactions of `AI-OS-SEED`.

---

## 1. System Design Overview

AI-OS-SEED employs a modular, capability-based microkernel architecture designed specifically for AI agent workloads. The kernel follows the principle of least privilege, isolating all process operations behind a strict capability gateway and structured system call interface.

```
+-----------------------------------------------------------------+
|                         Agent RPC API                           |
|                    (Introspection & Control)                    |
+-----------------------------------------------------------------+
                                |
                                v
+-----------------------------------------------------------------+
|                       Syscall Dispatcher                        |
|              (Capability Validation & Verification)             |
+-----------------------------------------------------------------+
        |                 |               |                |
        v                 v               v                v
+---------------+ +---------------+ +----------+ +----------------+
| Security Mgr  | | Memory space  | |   VFS    | |   IPC Queue    |
| (CBAC Quotas) | |   Isolation   | | (Memory) | |  (Capability)  |
+---------------+ +---------------+ +----------+ +----------------+
        ^                 ^               ^                ^
        |                 |               |                |
+-----------------------------------------------------------------+
|                    Priority Process Scheduler                   |
|                    & Telemetry Audit Logger                     |
+-----------------------------------------------------------------+
```

---

## 2. Microkernel Subsystems (`ai_os/kernel/`)

### 2.1 Types & Core Abstractions (`types.py`)
- Defines kernel data structures including Process Control Block (PCB) states (`CREATED`, `READY`, `RUNNING`, `BLOCKED`, `SUSPENDED`, `TERMINATED`).
- Enforces capability definitions (`Capability`, `CapabilityType`) covering process spawning, memory allocation/read/write, VFS operations, and IPC message passing.

### 2.2 Security & Access Control (`security.py`)
- Implements Capability-Based Access Control (CBAC).
- Enforces resource quotas per PID (maximum memory bytes, open files, active IPC channels, and CPU ticks).
- Validates capability scopes prior to executing any system call or resource modification.

### 2.3 Virtual Memory Manager (`memory.py`)
- Provides per-process address space isolation (`MemorySpace`).
- Manages memory allocation, byte read/write bounds checking, and free operations.
- Direct inter-process memory tampering is strictly forbidden by design.

### 2.4 Virtual File System (`vfs.py`)
- In-memory hierarchical Virtual File System (`VFS`).
- Path normalization, directory creation, file reading/writing, and directory listing.
- Every VFS path access is gated by process capabilities (`VFS_READ`, `VFS_WRITE`, `VFS_LIST`).

### 2.5 Inter-Process Communication (`ipc.py`)
- Named IPC channels and process message inboxes (`IPCManager`).
- Capability-guarded message transmission (`IPC_SEND`) and reception (`IPC_RECEIVE`).

### 2.6 Process Scheduler (`scheduler.py`)
- Preemptive/cooperative priority queue process scheduler.
- Tracks process states, manages context switches, and ticks execution progress.
- Enforces CPU tick quotas to prevent runaway processes.

### 2.7 Syscall Gateway (`syscall.py`)
- Central entrypoint for all process requests into kernel space.
- Validates process existence and capability permissions before executing system calls.

### 2.8 Telemetry & Audit Logger (`telemetry.py`)
- Immutable event logger capturing syscall executions, security rejections, boot events, and state transitions.

### 2.9 Microkernel Core & Agent API (`core.py`, `agent_api.py`)
- `KernelCore`: Orchestrates boot/shutdown lifecycle and holds subsystem instances.
- `AgentAPI`: Exposes RPC endpoints for agents to query system status, inspect processes, execute syscalls, and fetch telemetry logs.

---

## 3. Security Invariants
1. No unprivileged process can perform system calls without matching `Capability` tokens.
2. Memory address spaces are strictly isolated per process.
3. System calls emit audit telemetry events for maximum agent observability.
