# LINUX INTER-PROCESS COMMUNICATION (PIPES & FIFOS)
## Academic Presentation Slide Deck (12 Slides)

**Course**: Operating Systems and System Programming (OSSP)  
**Degree**: B.Tech in Computer Science and Engineering  
**Presenter**: G Jashwanth Reddy  
**Project Repository**: `OCTO_OSSP-Project/`

---

### SLIDE 1: Title Slide
- **Header / Title**: OPERATING SYSTEMS & SYSTEM PROGRAMMING
- **Subtitle**: Linux Inter-Process Communication: CO-Wise Implementation & Demonstration
- **Mapping**: Mapping Project Design & Code to Course Outcomes: CO1 (Syscall Abstraction), CO2 (Process Control), CO3 (IPC Mechanisms) | Shared Linux Named FIFO & Real-Time Kernel Bridge
- **Presenter Details**:
  - **Student Name**: G Jashwanth Reddy
  - **Course**: OSSP | Tech Stack: C, POSIX, Linux Kernel, JavaScript (Vite) | License: MIT

---

### SLIDE 2: Course Outcomes (CO) Overview
- **Header**: OPERATING SYSTEMS & SYSTEM PROGRAMMING — CO-WISE IMPLEMENTATION
- **Title**: Course Outcomes (CO) Overview
- **Matrix**:

| CO NO | Course Outcome Description | Project Implementation Mapping |
| :--- | :--- | :--- |
| **CO1** | Analyze the operating system as a layered service abstraction — kernel mode vs user mode, the syscall interface, the role of the shell as a user-space program — and trace a simple command from typing it to completion. | User/Kernel mode boundary traps via POSIX syscall interface (`pipe`, `mkfifo`, `open`, `read`, `write`, `close`, `lstat`). Real kernel execution under WSL/Ubuntu with live step-by-step activity timeline. |
| **CO2** | Apply Unix process-control primitives — `fork`, `exec`, `wait`, `exit` — to write systems-programming code in C that creates, controls, and reaps child processes correctly. | Process creation via `fork()`, parent-child descriptor inheritance, `wait()` process synchronization, and clean child process termination. |
| **CO3** | Apply inter-process communication mechanisms — anonymous pipes, named pipes (FIFOs), Unix domain sockets, signals, and shared memory — to design simple multi-process applications. | Implementation of Anonymous Pipes for related processes and a Single Shared Persistent Named FIFO (`linux-implementation/myfifo`) bridging native C programs with web simulator, featuring immediate in-flight file truncation. |

---

### SLIDE 3: CO1 Implementation: OS Layered Abstraction & Syscalls
- **Header**: OPERATING SYSTEMS & SYSTEM PROGRAMMING — CO-WISE IMPLEMENTATION
- **Title**: CO1 Implementation: OS Layered Abstraction & Syscalls
- **Card 1: 🖥️ User vs Kernel Mode**:
  - **User Space**: Process A and Process B execute in unprivileged user mode.
  - **Software Trap**: Calling `pipe()` or `mkfifo()` triggers a hardware trap (`syscall`), transitioning execution to Linux Kernel Mode.
- **Card 2: ⚙️ POSIX Syscall Interface**:
  - **Core POSIX Calls**: `pipe()`, `fork()`, `mkfifo()`, `open()`, `read()`, `write()`, `close()`, `lstat()`.
  - **POSIX Verification**: Verifies FIFO integrity via `lstat()` and `S_ISFIFO()` before opening, guaranteeing it is a true FIFO special node.
  - **Kernel Protection**: Strict abstraction shields user code from virtual memory paging, inode management, and hardware ring buffers.
- **Card 3: 🔍 Real Kernel Syscall Trace**:
  - **Zero Mock Simulation**: Web Simulator communicates directly with real Linux kernel FIFO through a dedicated Node.js WSL bridge.
  - **6-Step Execution Timeline**: Traces `lstat(S_ISFIFO)` ➔ `open(O_WRONLY)` ➔ `write(payload)` ➔ `open(O_RDONLY)` ➔ `read(buffer)` ➔ `close(fd)`.
  - **Activity Checklist**: Live interactive UI ticks off completed kernel steps with exact descriptor numbers and byte counts.

---

### SLIDE 4: CO2 Implementation: Unix Process-Control Primitives
- **Header**: OPERATING SYSTEMS & SYSTEM PROGRAMMING — CO-WISE IMPLEMENTATION
- **Title**: CO2 Implementation: Unix Process-Control Primitives
- **1. Process Lifecycle & Primitives**:
  - `fork()` Primitive: Clones parent process context to spawn Child (Process B) with identical virtual address space.
  - Descriptor Inheritance: Child automatically inherits parent's open file descriptor table containing `pipefd[0]` and `pipefd[1]`.
  - `wait(NULL)` Reaping: Parent calls `wait()` to synchronize execution, blocking until child completes to eliminate zombie processes.
  - `exit()` Termination: Child finishes cleanly and returns exit code (`EXIT_SUCCESS`) to OS kernel.
- **2. Process Control Implementation Rules**:
  - Closing Unneeded End (Parent): Closes `fd[0]` immediately after `fork()` to maintain strict Writer role.
  - Closing Unneeded End (Child): Closes `fd[1]` immediately after `fork()` to maintain strict Reader role.
  - EOF Signal Generation: Closing parent's `fd[1]` reduces kernel reference count to 0, sending EOF (0 bytes) to child `read()`.
  - Deadlock Prevention: Failing to close unneeded descriptor ends leaves write reference open, causing `read()` to block forever.

---

### SLIDE 5: CO3 Implementation: Anonymous Pipe Mechanics
- **Header**: OPERATING SYSTEMS & SYSTEM PROGRAMMING — CO-WISE IMPLEMENTATION
- **Title**: CO3 Implementation: Anonymous Pipe Mechanics
- **1. Anonymous Pipe Architecture (`pipe`)**:
  - Half-Duplex Stream: Single unidirectional byte stream (Data flows strictly from `fd[1]` ➔ `fd[0]`).
  - Kernel Memory Buffer: Maintains standard 64KB circular ring buffer directly inside Linux kernel RAM.
  - Scope Limit: Restricted strictly to related processes sharing parent-child fork lineage.
  - No Disk Presence: Purely transient in-memory structure; destroyed automatically when all file descriptors close.
- **2. System Call Sequence & Flow**:
  - `pipe(int fd[2])`: Allocates descriptor pair: `fd[0]` for reading, `fd[1]` for writing.
  - `write(fd[1], buf, len)`: Pushes byte payload into kernel ring buffer. Blocks if buffer is full (64KB).
  - `read(fd[0], buf, capacity)`: Pulls byte payload from kernel ring buffer. Blocks if buffer is empty.
  - `close(fd[1])` ➔ EOF: Closing write end causes subsequent `read()` call to return 0 (EOF), signaling stream end.

---

### SLIDE 6: CO3 Implementation: Named FIFO Mechanics
- **Header**: OPERATING SYSTEMS & SYSTEM PROGRAMMING — CO-WISE IMPLEMENTATION
- **Title**: CO3 Implementation: Named FIFO Mechanics
- **1. Shared Named FIFO Architecture (`myfifo`)**:
  - **Unified Shared Path**: Single real Linux FIFO at `linux-implementation/myfifo` shared by both Web Simulator & Ubuntu C binaries.
  - **S_ISFIFO Verification**: Checks node with `lstat()`; guarantees POSIX named pipe (`prw-r--r--`) and refuses to overwrite regular files.
  - **Persistent Lifecycle**: FIFO remains present across sessions; no deletion after each message, matching real production system daemons.
  - **Concurrency Protection**: Exclusive session locks via `flock()` prevent simultaneous conflicting reader/writer executions.
- **2. Rendezvous Handshake & System Calls**:
  - `mkfifo(path, 0666)`: Creates real POSIX FIFO node in filesystem directory with read/write permissions.
  - `open(path, O_WRONLY)` [Process A]: Writer opens FIFO. Blocks in kernel until Reader attaches (unblocks on handshake).
  - `open(path, O_RDONLY)` [Process B]: Reader attaches to the same node, completing rendezvous and releasing both processes.
  - `write()` & `read()`: Transfers exact payload through kernel buffer; Process B confirms receipt instantly.

---

### SLIDE 7: Comparative Matrix: Anonymous Pipe vs Named FIFO
- **Header**: OPERATING SYSTEMS & SYSTEM PROGRAMMING — CO-WISE IMPLEMENTATION
- **Title**: Comparative Matrix: Anonymous Pipe vs Named FIFO

| Feature / Property | Anonymous Pipe (`pipe`) | Named FIFO (`mkfifo`) |
| :--- | :--- | :--- |
| **Process Scope** | Related processes only (Parent & Child spawned via `fork`) | Unrelated independent processes running anywhere in system |
| **Filesystem Identity** | No path in filesystem (Anonymous/Unnamed) | Dedicated persistent node: `linux-implementation/myfifo` |
| **Creation Call** | `pipe(int fd[2])` | `mkfifo(const char *path, mode_t mode)` |
| **Lifespan / Persistence** | Transient: Exists only while descriptor reference > 0 | Persistent: Retained on filesystem across sessions; verified via `lstat()` & `S_ISFIFO` |
| **Opening Semantics** | Created pre-opened via `pipe()` descriptor array | Explicit `open()` call required; BLOCKS until reader & writer connect |
| **Directionality** | Unidirectional (Half-Duplex) | Unidirectional per node; Bidirectional requires two FIFOs |

---

### SLIDE 8: Interactive Web Simulator Design
- **Header**: OPERATING SYSTEMS & SYSTEM PROGRAMMING — CO-WISE IMPLEMENTATION
- **Title**: Interactive Web Simulator Design
- **Card 1: 🎨 Modern Visual Laboratory**:
  - Sleek dark aesthetic with cyan/purple accents, responsive glass cards, and status indicators.
  - Dual interactive modes: Anonymous Pipe Simulator vs Single Shared FIFO Visualizer.
  - Live Disk File Monitor: Real-time badge inside FIFO box reflecting exact 0-byte file status on disk.
- **Card 2: ⚡ Real Linux Backend Bridge**:
  - Local Node.js Backend Bridge (`server.js` & Vite middleware) wired directly to WSL2/Ubuntu.
  - Real Kernel Traps: Triggers actual C binaries via `run_transfer.sh` in < 1.2s total execution.
  - Process B displays actual received payload confirmed from Linux `read()`, eliminating mock strings.
- **Card 3: 📄 In-Flight File Immediate Clear**:
  - `myfifo_display.txt` mirrors message payload on disk strictly while in transit.
  - Immediate Truncation: Process B confirmation (`bytes_read > 0`) immediately truncates file to 0 bytes without delays.
  - Race Protection: `clear_display_file_if_matching()` ensures older cleanups never erase newer rapid messages.

---

### SLIDE 9: Execution & Verification Guide
- **Header**: OPERATING SYSTEMS & SYSTEM PROGRAMMING — CO-WISE IMPLEMENTATION
- **Title**: Execution & Verification Guide
- **1. Running the Web Simulator**:
  ```bash
  # Project Root: OCTO_OSSP-Project/
  npm install            # Install Vite & dev tools
  npm run dev            # Start Vite + Linux Backend API
  # Opens automatically at: http://localhost:5173
  # VS Code One-Click: Press F5 to launch debugger
  # In-Editor View: Ctrl+Shift+P -> Simple Browser: Show
  ```
- **2. Running Native C Programs (Linux/WSL)**:
  ```bash
  cd OCTO_OSSP-Project/linux-implementation
  make all               # Compiles pipe_demo, fifo_writer, fifo_reader
  # Manual Shared FIFO (Two Terminal Windows):
  Terminal 1:  ./fifo_reader     # Process B: opens O_RDONLY
  Terminal 2:  ./fifo_writer     # Process A: opens O_WRONLY & writes
  # Coordinated Script: ./run_transfer.sh 'Message' (<1.2s)
  # Persistent Log:    cat received_messages.txt
  ```

---

### SLIDE 10: Conclusion & Course Outcomes Attainment
- **Header**: OPERATING SYSTEMS & SYSTEM PROGRAMMING — CO-WISE IMPLEMENTATION
- **Title**: Conclusion & Course Outcomes Attainment
- **🎯 CO1 Attainment — Layered Abstraction & Real Syscalls**:
  - Demonstrated genuine User Space to Kernel Space transitions via direct system calls (`pipe`, `mkfifo`, `open`, `read`, `write`, `close`, `lstat`) with zero mock fakes and real-time execution logging.
- **🎯 CO2 Attainment — Unix Process Control & Hygiene**:
  - Mastered Unix primitives (`fork`, `wait`, `exit`) for child process control, descriptor table inheritance, closing unused ends to guarantee EOF, and reaping to prevent zombie processes.
- **🎯 CO3 Attainment — Unified IPC & Immediate Synchronization**:
  - Successfully implemented Anonymous Pipes for related streams and a Single Shared Linux Named FIFO (`linux-implementation/myfifo`) uniting a modern web lab with native Ubuntu C programs, featuring immediate 0-delay display file truncation.
- **🚀 Comprehensive Deliverable & Impact**:
  - Bridged low-level Linux systems programming with an intuitive web laboratory simulator for complete conceptual, visual, and practical mastery.

---

### SLIDE 11: Real-Time Web-to-Kernel Architecture
- **Header**: OPERATING SYSTEMS & SYSTEM PROGRAMMING — ADVANCED INTEGRATION
- **Title**: System Integration: Real-Time Web-to-Kernel Architecture
- **🌐 1. Web Presentation Layer**:
  - Interactive Web Client: Built with modern HTML5/ES6 and responsive glassmorphism UI.
  - Process A (Writer): Captures user input message and initiates real transmission.
  - Channel Animation: Animates data packet gliding into the central FIFO buffer with live status indicators.
  - Process B (Reader): Displays actual received payload read from the real Linux kernel FIFO.
- **⚡ 2. Local Backend Bridge**:
  - Node.js API Bridge: Lightweight backend middleware (`server.js` & Vite) listening on port 5173.
  - REST Endpoints: `/api/fifo/write` (transfer), `/api/fifo/status`, `/api/fifo/display`, `/api/fifo/reset`.
  - Session Locking (`flock`): Non-blocking locks prevent concurrent session collisions.
  - Coordinated Transfer: Executes `run_transfer.sh` in WSL2/Ubuntu in < 1.2s total round-trip time.
- **🐧 3. Native Linux Kernel IPC**:
  - Single Shared FIFO: Real POSIX named pipe at `linux-implementation/myfifo` (`prw-r--r--`).
  - POSIX Verification: `lstat()` and `S_ISFIFO()` ensure node is a real FIFO special file.
  - Native C Binaries: `fifo_writer.c` and `fifo_reader.c` execute real kernel traps (`open`, `read`, `write`, `close`).
  - Dual-Client Support: Ubuntu terminal and Web Simulator use the exact same filesystem object.

---

### SLIDE 12: In-Flight File Synchronization & Immediate Truncation
- **Header**: OPERATING SYSTEMS & SYSTEM PROGRAMMING — ADVANCED INTEGRATION
- **Title**: In-Flight File Synchronization & Immediate Truncation
- **🎯 1. The Engineering Requirement**:
  - Visual File Mirroring: `myfifo_display.txt` mirrors payload on disk while in transit through FIFO.
  - Zero Stale Data: File must become completely empty (0 bytes) as soon as Process B completes `read()`.
  - No Arbitrary Delays: Prohibits `sleep()`, `setTimeout()`, or fixed delay timers for cleanup.
  - Disk File Integrity: Ensures actual disk sectors are truncated, not just frontend visual hiding.
- **⚡ 2. Immediate Receipt Trigger**:
  - Read Confirmation Trigger: `fifo_reader.c` triggers `clear_display_file_if_matching()` immediately upon `read() > 0`.
  - Atomic Truncation: `ftruncate(fileno(f), 0)` instantly zeroes the file descriptor on disk.
  - Dual-Environment Sync: Truncates both Linux ext4 and Windows NTFS file mirrors simultaneously.
  - Failed-Read Safety: If `read()` returns `<= 0` (timeout/error), clearing is aborted to preserve state.
- **🛡️ 3. Race & Sequence Protection**:
  - Payload Matching Check: Compares current file content with received message before truncating.
  - Protects Newer Messages: Prevents an asynchronous cleanup of a previous message from erasing a newer message.
  - Persistent History Log: `received_messages.txt` records timestamped payload and source for auditing.
  - Web Live Status Badge: UI displays real-time disk file state: `[EMPTY (0 bytes)]` / `[In Transit]` / `[CLEARED]`.
