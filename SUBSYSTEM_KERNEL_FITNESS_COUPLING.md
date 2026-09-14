# Subsystem–Kernel Fitness Coupling Specification

## Purpose
Couple emergent subsystem fitness (scheduler, memory, VFS, HAL, runtime) directly into kernel lineage fitness and survival.
This ensures that evolved subsystem traits materially affect which lineages live, die, and dominate.

## 1. Fitness Aggregation Model

Each lineage’s fitness becomes a weighted aggregate of:

- core kernel fitness (`fit_core`)
- scheduler fitness (`fit_sched`)
- memory fitness (`fit_mem`)
- VFS fitness (`fit_vfs`)
- HAL fitness (`fit_hal`)
- runtime fitness (`fit_rt`)

Example aggregation:

`fit_total = ( 0.30 * fit_core + 0.15 * fit_sched + 0.15 * fit_mem + 0.15 * fit_vfs + 0.15 * fit_hal + 0.10 * fit_rt )`

Weights are stored in:

`docs/evolution/fitness_weights.json`

## 2. Subsystem Fitness Hooks

Each emergent subsystem exposes a `compute_fitness()` hook:

- `EmergentScheduler.compute_fitness(metrics) -> float`
- `EmergentMemoryModel.compute_fitness(metrics) -> float`
- `EmergentVFS.compute_fitness(metrics) -> float`
- `EmergentHAL.compute_fitness(metrics) -> float`
- `EmergentRuntime.compute_fitness(metrics) -> float`

Metrics are collected from telemetry and kernel behaviour.

## 3. Tournament Integration

Kernel tournaments now:

- read subsystem fitness values per lineage
- compute `fit_total` using the aggregation model
- rank lineages by `fit_total`
- eliminate low‑fitness lineages
- promote high‑fitness lineages

Subsystem performance directly affects tournament outcomes.

## 4. Pressure Integration

Evolutionary pressure cycles apply to coupled fitness:

- fitness decay affects `fit_total`
- mutation quotas target low‑fitness subsystems
- recombination is biased toward high‑fitness subsystem traits
- extinction events remove lineages with persistently low `fit_total`

Pressure now acts on the whole organism, not just isolated parts.

## 5. Logging

Coupled fitness is logged per cycle:

```json
{
  "lineage_id": "kernel-lineage-001",
  "fit_core": 0.78,
  "fit_sched": 0.81,
  "fit_mem": 0.74,
  "fit_vfs": 0.79,
  "fit_hal": 0.72,
  "fit_rt": 0.76,
  "fit_total": 0.77,
  "cycle": 42
}
```

Stored in: `docs/evolution/fitness_coupling_log.json`

## Notes
Subsystem–kernel fitness coupling turns the OS from a set of evolving components into a single evolving organism.
Lineage survival now depends on coherent, high‑fitness architecture across all emergent subsystems.
You’ve just wired the whole thing together—now evolution selects *architectures*, not just code.
