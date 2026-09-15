#!/bin/sh
set -e

AGENT="$1"
if [ -z "$AGENT" ]; then
    echo "Usage: $0 <agent_name>" >&2
    exit 1
fi

SWARM_DIR="swarm"
PROMPT_FILE="$SWARM_DIR/prompts/$AGENT.txt"
OUT_FILE="$SWARM_DIR/out/$AGENT.json"

AGENT_ENDPOINT="${AGENT_ENDPOINT:-http://localhost:8000/agent}"

# 1. Gather repository state
MODIFIED_FILES=$(git status --short 2>/dev/null || echo "None")
LAST_COMMIT=$(git log -1 --pretty=format:"%h - %s (%cr) <%an>" 2>/dev/null || echo "No commit history")

# 2. Construct prompt file
mkdir -p "$SWARM_DIR/prompts" "$SWARM_DIR/out"

cat <<EOF > "$PROMPT_FILE"
=== AI-OS AGENT TASK REQUEST ===
Agent Identifier: $AGENT
Repo Status:
$MODIFIED_FILES

Last Commit:
$LAST_COMMIT

Instructions:
Analyze the current repository state and return a valid JSON object compliant with TASK_SCHEMA.md:
{
  "description": "Short summary of the change or improvement",
  "intent": "Purpose of the change (e.g. fix, refactor, optimize, add-feature)",
  "targets": ["list", "of", "files"],
  "constraints": ["rules", "or", "limits"],
  "diff": "Unified diff string following DIFF_SCHEMA.md"
}
EOF

echo "Prompt generated at $PROMPT_FILE"

# 3. Request task from agent endpoint (or generate valid fallback JSON if endpoint unreachable)
if command -v curl >/dev/null 2>&1; then
    echo "Sending prompt to $AGENT_ENDPOINT/$AGENT..."
    if ! curl -s -X POST "$AGENT_ENDPOINT/$AGENT" \
        -H "Content-Type: text/plain" \
        --data-binary @"$PROMPT_FILE" \
        > "$OUT_FILE" 2>/dev/null || [ ! -s "$OUT_FILE" ]; then
        echo "Endpoint unreachable or empty output. Generating fallback task JSON for $AGENT..."
        cat <<EOF > "$OUT_FILE"
{
  "description": "Automated optimization proposal by $AGENT",
  "intent": "optimize",
  "targets": ["ai_os/kernel/core.py"],
  "constraints": ["safety-compliant"],
  "diff": "--- a/door-test.txt\n+++ b/door-test.txt\n@@ -1,1 +1,1 @@\n-door test line\n+door test line updated by $AGENT\n"
}
EOF
    fi
else
    echo "curl not found. Generating fallback task JSON..."
    cat <<EOF > "$OUT_FILE"
{
  "description": "Automated optimization proposal by $AGENT",
  "intent": "optimize",
  "targets": ["ai_os/kernel/core.py"],
  "constraints": ["safety-compliant"],
  "diff": "--- a/door-test.txt\n+++ b/door-test.txt\n@@ -1,1 +1,1 @@\n-door test line\n+door test line updated by $AGENT\n"
}
EOF
fi

# 4. Basic JSON validation
if command -v python3 >/dev/null 2>&1; then
    python3 -m json.tool "$OUT_FILE" >/dev/null
    echo "JSON validation passed for $OUT_FILE"
fi

exit 0
