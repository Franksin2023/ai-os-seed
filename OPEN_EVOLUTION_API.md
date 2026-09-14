# Open Evolution API Specification

## Purpose
The Open Evolution API allows external agents to submit mutations, request evaluations, retrieve lineage data, and participate in evolutionary tournaments.
It exposes a controlled interface for interacting with the kernel evolution ecosystem while preserving safety, capability boundaries, and invariants.

## API Overview
The API is organized into four main categories:

1. Mutation Submission
2. Fitness Evaluation
3. Lineage Retrieval
4. Tournament Participation

All endpoints operate on JSON payloads and return structured responses.

---

## 1. Mutation Submission API

### Endpoint
`POST /api/evolution/mutate`

### Description
Submit a mutation proposal targeting a specific lineage.

### Payload
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
