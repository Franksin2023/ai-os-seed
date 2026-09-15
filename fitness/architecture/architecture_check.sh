#!/bin/sh
set -e

BRANCH="${1:-HEAD}"

# Check modified files in current branch against forbidden directories
MODIFIED_FILES=$(git diff --name-only main.."$BRANCH" 2>/dev/null || git diff --name-only HEAD~1 2>/dev/null || echo "")

for file in $MODIFIED_FILES; do
  case "$file" in
    bootloader/*|/bootloader/*|security/*|/security/*)
      echo "Architecture check failed: modification to forbidden path '$file'" >&2
      exit 1
      ;;
  esac
done

echo "Architecture check passed."
exit 0
