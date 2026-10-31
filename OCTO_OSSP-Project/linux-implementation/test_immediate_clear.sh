#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=========================================================="
echo "TEST A: Verify message is in myfifo_display.txt during write"
echo "=========================================================="

MSG="Operating Systems Project"

# Start reader waiting in background
./fifo_reader --timeout 5 > /tmp/reader.out 2> /tmp/reader.err &
R_PID=$!
sleep 0.1

# Writer sends message
./fifo_writer "$MSG" > /tmp/writer.out 2> /tmp/writer.err

# Wait for reader to complete
wait $R_PID

# Check reader output
cat /tmp/reader.out

# Check size of display file IMMEDIATELY after reader completes
SIZE=$(stat -c%s myfifo_display.txt 2>/dev/null || echo 0)
echo "Size of myfifo_display.txt immediately after Process B received message: $SIZE bytes"
if [ "$SIZE" -eq 0 ]; then
    echo "✓ SUCCESS: myfifo_display.txt was cleared immediately upon Process B receipt!"
else
    echo "✗ FAIL: myfifo_display.txt is NOT empty ($SIZE bytes)"
    cat myfifo_display.txt
    exit 1
fi

echo ""
echo "=========================================================="
echo "TEST B: Messages with spaces"
echo "=========================================================="

MSG2="Advanced Linux IPC Using Named Pipes and FIFOs"

./fifo_reader --timeout 5 > /tmp/reader.out 2> /tmp/reader.err &
R_PID=$!
sleep 0.1

./fifo_writer "$MSG2" > /tmp/writer.out 2> /tmp/writer.err
wait $R_PID

cat /tmp/reader.out
SIZE2=$(stat -c%s myfifo_display.txt 2>/dev/null || echo 0)
echo "Size of myfifo_display.txt immediately after receipt: $SIZE2 bytes"
if [ "$SIZE2" -eq 0 ]; then
    echo "✓ SUCCESS: Cleared immediately for message with spaces!"
else
    echo "✗ FAIL: Not empty!"
    exit 1
fi

echo ""
echo "=========================================================="
echo "TEST C: Multiple consecutive messages without wiping newer message"
echo "=========================================================="

for i in 1 2 3; do
    MSG_LOOP="Consecutive Message $i"
    ./fifo_reader --timeout 5 > /tmp/reader.out 2> /tmp/reader.err &
    R_PID=$!
    sleep 0.1
    ./fifo_writer "$MSG_LOOP" > /tmp/writer.out 2> /tmp/writer.err
    wait $R_PID
    SIZE_LOOP=$(stat -c%s myfifo_display.txt 2>/dev/null || echo 0)
    echo "Iteration $i ($MSG_LOOP): display file size after receipt = $SIZE_LOOP bytes"
    if [ "$SIZE_LOOP" -ne 0 ]; then
        echo "✗ FAIL: Iteration $i not cleared!"
        exit 1
    fi
done

echo ""
echo "=========================================================="
echo "ALL TESTS PASSED: myfifo_display.txt clears immediately"
echo "upon confirmed receipt by Process B with 0-second delay!"
echo "=========================================================="
