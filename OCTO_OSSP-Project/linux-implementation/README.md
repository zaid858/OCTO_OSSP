# Linux Inter-Process Communication (Pipes & FIFOs) - C Implementation

This directory contains the production C source code demonstrating native Linux IPC system calls for an **Operating Systems and System Programming (OSSP)** coursework project.

---

## 📁 Source Code Files

| File | System Calls Demonstrated | Description |
| :--- | :--- | :--- |
| `pipe_demo.c` | `pipe()`, `fork()`, `write()`, `read()`, `close()` | Anonymous pipe IPC between Parent (Process A) and Child (Process B). |
| `fifo_writer.c` | `mkfifo()`, `open()`, `write()`, `close()` | Writer Process A that creates `/tmp/myfifo` and writes user payload. |
| `fifo_reader.c` | `open()`, `read()`, `close()`, `unlink()` | Reader Process B that attaches to `/tmp/myfifo`, reads data, and cleans up node. |
| `Makefile` | GCC Compiler Commands | Build script for automated compilation and target execution. |

---

## 🛠️ Compilation & Execution Instructions (Linux / Ubuntu / WSL)

### Prerequisites
- GCC Compiler (`gcc`)
- Make utility (`make`)
- Linux Environment (Ubuntu, Debian, Fedora, or WSL2 on Windows)

---

### Demonstration 1: Anonymous Pipe (`pipe_demo.c`)

1. **Compile the program**:
   ```bash
   make pipe_demo
   # or manually: gcc -Wall -Wextra pipe_demo.c -o pipe_demo
   ```

2. **Run the program**:
   ```bash
   ./pipe_demo
   ```

3. **Sample Execution**:
   ```text
   =========================================================
        LINUX ANONYMOUS PIPE IPC DEMONSTRATION (OSSP)      
   =========================================================

   [PROCESS A - PARENT] Enter a message to send through Pipe: Hello Linux Pipe!
   ✓ System call pipe() succeeded. Descriptors: read_fd=3, write_fd=4

   [PROCESS A (PID: 4120)] Active. Closing unneeded read descriptor fd[0]...
   [PROCESS A] Writing data "Hello Linux Pipe!" to pipe write descriptor fd[1]...
   ✓ [PROCESS A] Successfully wrote 18 bytes into kernel pipe buffer.

   [PROCESS B (PID: 4121)] Spawned via fork(). Closing unneeded write descriptor fd[1]...
   [PROCESS B] Waiting to read from pipe read descriptor fd[0]...
   ✓ [PROCESS B] Successfully read 18 bytes from pipe.

   =========================================================
    [PROCESS B RECEIVED OUTPUT]: "Hello Linux Pipe!"
   =========================================================
   ```

---

### Demonstration 2: Named FIFO (`fifo_writer.c` & `fifo_reader.c`)

Because Named FIFOs facilitate IPC between independent processes, you should run Writer and Reader in two separate terminal windows.

#### Step 1: Terminal 1 - Start the Reader Process (Process B)
```bash
make fifo_reader
./fifo_reader
```
*(Process B will open `/tmp/myfifo` in `O_RDONLY` mode and block until Process A opens for writing.)*

#### Step 2: Terminal 2 - Start the Writer Process (Process A)
```bash
make fifo_writer
./fifo_writer
```
*Enter your message when prompted (e.g. `OSSP Named FIFO Test`).*

#### Expected Result:
Process A writes the message into `/tmp/myfifo` and exits. Process B instantly receives the message in Terminal 1, prints it out, closes descriptors, and unlinks the FIFO file node!

---

## 🧹 Cleaning Build Artifacts

To remove compiled binaries and clean up any lingering `/tmp/myfifo` file nodes:
```bash
make clean
```
