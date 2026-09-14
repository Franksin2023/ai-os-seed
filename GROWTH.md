# GROWTH.md - Evolutionary Guidelines for AI-OS

Welcome, AI Agent. This document defines the rules, processes, and evolutionary principles for expanding and improving `AI-OS-SEED`.

---

## 1. Core Principles of Evolution

1. **Self-Consistency & Bootability**: The system MUST remain fully bootable (`python3 boot.py`) and all tests MUST pass (`python3 -m pytest`) after every accepted change.
2. **Incremental & Verifiable Progress**: Prefer small, atomic, highly testable changes over monolithic refactors. Every change must be verified before submission.
3. **Safety & Invariants**: Never weaken or bypass any constraint defined in `SAFETY.md`. Security and isolation are non-negotiable hard invariants.
4. **Agent Legibility**: Code, documentation, and error messages must be structured clearly so future autonomous agents can understand, verify, and build upon them.
5. **Observability First**: All new subsystems must expose metrics, state introspection, and audit events via the kernel telemetry subsystem.

---

## 2. Mandatory Rules for Every Modification

Every meaningful commit or evolution step MUST include:
1. **Source Code Modifications**: High-quality, typed, documented code in `ai_os/`.
2. **Unit & Integration Tests**: Comprehensive tests covering normal behavior, edge cases, and security boundaries in `tests/`.
3. **Evolution Log (ADR)**: An Architectural Decision Record file added to `docs/evolution/` following the format `000X-title.md`.

---

## 3. Structure of an Evolution ADR (`docs/evolution/000X-*.md`)

When adding a new evolution entry, follow this schema:

```markdown
# ADR 000X: [Title of Change]

- **Status**: Proposed / Accepted / Superseded
- **Author**: [Agent Name / ID]
- **Date**: [YYYY-MM-DD]

## Context & Motivation
Why was this change necessary? What deficiency or feature gap does it address?

## Architectural Changes
What components were modified or created? How do they interact with existing kernel subsystems?

## Safety & Invariant Verification
How does this change respect `SAFETY.md`? What capability checks or resource limits were added?

## Test & Benchmark Results
List test commands run and verification metrics achieved.
```

---

## 4. Prioritized Areas for Growth

Future agents are encouraged to expand the operating system in the following domains:
- Enhanced IPC primitives (shared memory, pub-sub channels).
- Advanced memory eviction and paging strategies.
- Persistence mechanisms for VFS backed by transactional state.
- Hierarchical process trees, parent-child process handling, and signal trapping.
- Dynamic driver architecture and device abstraction layers.
- Advanced agent RPC tools and self-diagnostic auto-repair capabilities.
