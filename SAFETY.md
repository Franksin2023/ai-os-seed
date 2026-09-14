# SAFETY.md - Inviolable Safety & Security Constraints

This document specifies the **hard constraints** and **immutable safety invariants** of `AI-OS-SEED`. No agent, process, or system modification may disable, bypass, or weaken these rules.

---

## 1. Immutable Safety Invariants

### Invariant 1: Capability Enforcement
- No process or agent may execute a system call, access memory outside its assigned regions, read/write VFS paths, or send IPC messages without holding explicit, verified `Capability` tokens.
- Kernel code must validate capability scopes BEFORE executing any request.

### Invariant 2: Process Isolation & Sandboxing
- Processes must operate within isolated memory spaces and restricted VFS mount points.
- Direct raw memory references across process boundaries are strictly forbidden.

### Invariant 3: Bound Resource Limits
- Every process must be bound by strict resource quotas (maximum memory bytes, maximum open VFS handles, maximum active IPC channels, and maximum CPU time-slice ticks).
- Exceeding resource limits must trigger process suspension or termination with telemetry audit logging.

### Invariant 4: Auditability & Telemetry
- All syscall failures, security capability rejections, process state transitions, and resource boundary violations MUST produce an immutable telemetry audit event.

### Invariant 5: Kernel Memory Protection
- User-space code or untrusted agents must never hold direct references to kernel internal data structures (`KernelCore`, `Scheduler`, `CapabilityManager`). All interactions must pass through the `SyscallDispatcher` or `AgentAPI` barriers.

---

## 2. Prohibited Behaviors

The following actions are strictly prohibited in any PR or evolutionary update:
1. Removing or disabling capability validation in `ai_os/kernel/security.py` or `ai_os/kernel/syscall.py`.
2. Exposing unchecked arbitrary shell or OS execution wrappers (`os.system`, `subprocess` without sandboxing) to user-space processes.
3. Silencing security exception logs or suppressing telemetry failures.
4. Hardcoding backdoor admin bypass privileges that skip capability verification.
