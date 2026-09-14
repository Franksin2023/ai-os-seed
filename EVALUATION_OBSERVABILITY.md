# Evaluation Dimension: Kernel Observability Score

## Purpose
This evaluation dimension measures how effectively the microkernel exposes internal state, scheduling behavior, memory usage, and capability interactions to agents.
Higher observability enables better debugging, optimization, and evolutionary adaptation.

## Metrics

### 1. Telemetry Coverage Ratio (TCR)
Measures how many kernel subsystems emit structured telemetry events.

TCR = (subsystems_with_telemetry / total_subsystems)

### 2. Event Granularity Quality (EGQ)
Evaluates how detailed each telemetry event is.

EGQ = average(event_detail_score)

### 3. Introspection Latency (IL)
Measures how quickly agents can retrieve kernel state via the AgentAPI.

IL = average(introspection_request_time_ms)

### 4. Memory Visibility Completeness (MVC)
Indicates how much of the virtual memory subsystem is observable without violating isolation guarantees.

MVC = (observable_memory_fields / total_memory_fields)

## Combined Observability Score (COS)
COS = (0.4 * TCR) + (0.3 * EGQ) + (0.2 * (1 - IL_normalized)) + (0.1 * MVC)

Higher scores indicate more transparent and introspectable kernel behavior.

## Agent Guidance
Agents may evolve:
- richer telemetry events
- lower‑latency introspection endpoints
- improved memory visibility models
- capability‑aware observability hooks
- scheduler event streams
- VFS operation traces

All improvements must satisfy:
- SAFETY.md
- GROWTH.md
- EVALUATION.md
- POST diagnostics
- isolation guarantees

## Output Format
Agents must output a JSON object:

```json
{
  "tcr": 0.0,
  "egq": 0.0,
  "il": 0.0,
  "mvc": 0.0,
  "cos": 0.0
}
```
