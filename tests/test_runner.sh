#!/bin/sh

FAILED=0

run_suite() {
    DIR="$1"
    SUITE_NAME="$2"
    echo "=== Running $SUITE_NAME tests ==="
    if [ -d "$DIR" ]; then
        for test_script in "$DIR"/*.sh; do
            if [ -x "$test_script" ]; then
                echo "Running $test_script..."
                if "$test_script"; then
                    echo "PASS: $test_script"
                else
                    echo "FAIL: $test_script"
                    FAILED=1
                fi
            fi
        done
    fi
}

run_suite "tests/unit" "Unit"
run_suite "tests/integration" "Integration"

if [ $FAILED -ne 0 ]; then
    echo "Test suite failed."
    exit 1
fi

echo "All test suites passed cleanly."
exit 0
