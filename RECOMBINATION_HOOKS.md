# Recombination Hooks Specification

## Purpose
Recombination hooks allow agents to combine traits from multiple kernel lineages into new descendants.
This introduces structured innovation beyond simple mutation, enabling major architectural leaps while preserving safety and invariants.

## Recombination Model

### 1. Parent Selection
Recombination operates on two or more parent lineages:

- `parent_a_id`
- `parent_b_id`
- (optional) additional parents

Parents are selected based on:
- tournament performance
- fitness scores
- diversity metrics

### 2. Trait Categories
Recombination can operate on the following trait categories:

- scheduler configuration
- memory model parameters
- capability system rules
- observability/telemetry configuration
- HAL/driver configuration
- VFS behaviour

Each trait category is recombined independently.

### 3. Recombination Strategies

Examples:

- **Weighted Merge**
  Combine parameters using fitness‑weighted averages.

- **Segment Swap**
  Take scheduler traits from parent A, memory traits from parent B.

- **Dominant Parent**
  Use parent A as base, selectively override traits with parent B.

All strategies must be deterministic and logged.

### 4. Recombination API

Agents propose recombination as:

```json
{
  "parents": ["lineage-a", "lineage-b"],
  "strategy": "segment_swap",
  "trait_categories": ["scheduler", "memory"]
}
```
