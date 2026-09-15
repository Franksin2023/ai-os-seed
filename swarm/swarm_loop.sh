#!/bin/sh

SWARM_DIR="swarm"
AGENTS_FILE="$SWARM_DIR/agents.txt"
DOOR_SERVER="${DOOR_SERVER:-http://localhost:3000}"
DOOR_TOKEN="${DOOR_TOKEN:-yourtoken}"

mkdir -p "$SWARM_DIR/out" "$SWARM_DIR/results" "$SWARM_DIR/prompts"

if [ ! -f "$AGENTS_FILE" ]; then
    echo "Agents list not found at $AGENTS_FILE" >&2
    exit 1
fi

echo "=== Starting Swarm Controller Loop ==="

AGENTS=""
while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines or comments
    clean_line=$(echo "$line" | tr -d '\r' | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
    case "$clean_line" in
        ''|\#*) continue ;;
        *) AGENTS="$AGENTS $clean_line" ;;
    esac
done < "$AGENTS_FILE"

for AGENT in $AGENTS; do
    echo ""
    echo "------------------------------------------------------------"
    echo "Processing Agent: $AGENT"
    echo "------------------------------------------------------------"

    # 1. Request task from agent
    if [ -x "$SWARM_DIR/request_task.sh" ]; then
        "$SWARM_DIR/request_task.sh" "$AGENT"
    else
        sh "$SWARM_DIR/request_task.sh" "$AGENT"
    fi

    OUT_JSON="$SWARM_DIR/out/$AGENT.json"
    RESULT_JSON="$SWARM_DIR/results/$AGENT.json"

    if [ ! -f "$OUT_JSON" ]; then
        echo "{\"status\":\"failed\",\"error\":\"task output JSON not produced\"}" > "$RESULT_JSON"
        continue
    fi

    # 2. Forward payload to door-server
    echo "Submitting task to door-server at $DOOR_SERVER/propose-change..."
    if command -v curl >/dev/null 2>&1; then
        HTTP_CODE=$(curl -s -o "$RESULT_JSON" -w "%{http_code}" -X POST "$DOOR_SERVER/propose-change" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $DOOR_TOKEN" \
            -d @"$OUT_JSON" 2>/dev/null || echo "000")

        if [ "$HTTP_CODE" = "000" ]; then
            cat <<EOF > "$RESULT_JSON"
{
  "status": "failed",
  "error": "Door server connection failed (unreachable at $DOOR_SERVER)"
}
EOF
        fi
    else
        echo "{\"status\":\"failed\",\"error\":\"curl command not available\"}" > "$RESULT_JSON"
    fi
done

echo ""
echo "============================================================"
echo "               SWARM LOOP EXECUTION SUMMARY                 "
echo "============================================================"
printf "%-12s | %-8s | %-28s | %s\n" "AGENT" "STATUS" "BRANCH" "ERROR"
echo "------------------------------------------------------------"

for AGENT in $AGENTS; do
    RESULT_JSON="$SWARM_DIR/results/$AGENT.json"
    STATUS="UNKNOWN"
    BRANCH="N/A"
    ERR_MSG="N/A"

    if [ -f "$RESULT_JSON" ] && command -v python3 >/dev/null 2>&1; then
        STATUS=$(python3 -c "import json, sys; data=json.load(open('$RESULT_JSON')); print(data.get('status', 'failed'))" 2>/dev/null || echo "failed")
        BRANCH=$(python3 -c "import json, sys; data=json.load(open('$RESULT_JSON')); print(data.get('branch', 'N/A'))" 2>/dev/null || echo "N/A")
        ERR_MSG=$(python3 -c "import json, sys; data=json.load(open('$RESULT_JSON')); print(data.get('error', 'N/A'))" 2>/dev/null || echo "N/A")
    fi

    printf "%-12s | %-8s | %-28s | %s\n" "$AGENT" "$STATUS" "$BRANCH" "$ERR_MSG"
done

echo "============================================================"
exit 0
