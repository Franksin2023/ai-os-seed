# Mutation Operators Specification

## Purpose
Mutation operators define controlled transformations that agents can apply to kernel lineages.
They introduce structured variation while preserving safety, capability boundaries, and kernel invariants.

## Operator Categories

### 1. Scheduler Mutation Operators
Controlled changes to scheduling behaviour.

Examples:
- adjust time slice granularity
- modify priority weighting
- change fairness heuristics (TSU, SI, PDS, CFS)
- alter queueing strategy (FIFO, priority, hybrid)

Constraints:
- must not violate fairness invariants
- must not starve critical tasks
- must preserve isolation guarantees

### 2. Memory Model Mutation Operators
Controlled changes to memory handling.

Examples:
- adjust allocation strategies
- tune fragmentation thresholds
- modify paging behaviour
- refine capability‑based access rules

Constraints:
- must not break capability isolation
- must not allow unauthorized access
- must preserve invariant: no cross‑lineage memory leaks

### 3. Observability Mutation Operators
Controlled changes to telemetry and introspection.

Examples:
- add/remove metrics
- change sampling rates
- refine event aggregation
- adjust logging verbosity

Constraints:
- must not disable critical safety telemetry
- must not introduce unbounded logging
- must preserve introspection availability

### 4. Capability System Mutation Operators
Controlled changes to capability boundaries.

Examples:
- refine capability classes
- adjust permission scopes
- modify escalation rules
- tune default capability sets

Constraints:
- must not allow privilege escalation
- must not weaken isolation
- must preserve core security invariants

### 5. HAL & Driver Mutation Operators
Controlled changes to hardware abstraction and drivers.

Examples:
- adjust initialization sequences
- tune timeouts and retries
- refine device capability detection
- optimize minimal driver stacks

Constraints:
- must not break boot path
- must not corrupt device state
- must preserve minimal operability

## Operator Application Model

Agents propose mutations as:

```json
{
  "lineage_id": "kernel-lineage-001",
  "operator_category": "scheduler",
  "operator_name": "adjust_priority_weighting",
  "parameters": {
    "high_priority_weight": 1.2,
    "low_priority_weight": 0.8
  }
}
```
