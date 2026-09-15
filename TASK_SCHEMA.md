# AI Task Schema

All AI agents must submit tasks using the following JSON structure. This schema ensures consistent communication between agents and the door-server.

## Required JSON Structure

```json
{
  "description": "Short summary of the change or improvement",
  "intent": "Purpose of the change (e.g. fix, refactor, optimize, add-feature)",
  "targets": ["list", "of", "files", "or", "modules"],
  "constraints": ["optional", "rules", "or", "limits"],
  "diff": "Unified diff string following DIFF_SCHEMA.md"
}
```
