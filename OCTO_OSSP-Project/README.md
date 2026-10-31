# Linux Inter-Process Communication Using Pipes and FIFOs

A complete, interactive visual simulator and production C implementation suite designed for **Operating Systems and System Programming (OSSP)** coursework.

---

## 📌 Project Overview

**Inter-Process Communication (IPC)** allows concurrent Linux processes to exchange data and synchronize execution. This project provides a dual-approach demonstration:
1. **Interactive Web Application Simulator (`/src` & `index.html`)**: An interactive browser-based visualization modeled as a modern Operating Systems Laboratory. Users enter dynamic strings in Process A, observe SVG/CSS packet animations traversing kernel Pipe / FIFO buffer queues, and view dynamic outputs received in Process B alongside system call execution timelines.
2. **Actual Linux C Implementation (`/linux-implementation`)**: Standalone C programs written for Linux/Ubuntu/WSL utilizing native POSIX system calls (`pipe`, `fork`, `mkfifo`, `open`, `read`, `write`, `close`, `unlink`).

---

## 🚀 Quick Start - Web Application Simulator

### Option A: Local Dev Server (Recommended)
```bash
# 1. Install dependencies (Vite)
npm install

# 2. Start local development server
npm run dev
```
Open the provided URL (typically `http://localhost:5173`) in any modern Web Browser (Chrome, Firefox, Edge, Safari).

### Option B: Static Browser Viewing
Simply double-click `index.html` or open it directly in your browser without needing any server setup.

---

## 🐧 Quick Start - Linux C Implementation

Navigate to the `linux-implementation` folder on Linux / Ubuntu / WSL:

```bash
cd linux-implementation

# Build all binaries
make all

# Run Anonymous Pipe Demonstration
./pipe_demo

# Run Named FIFO Demonstration (Open 2 terminal tabs)
# Terminal 1:
./fifo_reader

# Terminal 2:
./fifo_writer
```

---

## 💡 Core Concepts & System Calls

### 1. Anonymous Pipe (`pipe()`)
- **Memory Buffer**: Managed directly in Linux kernel memory (64KB default capacity).
- **Scope**: Unidirectional data stream strictly between related processes (e.g., Parent and Child created via `fork()`).
- **Descriptors**: `pipefd[0]` for reading, `pipefd[1]` for writing.

### 2. Named FIFO (`mkfifo()`)
- **Filesystem Node**: Appears as a special file node (e.g., `/tmp/myfifo`).
- **Scope**: Enables bidirectional or unidirectional IPC between completely independent, unrelated processes.
- **Persistence**: Exists in the filesystem until explicitly removed via `unlink()`.

### 3. System Call Reference

| System Call | Signature / Usage | Purpose in IPC |
| :--- | :--- | :--- |
| `pipe()` | `int pipe(int pipefd[2])` | Allocates an anonymous pipe descriptor pair in memory. |
| `fork()` | `pid_t fork(void)` | Spawns child process duplicating parent descriptor table. |
| `mkfifo()` | `int mkfifo(const char *pathname, mode_t mode)` | Creates named FIFO node in the filesystem. |
| `open()` | `int open(const char *pathname, int flags)` | Attaches process to FIFO in `O_RDONLY` or `O_WRONLY` mode. |
| `write()` | `ssize_t write(int fd, const void *buf, size_t count)` | Transmits data buffer bytes into IPC kernel queue. |
| `read()` | `ssize_t read(int fd, void *buf, size_t count)` | Receives data buffer bytes from IPC kernel queue. |
| `close()` | `int close(int fd)` | Closes descriptor, signaling EOF when all write ends close. |
| `unlink()` | `int unlink(const char *pathname)` | Deletes FIFO special file node from filesystem. |

---

## 📂 Repository Structure

```text
OCTO_OSSP-project/
├── index.html                   # Main Web Application Single-Page Layout
├── package.json                 # Project configuration & dev scripts (Vite)
├── README.md                    # Main Repository Documentation
├── src/
│   ├── css/
│   │   └── main.css             # OS Lab Dark Theme, Glassmorphism & Keyframe Animations
│   └── js/
│       ├── main.js              # Navigation & accordion tab controllers
│       ├── pipe-simulator.js    # Anonymous Pipe interactive animation engine
│       └── fifo-simulator.js    # Named FIFO queue visualizer & checklist engine
└── linux-implementation/
    ├── pipe_demo.c              # Anonymous Pipe C source code (pipe, fork, write, read)
    ├── fifo_writer.c            # Named FIFO Writer C source code (mkfifo, open, write)
    ├── fifo_reader.c            # Named FIFO Reader C source code (open, read, unlink)
    ├── Makefile                 # GCC build script for Linux/WSL
    └── README.md                # Compilation & execution guide for C programs
```

---

## ⚡ Technical Clarification

- **Visual Simulator**: The browser interface is an educational visual model. JavaScript handles the dynamic visual packet animations and status timelines.
- **Native Implementation**: The C programs in `/linux-implementation` execute actual Linux kernel system calls under Linux/WSL environments.

---

## 🎓 Project Details
- **Course**: Operating Systems and System Programming (OSSP)
- **Author**: G Jashwanth Reddy
- **License**: MIT
