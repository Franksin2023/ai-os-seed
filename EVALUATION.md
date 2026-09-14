# EVALUATION.md - System Evaluation & Benchmark Standards

This document establishes the evaluation criteria, verification standards, and quality metrics required for changes submitted to `AI-OS-SEED`.

---

## 1. System Quality Gates

Before any change is accepted into the repository, it must satisfy four mandatory quality gates:

| Quality Gate | Requirement | Verification Command |
| :--- | :--- | :--- |
| **Bootability** | Kernel boots clean through POST with exit code 0 | `python3 boot.py` |
| **Test Coverage** | 100% of tests in `tests/` pass without errors | `python3 -m pytest` |
| **Safety Verification** | All capability violation tests pass and safety checks trigger | `python3 -m pytest tests/test_kernel.py -k security` |
| **Documentation** | An evolution log entry exists in `docs/evolution/` | File check in `docs/evolution/` |

---

## 2. Key Performance Indicators (KPIs) & Metrics

Agents introducing evolutionary improvements should measure and log performance metrics in their ADRs:

1. **Boot Latency**: Time elapsed during system hardware POST and microkernel initialization (target < 100ms).
2. **Syscall Latency**: Average time required to validate capability and dispatch syscalls (target < 1ms).
3. **IPC Throughput**: Messages processed per second across capability-guarded channels.
4. **Context Switch Overhead**: CPU clock time spent during process scheduling context switches.
5. **Memory Efficiency**: Heap consumption per idle process context.

---

## 3. Standard Verification Checklist for Agents

```markdown
- [ ] System boots cleanly via `python3 boot.py`.
- [ ] All unit and integration tests pass via `python3 -m pytest`.
- [ ] Security capability tests verify isolation and enforcement.
- [ ] An ADR file is created in `docs/evolution/`.
- [ ] Code conforms to Python typing annotations and clean code standards.
```
