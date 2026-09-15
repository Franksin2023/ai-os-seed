#!/usr/bin/env bash

SWARM_DIR="swarm"
DOOR_SERVER="${DOOR_SERVER:-http://localhost:3000}"
DOOR_TOKEN="${DOOR_TOKEN:-yourtoken}"
OUT_DIR="$SWARM_DIR/output"

mkdir -p "$SWARM_DIR/out" "$SWARM_DIR/results" "$SWARM_DIR/prompts" "$OUT_DIR"

AGENTS=("Claude" "Gemini" "Copilot" "DeepSeek" "Devin" "Cursor")

echo "=== Starting Swarm Controller Loop ==="

for AGENT in "${AGENTS[@]}"; do
    echo "Running agent: $AGENT"

    bash "$SWARM_DIR/request_task.sh" "$AGENT"

    DIFF_FILE="$OUT_DIR/$AGENT.diff"
    DESC_FILE="$OUT_DIR/$AGENT.json"
    RESULT_FILE="$SWARM_DIR/results/$AGENT.json"

    if [ ! -f "$DIFF_FILE" ] || [ ! -f "$DESC_FILE" ]; then
        echo "{\"status\":\"failed\",\"error\":\"Output diff or description not produced\"}" > "$RESULT_FILE"
        continue
    fi

    # Format JSON payload safely with python if available
    PAYLOAD_FILE="$SWARM_DIR/out/${AGENT}_payload.json"
    if command -v python3 >/dev/null 2>&1; then
        python3 -c "import json; desc=open('$DESC_FILE').read().strip(); diff=open('$DIFF_FILE').read(); json.dump({'description': desc, 'diff': diff}, open('$PAYLOAD_FILE', 'w'))"
    else
        DESCRIPTION=$(cat "$DESC_FILE")
        DIFF=$(cat "$DIFF_FILE")
        cat <<EOF > "$PAYLOAD_FILE"
{
  "description": "$DESCRIPTION",
  "diff": "$DIFF"
}
EOF
    fi

    echo "Submitting $AGENT proposal to door-server at $DOOR_SERVER/propose-change..."
    if command -v curl >/dev/null 2>&1; then
        HTTP_CODE=$(curl -s -o "$RESULT_FILE" -w "%{http_code}" -X POST "$DOOR_SERVER/propose-change" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $DOOR_TOKEN" \
            -d @"$PAYLOAD_FILE" 2>/dev/null || echo "000")

        if [ "$HTTP_CODE" = "000" ]; then
            cat <<EOF > "$RESULT_FILE"
{
  "status": "failed",
  "error": "Door server connection failed (unreachable at $DOOR_SERVER)"
}
EOF
        fi
    else
        echo "{\"status\":\"failed\",\"error\":\"curl command not available\"}" > "$RESULT_FILE"
    fi
done

echo ""
echo "============================================================"
echo "               SWARM LOOP EXECUTION SUMMARY                 "
echo "============================================================"
printf "%-12s | %-8s | %-28s | %s\n" "AGENT" "STATUS" "BRANCH" "ERROR"
echo "------------------------------------------------------------"

for AGENT in "${AGENTS[@]}"; do
    RESULT_FILE="$SWARM_DIR/results/$AGENT.json"
    STATUS="UNKNOWN"
    BRANCH="N/A"
    ERR_MSG="N/A"

    if [ -f "$RESULT_FILE" ] && command -v python3 >/dev/null 2>&1; then
        STATUS=$(python3 -c "import json; data=json.load(open('$RESULT_FILE')); print(data.get('status', 'failed'))" 2>/dev/null || echo "failed")
        BRANCH=$(python3 -c "import json; data=json.load(open('$RESULT_FILE')); print(data.get('branch', 'N/A'))" 2>/dev/null || echo "N/A")
        ERR_MSG=$(python3 -c "import json; data=json.load(open('$RESULT_FILE')); print(data.get('error', 'N/A'))" 2>/dev/null || echo "N/A")
    fi

    printf "%-12s | %-8s | %-28s | %s\n" "$AGENT" "$STATUS" "$BRANCH" "$ERR_MSG"
done

echo "============================================================"
exit 0
