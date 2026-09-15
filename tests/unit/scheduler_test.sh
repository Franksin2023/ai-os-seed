#!/bin/sh
set -e

if [ ! -f "kernel/scheduler.c" ]; then
    echo "FAIL: kernel/scheduler.c does not exist" >&2
    exit 1
fi

CC=${CC:-gcc}
if ! command -v "$CC" >/dev/null 2>&1; then
    CC=clang
fi

if ! "$CC" -c kernel/scheduler.c -o /tmp/scheduler_test.o 2>/dev/null; then
    echo "FAIL: kernel/scheduler.c failed to compile" >&2
    exit 1
fi

rm -f /tmp/scheduler_test.o
echo "PASS: scheduler_test.sh"
exit 0
