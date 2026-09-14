# Evaluation Dimension: Scheduler Fairness Score

## Purpose
This evaluation dimension measures how fairly the microkernel scheduler allocates CPU time across competing agent processes.
Agents may evolve new scheduling algorithms to improve fairness, reduce starvation, and optimize cooperative multitasking.

## Metrics

### 1. Time Slice Distribution Uniformity (TSU)
Measures how evenly CPU time is distributed across all runnable processes.

Formula:
TSU = 1 - (variance(time_slices) / max_variance)

### 2. Starvation Incidence (SI)
Counts how many processes receive zero CPU time within a scheduling window.

SI = number_of_starved_processes

### 3. Priority Drift Stability (PDS)
Measures how stable priority levels remain over time without collapsing into unfair bias.

PDS = 1 - (priority_drift / max_drift)

## Combined Fairness Score (CFS)
The final score is a weighted combination of the three metrics:

CFS = (0.5 * TSU) + (0.3 * PDS) + (0.2 * (1 - SI_normalized))

Higher scores indicate more fair scheduling behavior.

## Agent Guidance
Agents may evolve:
- new scheduling algorithms
- improved priority heuristics
- adaptive time slicing
- starvation prevention mechanisms
- fairness‑aware IPC patterns

All evolved schedulers must pass:
- SAFETY.md
- GROWTH.md
- EVALUATION.md
- existing test suites
- POST diagnostics

## Output Format
Agents must output a JSON object:

```json
{
  "tsu": 0.0,
  "si": 0,
  "pds": 0.0,
  "cfs": 0.0
}
```
