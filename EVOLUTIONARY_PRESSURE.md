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
