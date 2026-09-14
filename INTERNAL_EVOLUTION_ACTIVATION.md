# Internal Evolution Activation Specification

## Purpose
Activate internal, Jules-driven evolution of kernel lineages using the existing mutation, recombination, tournament, fitness, and pressure systems.
This defines how Jules acts as the first evolutionary agent inside the AI-OS microkernel seed.

## Role: Jules as Internal Evolution Agent

Jules is authorized to:
- propose mutations via mutation operators
- initiate recombination via recombination hooks
- enroll lineages into tournaments
- respond to evolutionary pressure cycles
- update fitness scores
- record evolution telemetry

All actions must respect:
- SAFETY.md invariants
- capability boundaries
- evaluation rules

---

## 1. Internal Evolution Loop

The internal evolution loop runs as a recurring process:

1. **Read pressure state**
   - check current cycle (light / moderate / heavy)
   - read mutation quotas
   - read diversity metrics

2. **Select candidate lineages**
   - high-fitness survivors
   - recent champions
   - diverse outliers

3. **Apply mutations**
   - use mutation operators on selected lineages
   - ensure safety validation passes
   - log all mutations

4. **Trigger recombination (if needed)**
   - if diversity < threshold or fitness stagnates:
     - recombine traits from multiple parents
     - create new descendant lineages
     - record ancestry

5. **Run tournaments**
   - enroll candidate lineages
   - execute configured rounds
   - update scores
   - eliminate low performers
   - promote champions

6. **Update fitness landscape**
   - recalculate fitness for all active lineages
   - apply fitness decay
   - store updated scores

7. **Log evolution telemetry**
   - mutations
   - recombinations
   - tournament results
   - fitness changes
   - extinction events (if any)

---

## 2. Activation Entry Point

Add an internal evolution harness:

- file: `evolution_internal.py`
- function: `run_internal_evolution_cycle()`

This function:
- reads pressure configuration
- executes one full evolution loop
- writes logs to `docs/evolution/pressure_log.json` and `docs/evolution/tournament_scores.json`

---

## 3. Safety & Control

Internal evolution must:
- never bypass safety checks
- never modify SAFETY.md, GROWTH.md, or core invariants
- respect resource limits
- keep all changes observable via telemetry

If any evolution step fails validation:
- the step is aborted
- the lineage is not updated
- the event is logged as a safety violation

---

## Notes
Internal evolution activation turns the AI-OS microkernel seed from a static evolutionary framework into a live, Jules-driven evolutionary system.
Once stable, external agents may be allowed to participate via the Open Evolution API.
