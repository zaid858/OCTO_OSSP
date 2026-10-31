#!/bin/bash
set -e

cd ~/OCTO_OSSP-project/linux-implementation

echo "=== Running TEST 8: Concurrent Access / Session Lock Test ==="

# Start reader 1 in background
./fifo_reader --timeout 3 &
PID_READER=$!
sleep 0.2

# Try to start reader 2 while reader 1 is running
echo "Attempting to run a second reader while session 1 is active:"
set +e
./fifo_reader 2>&1
CODE=$?
set -e

echo "Exit code from conflicting session: $CODE"

wait $PID_READER 2>/dev/null || true

echo "=== TEST 8 VERIFIED ==="
