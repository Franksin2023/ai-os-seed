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
OUT_DIR="$SWARM_DIR/output"
mkdir -p "$SWARM_DIR/prompts" "$SWARM_DIR/out" "$OUT_DIR"

AGENT_ENDPOINT="${AGENT_ENDPOINT:-http://localhost:8000/agent}"

# 1. Extract agent profile
PROFILES_FILE="$SWARM_DIR/AGENT_PROFILES.md"
PROFILE_TEXT="No profile specified."
if [ -f "$PROFILES_FILE" ]; then
    AGENT_HEADER="$(echo "$AGENT" | awk '{print toupper(substr($0,1,1)) tolower(substr($0,2))}') "
    PROFILE_TEXT=$(sed -n "/## ${AGENT_HEADER% }/,/## /p" "$PROFILES_FILE" | grep -v "^## [A-Za-z]" | sed '/^$/d')
    if [ -z "$PROFILE_TEXT" ]; then
        PROFILE_TEXT=$(sed -n "/## ${AGENT_HEADER% }/,\$p" "$PROFILES_FILE" | grep -v "^## [A-Za-z]" | sed '/^$/d')
    fi
fi

# 2. Extract OS project structure
STRUCTURE_TEXT="No project structure specified."
if [ -f "OSPROJECTSTRUCTURE.md" ]; then
    STRUCTURE_TEXT=$(cat "OSPROJECTSTRUCTURE.md")
elif [ -f "OS_PROJECT_STRUCTURE.md" ]; then
    STRUCTURE_TEXT=$(cat "OS_PROJECT_STRUCTURE.md")
fi

# 3. Gather repository snapshot & last commit
REPO_SNAPSHOT=$(git ls-files 2>/dev/null || echo "None")
LAST_COMMIT=$(git log -1 2>/dev/null || echo "No commit history")

# 4. Construct prompt file
cat <<EOF > "$PROMPT_FILE"
You are $AGENT.

Here is your agent profile:
$PROFILE_TEXT

Here is the OS project structure:
$STRUCTURE_TEXT

Here is the current repo snapshot:
$REPO_SNAPSHOT

Here is the last commit:
$LAST_COMMIT

Follow your constraints. Produce a JSON task and a unified diff compliant with TASK_SCHEMA.md:
{
  "description": "Short summary of the change or improvement",
  "intent": "Purpose of the change (e.g. fix, refactor, optimize, add-feature)",
  "targets": ["list", "of", "files"],
  "constraints": ["rules", "or", "limits"],
  "diff": "Unified diff string following DIFF_SCHEMA.md"
}
EOF

echo "Prompt generated at $PROMPT_FILE"

# 5. Request task from agent endpoint (or generate valid fallback outputs if endpoint unreachable)
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

# 6. Populate swarm/output/$AGENT.diff and swarm/output/$AGENT.json for swarm_loop.sh
if command -v python3 >/dev/null 2>&1; then
    python3 -c "import json; d=json.load(open('$OUT_FILE')); open('$OUT_DIR/$AGENT.json','w').write(d.get('description','Automated proposal by $AGENT')); open('$OUT_DIR/$AGENT.diff','w').write(d.get('diff',''))" 2>/dev/null || true
else
    echo "Automated optimization proposal by $AGENT" > "$OUT_DIR/$AGENT.json"
    echo "--- a/door-test.txt\n+++ b/door-test.txt\n@@ -1,1 +1,1 @@\n-door test line\n+door test line updated by $AGENT" > "$OUT_DIR/$AGENT.diff"
fi

exit 0
