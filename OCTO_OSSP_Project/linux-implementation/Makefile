# Makefile for Linux Inter-Process Communication (Pipes & FIFOs) C Programs
# Course: Operating Systems & System Programming (OSSP)

CC = gcc
CFLAGS = -Wall -Wextra -O2

TARGETS = pipe_demo fifo_writer fifo_reader

all: $(TARGETS) setup-fifo

pipe_demo: pipe_demo.c
	$(CC) $(CFLAGS) pipe_demo.c -o pipe_demo

fifo_writer: fifo_writer.c fifo_common.h
	$(CC) $(CFLAGS) fifo_writer.c -o fifo_writer

fifo_reader: fifo_reader.c fifo_common.h
	$(CC) $(CFLAGS) fifo_reader.c -o fifo_reader

setup-fifo: fifo_writer
	./fifo_writer --init

verify-fifo:
	@echo "Checking Shared FIFO node status:"
	@ls -la myfifo
	@file myfifo
	@test -p myfifo && echo "✓ Verified: myfifo is a real POSIX named pipe (FIFO)" || echo "✗ Error: not a FIFO"

run-pipe: pipe_demo
	./pipe_demo

run-fifo-writer: fifo_writer
	./fifo_writer

run-fifo-reader: fifo_reader
	./fifo_reader

# Standard clean preserves the shared myfifo between sessions
clean:
	rm -f $(TARGETS) .fifo_*.lock myfifo_display.txt

# Full cleanup target to also remove myfifo and history if explicitly requested
clean-all: clean
	rm -f myfifo received_messages.txt

.PHONY: all clean clean-all run-pipe run-fifo-writer run-fifo-reader setup-fifo verify-fifo
