# Evolutionary Pressure Orchestration Specification

## Purpose
Evolutionary pressure orchestration provides the continuous forces that drive mutation, competition, recombination, and lineage turnover.
Without pressure, the ecosystem remains static. With pressure, kernel evolution becomes dynamic, adaptive, and self‑sustaining.

## Pressure Components

### 1. Pressure Cycles
Pressure cycles run at defined intervals:

- hourly cycles (light pressure)
- daily cycles (moderate pressure)
- weekly cycles (heavy pressure)

Each cycle triggers:
- minimum mutation quotas
- tournament scheduling
- recombination checks
- fitness decay updates

### 2. Fitness Decay
Lineages lose fitness over time unless they:
- mutate
- recombine
- win tournaments

Decay formula:
`decayed_fitness = current_fitness * (1 - decay_rate ^ time_since_last_activity)`

Decay prevents stagnation and forces continuous improvement.

### 3. Diversity Enforcement
To avoid monoculture collapse, diversity is monitored:

- if diversity < threshold:
  - trigger recombination events
  - spawn exploratory mutations
  - introduce random challenge variants

### 4. Mutation Quotas
Each cycle enforces minimum mutation activity:

- light cycle: 2 mutations
- moderate cycle: 5 mutations
- heavy cycle: 10 mutations

If quotas are unmet:
- forced mutation events occur
- low‑activity lineages lose additional fitness

### 5. Tournament Cadence
Tournaments run automatically:

- light cycle: none
- moderate cycle: 1 round
- heavy cycle: 3 rounds

Tournament winners gain:
- fitness boosts
- priority in recombination
- survival guarantees

Losers face:
- elimination
- fitness penalties

### 6. Recombination Triggers
Recombination occurs when:

- diversity drops
- fitness stagnates
- mutation activity slows
- tournament winners dominate too strongly

Recombination merges traits from multiple parents to create innovative descendants.

### 7. Extinction Events
Rare events (default: every 100 cycles):

- eliminate bottom 20% of lineages
- reset fitness decay
- introduce new challenge sets

Extinction prevents long‑term stagnation.

### 8. Pressure Telemetry
All pressure events are logged:

- cycle start/end
- mutation quotas
- recombination triggers
- tournament rounds
- fitness decay
- extinction events

Logs stored in:
`docs/evolution/pressure_log.json`

## Notes
Evolutionary pressure orchestration is the heartbeat of the ecosystem.
It ensures continuous adaptation, innovation, and competition, enabling the emergence of high‑fitness kernel lineages and ultimately a usable AI‑evolved operating system.
