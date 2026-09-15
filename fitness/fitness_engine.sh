#!/bin/sh

REPO_PATH="${1:-$REPO_PATH}"
REPO_PATH="${REPO_PATH:-.}"
BRANCH="${2:-HEAD}"

PERF_STATUS="pass"
STABILITY_STATUS="pass"
ARCH_STATUS="pass"
SCORE=100

if [ -x "$REPO_PATH/fitness/benchmarks/perf_check.sh" ]; then
  if ! "$REPO_PATH/fitness/benchmarks/perf_check.sh"; then
    PERF_STATUS="fail"
    SCORE=$((SCORE - 35))
  fi
else
  PERF_STATUS="fail"
  SCORE=$((SCORE - 35))
fi

if [ -x "$REPO_PATH/fitness/stability/stability_check.sh" ]; then
  if ! "$REPO_PATH/fitness/stability/stability_check.sh"; then
    STABILITY_STATUS="fail"
    SCORE=$((SCORE - 35))
  fi
else
  STABILITY_STATUS="fail"
  SCORE=$((SCORE - 35))
fi

if [ -x "$REPO_PATH/fitness/architecture/architecture_check.sh" ]; then
  if ! "$REPO_PATH/fitness/architecture/architecture_check.sh" "$BRANCH"; then
    ARCH_STATUS="fail"
    SCORE=$((SCORE - 35))
  fi
else
  ARCH_STATUS="fail"
  SCORE=$((SCORE - 35))
fi

if [ $SCORE -lt 0 ]; then
  SCORE=0
fi

cat <<EOF
{
  "score": $SCORE,
  "performance": "$PERF_STATUS",
  "stability": "$STABILITY_STATUS",
  "architecture": "$ARCH_STATUS"
}
EOF

if [ $SCORE -ge 70 ]; then
  exit 0
else
  exit 1
fi
