# Evolutionary Tournaments Specification

## Purpose
Evolutionary tournaments create structured competition between kernel lineages.
Each tournament round evaluates multiple lineages across the fitness landscape, eliminating weaker variants and promoting stronger ones.
This accelerates the emergence of usable operating system behaviours.

## Tournament Structure

### 1. Round Initialization
Each round begins by selecting a set of candidate lineages from:
- recent mutation outputs
- high‑fitness survivors
- experimental branches
- recombination events

Candidates are loaded into the tournament pool.

### 2. Challenge Set
Each round consists of standardized challenges:

#### Performance Challenge
Measures:
- scheduler latency
- IPC throughput
- memory efficiency

#### Stability Challenge
Measures:
- crash frequency
- invariant violations
- regression rate

#### Observability Challenge
Measures:
- telemetry completeness
- introspection latency
- event stream quality

#### Fairness Challenge
Measures:
- TSU
- SI
- PDS
- CFS

#### Boot & HAL Challenge
Measures:
- boot path correctness
- HAL initialization
- driver compatibility (minimal set)

### 3. Scoring
Each lineage receives a tournament score:

TS = (0.25 * Performance) +
     (0.25 * Stability) +
     (0.20 * Observability) +
     (0.20 * Fairness) +
     (0.10 * Boot/HAL)

Tournament scores are recorded in:

`docs/evolution/tournament_scores.json`

### 4. Elimination
Lineages below the median TS are eliminated from the pool.

Eliminated lineages are logged in:

`docs/evolution/eliminated_lineages.json`

### 5. Advancement
Top‑scoring lineages advance to the next round.

Advancing lineages are logged in:

`docs/evolution/advancing_lineages.json`

### 6. Champion Selection
After N rounds (default: 10), the highest‑scoring lineage is declared the tournament champion.

Champions are recorded in:

`docs/evolution/tournament_champions.json`

## Agent Workflow

1. Agent submits mutation proposals.
2. Proposals generate new lineages.
3. Lineages enter tournament rounds.
4. Tournament challenges evaluate fitness.
5. Weak lineages are eliminated.
6. Strong lineages advance.
7. Champion lineage becomes the dominant kernel variant.

## Notes
Evolutionary tournaments accelerate the emergence of usable operating system behaviours by applying structured competitive pressure across multiple axes of fitness.
