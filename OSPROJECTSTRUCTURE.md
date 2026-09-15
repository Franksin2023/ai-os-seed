# OS Project Structure

This document defines the canonical directory layout for the evolving OS.
All agents must follow this structure when creating, modifying, or deleting files.

## Root Layout

/
├── kernel/               # Core OS kernel (scheduler, memory, IPC)
├── drivers/              # Hardware drivers (net, disk, input)
├── sys/                  # System utilities and core services
├── usr/                  # Userland programs and tools
├── lib/                  # Shared libraries
├── boot/                 # Bootloader, init, startup sequence
├── pkg/                  # Package manager + installable modules
├── docs/                 # Documentation
├── tests/                # Test harness + fitness evaluation
└── swarm/                # Swarm controller + agent prompts

## Directory Rules

### /kernel
- Contains core OS logic.
- Only Claude, Copilot, and Devin may modify kernel files.
- Gemini may propose optimisations but cannot modify kernel directly.
- Cursor may fix kernel bugs but must not change architecture.

### /drivers
- Contains hardware drivers.
- Any agent may add new drivers.
- Only Cursor and Devin may fix driver-level bugs.

### /sys
- Contains system services (init, logging, IPC daemons).
- Claude may refactor.
- Gemini may add experimental services.
- Copilot may clean up and stabilise.

### /usr
- Contains userland tools and programs.
- All agents may contribute freely.

### /lib
- Shared libraries used across the OS.
- Claude maintains architecture.
- Copilot ensures consistency.
- Gemini may add experimental libs.

### /boot
- Bootloader, init sequence.
- Gemini is forbidden from modifying /boot.
- Only Claude and Devin may modify boot code.

### /pkg
- Package manager and installable modules.
- Gemini may add new modules.
- Copilot ensures module consistency.
- Devin handles wiring and integration.

### /docs
- Documentation for the OS.
- Any agent may update docs.

### /tests
- Test harness + fitness engine.
- Only Copilot and Cursor may modify tests.
- All agents must ensure tests pass.

### /swarm
- Swarm loop controller.
- Agent prompts.
- Task schemas.
- Diff schemas.
- Fitness scoring.

## File Placement Rules

- New kernel features → /kernel
- New drivers → /drivers
- New system services → /sys
- New user tools → /usr
- New shared libs → /lib
- New boot logic → /boot
- New packages → /pkg
- New documentation → /docs
- New tests → /tests
- Swarm logic → /swarm

## Mutation Constraints

- Agents must not create files outside the defined directories.
- Agents must not modify .gitignore, LICENSE, or repo metadata.
- Agents must not modify swarm controller files unless explicitly instructed.
- Agents must keep diffs minimal and targeted.
- Agents must follow their profile constraints in AGENT_PROFILES.md.
