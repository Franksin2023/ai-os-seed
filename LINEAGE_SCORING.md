# Lineage Scoring Specification

## Purpose
Lineage scoring provides a competitive ranking system for evolved kernel variants.
Each lineage receives a score based on performance, fairness, observability, stability, and mutation quality.
This encourages agents to produce high‑quality, multi‑dimensional improvements.

## Scoring Dimensions

### 1. Performance Score (PS)
Derived from:
- latency benchmarks
- memory efficiency
- IPC throughput
- scheduler responsiveness

PS = weighted_performance_metrics

### 2. Fairness Score (FS)
Imported from `EVALUATION_SCHEDULER.md`:
- TSU
- SI
- PDS
- CFS

FS = CFS

### 3. Observability Score (OS)
Imported from `EVALUATION_OBSERVABILITY.md`:
- TCR
- EGQ
- IL
- MVC
- COS

OS = COS

### 4. Stability Score (SS)
Measures:
- regression incidence
- invariant violations
- crash frequency
- test suite pass rate

SS = 1 - regression_rate_normalized

### 5. Mutation Quality Score (MQS)
Evaluates:
- safety compliance
- capability boundary adherence
- mutation hook correctness
- proposal validation success rate

MQS = validated_mutations / total_mutations

## Combined Lineage Score (CLS)

CLS = (0.3 * PS) + (0.25 * FS) + (0.25 * OS) + (0.15 * SS) + (0.05 * MQS)

Higher scores indicate stronger evolutionary fitness.

## Lineage Ranking

Lineages are ranked globally:

1. Highest CLS
2. Lowest regression rate
3. Highest mutation‑validation ratio
4. Most recent successful evolution event

Rankings are published in:

`docs/evolution/lineage_ranking.json`

## Agent Output Format

Agents must output:

```json
{
  "ps": 0.0,
  "fs": 0.0,
  "os": 0.0,
  "ss": 0.0,
  "mqs": 0.0,
  "cls": 0.0
}
```
