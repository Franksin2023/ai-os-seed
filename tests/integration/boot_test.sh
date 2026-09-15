#!/bin/sh
set -e

if [ ! -f "boot/main.c" ]; then
    echo "FAIL: boot/main.c does not exist" >&2
    exit 1
fi

CC=${CC:-gcc}
if ! command -v "$CC" >/dev/null 2>&1; then
    CC=clang
fi

if ! "$CC" -c boot/main.c -o /tmp/boot_test.o 2>/dev/null; then
    echo "FAIL: boot/main.c failed to compile" >&2
    exit 1
fi

rm -f /tmp/boot_test.o
echo "PASS: boot_test.sh"
exit 0
