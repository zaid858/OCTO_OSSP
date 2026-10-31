#!/bin/bash
set -e

cd ~/OCTO_OSSP-project/linux-implementation

echo "=== Running TEST 4: Ubuntu Communication ==="
./fifo_reader --timeout 5 &
R_PID=$!
sleep 0.2
./fifo_writer "Hello from Ubuntu"
wait $R_PID

echo "=== Running TEST 5: Messages with spaces ==="
./fifo_reader --timeout 5 &
R_PID=$!
sleep 0.2
./fifo_writer "Hello from Process A to Process B"
wait $R_PID

echo "=== Running TEST 6: Multiple messages ==="
./fifo_reader --timeout 5 &
R_PID=$!
sleep 0.2
./fifo_writer "Message 1: Operating Systems"
wait $R_PID

./fifo_reader --timeout 5 &
R_PID=$!
sleep 0.2
./fifo_writer "Message 2: System Programming"
wait $R_PID

echo "=== ALL C IPC TESTS COMPLETED SUCCESSFULLY ==="
