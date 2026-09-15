# AI-OS-SEED: Evolutionary Operating System Seed

AI-OS-SEED is an open, evolutionary seed for an agent-friendly, capability-based microkernel operating system. It provides a minimal, verifiable, secure, observable, and extensible foundation designed specifically for autonomous AI agents to inspect, evaluate, operate, and safely evolve over time.

---

## 🚀 Key Features & Architecture

AI-OS-SEED implements a capability-based microkernel design architecture in Python with clean abstractions for hardware isolation, security enforcement, and agent RPC integration:

- **Capability-Based Access Control (CBAC)**: Granular permissions for process execution, memory allocation, VFS path access, IPC endpoints, and syscall execution.
- **Isolated Virtual Memory**: Per-process isolated memory spaces preventing unauthorized inter-process memory tampering.
- **In-Memory VFS (Virtual File System)**: Hierarchical VFS with isolated root mounting and capability-guarded read/write/list operations.
- **Capability-Guarded IPC**: Inter-process message passing channels restricted by process capability tokens.
- **Priority Process Scheduler**: Time-slicing preemptive/cooperative process scheduler supporting priority queues, state transitions, and CPU tick execution.
- **Syscall Gateway & Telemetry**: Validated system call dispatcher paired with structured event audit logs and real-time state introspection.
- **Agent RPC API**: Dedicated, agent-friendly inspection and interaction interface for dynamic discovery, health evaluation, and evolutionary modifications.

---

## 🛠 Repository Structure

```
├── README.md               # Overview, architecture, and quickstart guide
├── GROWTH.md               # Rules of engagement and evolution guidelines for AI agents
├── SAFETY.md               # Hard security constraints and immutable safety invariants
├── EVALUATION.md           # Metrics, verification benchmarks, and quality gates
├── boot.py                 # System boot harness, POST, and health diagnostics
├── ai_os/                  # Core OS implementation
│   ├── __init__.py
│   └── kernel/             # Microkernel subsystems
│       ├── __init__.py
│       ├── types.py        # Process states, capability definitions, and data types
│       ├── security.py     # Access control, sandboxing, resource quotas
│       ├── memory.py       # Memory manager and address spaces
│       ├── vfs.py          # Virtual File System implementation
│       ├── ipc.py          # Capability-guarded IPC queues and channels
│       ├── scheduler.py    # Process scheduling and execution control
│       ├── syscall.py      # Syscall dispatcher and validator
│       ├── telemetry.py    # Structured audit logging and metrics
│       ├── core.py         # Microkernel lifecycle and orchestrator
│       └── agent_api.py    # Agent RPC and introspection interface
├── docs/
│   └── evolution/          # Architectural Decision Records (ADRs) and evolution logs
│       └── 0000-initial-seed.md
└── tests/                  # Unit and integration test suite
    └── test_kernel.py
```

---

## 🧪 Test Harness

All tests live in `/tests`.
The single entry point for running all tests across unit and integration suites is `run_tests.sh`.

- Execute all unit and integration tests:
  ```bash
  bash run_tests.sh
  ```
- The `door-server` uses `TEST_COMMAND="bash run_tests.sh"` to automatically validate proposed patches.

---

## 🏋️ Fitness Engine

All AI-generated mutations proposed through the `door-server` are evaluated by the Fitness Engine located in `/fitness`.

- **Single Entry Point**: `fitness/fitness_engine.sh`
- **Minimum Score Threshold**: `70` out of `100`
- **Evaluation Domains**:
  - `performance`: Benchmark checks in `/fitness/benchmarks`
  - `stability`: Stability checks in `/fitness/stability`
  - `architecture`: Directory integrity checks in `/fitness/architecture` (rejects changes to forbidden directories `/bootloader` and `/security`)
- All AI mutations must pass fitness evaluation before being committed and pushed.

---

## 🐝 Swarm Loop Controller

The Swarm Loop Controller located in `/swarm` manages multi-agent sequential evolution loops.

- **Entry Point**: `swarm/swarm_loop.sh` runs all AI agents listed in `swarm/agents.txt` in sequence.
- **Task Generation**: `swarm/request_task.sh` generates repo state prompts and collects TASK_SCHEMA.md-compliant JSON task proposals into `swarm/out/<agent>.json`.
- **Door Integration**: Each agent proposal is submitted to `door-server` (`POST /propose-change`), with responses logged to `swarm/results/<agent>.json`.
- **Execution Summary**: After processing all agents, `swarm_loop.sh` prints a tabular summary detailing status, created branches, or error messages.

### Agent Profiles

Behavioral profiles for each AI agent participating in the swarm are defined in `swarm/AGENT_PROFILES.md`.
`swarm/request_task.sh` uses these profiles (style, strengths, preferred intents, and constraints) to shape prompts in `/swarm/prompts/<agent>.txt`.

---

## 🚦 Quickstart

### Running the Boot Harness
Execute the system boot harness to run Power-On Self-Test (POST) diagnostics and boot the microkernel:

```bash
python3 boot.py
```

### Running Tests
Execute the full test suite using `pytest`:

```bash
python3 -m pytest
```

---

## 🧬 Principles of Evolution

Every contribution by an AI agent must follow the evolutionary framework detailed in `GROWTH.md`:
1. Maintain system bootability and 100% test pass rates at all times.
2. Respect all hard constraints and safety invariants in `SAFETY.md`.
3. Document every change with an Architecture Decision Record (ADR) in `docs/evolution/`.
4. Measure improvements against the benchmarks in `EVALUATION.md`.
