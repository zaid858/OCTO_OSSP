#!/bin/bash
# run_transfer.sh
# Executes reader and writer in coordinated transfer through linux-implementation/myfifo

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

MSG="$1"
if [ -z "$MSG" ]; then
    echo "Error: No message provided."
    exit 1
fi

# 1. Check exclusive session locks
if ! flock -n .fifo_reader.lock true 2>/dev/null || ! flock -n .fifo_writer.lock true 2>/dev/null; then
    echo "FIFO is currently being used by another communication session. Please try again."
    exit 2
fi

# 2. Update display file
printf "%s\n" "$MSG" > myfifo_display.txt

# 3. Clean up stale output logs
rm -f /tmp/reader.out /tmp/writer.out /tmp/reader.err /tmp/writer.err

# 4. Start reader in background waiting on real myfifo
./fifo_reader --timeout 6 > /tmp/reader.out 2> /tmp/reader.err &
R_PID=$!

# 5. Allow 120ms for reader to open myfifo in O_RDONLY mode
sleep 0.12

# 6. Execute writer transmitting payload into myfifo
./fifo_writer "$MSG" > /tmp/writer.out 2> /tmp/writer.err
W_EXIT=$?

# 7. Wait for reader to finish reading and exit
wait $R_PID
R_EXIT=$?

# 8. Output reader results
cat /tmp/reader.out
cat /tmp/writer.out
cat /tmp/reader.err
cat /tmp/writer.err

exit 0
