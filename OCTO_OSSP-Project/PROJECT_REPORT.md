# FORGESHELL PROJECT REPORT
## Linux Inter-Process Communication Using Pipes and FIFOs

**Project Report**: Linux IPC using Unnamed Pipes and Named FIFOs  

---

### 1. Problem Statement
Inter-Process Communication (IPC) is an essential mechanism in Linux operating systems that allows multiple processes to exchange data and coordinate their activities. Since processes normally operate in separate memory spaces, a controlled communication mechanism is required for transferring information between them.

The objective of this project is to implement and demonstrate Inter-Process Communication using Pipes and FIFOs in Linux. The project focuses on understanding how processes can communicate through kernel-managed communication channels without directly accessing each other's memory.

The implementation demonstrates two important IPC mechanisms: Pipes, primarily used for communication between related processes such as a parent and child process, and FIFOs (Named Pipes), which can be used for communication between processes that do not necessarily have a parent-child relationship.

---

### 2. Objectives
- Understand the concept of Inter-Process Communication in Linux.
- Study the working mechanism of unnamed pipes.
- Implement communication between a parent and child process using a pipe.
- Understand and implement Named Pipes (FIFOs).
- Demonstrate communication between independent processes using FIFOs.
- Use Linux system calls such as `pipe()`, `fork()`, `read()`, `write()`, `close()`, `mkfifo()`, and `open()`.
- Understand how data flows between processes through kernel-managed buffers.
- Test the communication mechanisms using multiple test cases.
- Demonstrate the practical importance of IPC in Linux-based applications.

---

### 3. Selected Commands and Their Workflow

#### 3.1 `pipe()`
The `pipe()` system call creates an unnamed pipe. It returns two file descriptors: `fd[0]` for reading and `fd[1]` for writing.

```c
int fd[2];
pipe(fd);
fd[0] -> Read end
fd[1] -> Write end
```

Data written using `fd[1]` can be read using `fd[0]`.

**Workflow**: Process A -> `write()` -> Pipe -> `read()` -> Process B

#### 3.2 `fork()`
The `fork()` system call creates a new child process. After `fork()`, the parent and child processes can use the pipe descriptors inherited from the parent.

```c
pid_t pid = fork();
```

#### 3.3 `write()`
The `write()` system call sends data into the pipe.

```c
write(fd[1], message, strlen(message) + 1);
```

#### 3.4 `read()`
The `read()` system call receives data from the pipe into a buffer.

```c
read(fd[0], buffer, sizeof(buffer));
```

#### 3.5 `close()`
Unused pipe descriptors should be closed to avoid unnecessary resource usage and to allow correct end-of-file behavior.

```c
close(fd[0]);
close(fd[1]);
```

#### 3.6 `mkfifo()`
The `mkfifo()` system call creates a named pipe in the Linux filesystem.

```c
mkfifo("myfifo", 0666);
```

The FIFO can be verified from the terminal using:

```bash
ls -l myfifo
```

#### 3.7 `open()`
A FIFO can be opened for reading or writing.

```c
open("myfifo", O_RDONLY);   /* Reader */
open("myfifo", O_WRONLY);   /* Writer */
```

#### 3.8 Compilation and Execution

```bash
gcc pipe.c -o pipe
./pipe
gcc fifo_writer.c -o fifo_writer
gcc fifo_reader.c -o fifo_reader
```

---

### 4. Implementation

#### 4.1 Module 1 - IPC Using Pipe
The first implementation uses an unnamed pipe to establish communication between a parent and child process.

```text
Parent Process      |    pipe()      |    fork()
   /   \
Parent  Child
  |       |
write() read()
  |       |
  +--Pipe-+
```

Sample implementation:

```c
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/wait.h>

int main() {
    int fd[2];
    char buffer[100];
    pipe(fd);
    pid_t pid = fork();
    if (pid > 0) {
        close(fd[0]);
        char message[] = "Hello from Parent";
        write(fd[1], message, strlen(message) + 1);
        close(fd[1]);
        wait(NULL);
    }
    else if (pid == 0) {
        close(fd[1]);
        read(fd[0], buffer, sizeof(buffer));
        printf("Child received: %s\n", buffer);
        close(fd[0]);
    }
    return 0;
}
```

Expected output:

```text
Child received: Hello from Parent
```

#### 4.2 Module 2 - IPC Using FIFO
Unlike an unnamed pipe, a FIFO has a name in the filesystem and can be accessed by separate processes.

```text
Terminal 1                 Terminal 2
FIFO Writer                FIFO Reader
    |                          |
  open()                     open()
    |                          |
  write()                    read()
    |                          |
    +-------- myfifo ---------+
```

The writer opens the FIFO in write mode and transmits data. The reader opens the FIFO in read mode and receives the data.

---

### 5. Detailed Description of the Implementation

#### 5.1 Pipe-Based Communication
The pipe implementation starts by creating a pipe using `pipe(fd)`. The pipe provides two file descriptors: `fd[0]` for reading and `fd[1]` for writing. The `fork()` system call then creates a child process.

The parent process closes the read end, creates a message, writes the message into the pipe, closes the write end, and waits for the child. The child closes the write end, reads the message, displays it, and closes the read end. This demonstrates one-way communication from the parent to the child.

#### 5.2 FIFO-Based Communication
A FIFO is created using `mkfifo("myfifo", 0666)`. Unlike an unnamed pipe, the FIFO has a filesystem name and can therefore be opened by independent processes.

```c
Writer:
int fd = open("myfifo", O_WRONLY);
write(fd, message, strlen(message) + 1);

Reader:
int fd = open("myfifo", O_RDONLY);
read(fd, buffer, sizeof(buffer));
```

After communication is complete, both processes close the FIFO descriptor.

#### 5.3 Difference Between Pipe and FIFO

| Feature | Pipe | FIFO |
| :--- | :--- | :--- |
| **Type** | Unnamed IPC | Named IPC |
| **Filesystem name** | No | Yes |
| **Typical communication** | Related processes | Independent processes |
| **Creation** | `pipe()` | `mkfifo()` |
| **Access** | File descriptors | File descriptors |
| **Persistence** | Exists while in use | FIFO file remains until removed |

---

### 6. Test Cases and Results

| Test Case | Description | Expected Result | Result |
| :--- | :--- | :--- | :--- |
| **TC01** | Create a pipe | Pipe should be created successfully | PASS |
| **TC02** | Create child using fork() | Child process should be created | PASS |
| **TC03** | Parent sends message through pipe | Child should receive message | PASS |
| **TC04** | Child reads data from pipe | Correct message should be displayed | PASS |
| **TC05** | Create FIFO using mkfifo() | Named FIFO should be created | PASS |
| **TC06** | Writer sends data through FIFO | Data should reach reader | PASS |
| **TC07** | Reader receives FIFO data | Correct message should be displayed | PASS |
| **TC08** | Close communication descriptors | Resources should be released correctly | PASS |

#### Test Case 1 - Pipe Creation
```c
pipe(fd);
```
Expected: Pipe created successfully. Result: PASS.

#### Test Case 2 - Parent-to-Child Communication
```text
Input: Hello from Parent
Child received: Hello from Parent
```
Result: PASS.

#### Test Case 3 - FIFO Creation
```bash
mkfifo("myfifo", 0666)
ls -l myfifo
```
Expected: A named FIFO named myfifo is present. Result: PASS.

#### Test Case 4 - FIFO Communication
```text
Writer sends: Hello from FIFO Writer
Reader received: Hello from FIFO Writer
```
Result: PASS.

#### Test Case 5 - Multiple Messages
The writer sends Message 1, Message 2, and Message 3. The reader receives the transmitted messages in sequence.

```text
Message 1
Message 2
Message 3
```
Result: PASS.

---

### 7. Conclusion
The Linux Inter-Process Communication Using Pipes and FIFOs project successfully demonstrates two fundamental IPC mechanisms available in Linux. The pipe implementation demonstrates communication between related processes, particularly a parent and child process created using `fork()`. The FIFO implementation extends this concept by allowing communication between independent processes through a named communication channel.

Through this project, the working of important Linux system calls such as `pipe()`, `fork()`, `read()`, `write()`, `close()`, `mkfifo()`, and `open()` was studied and implemented.

The test cases demonstrate that data can be transferred between processes using both mechanisms. The project also provides a practical understanding of process synchronization, file descriptors, kernel-managed communication buffers, and resource management.

Overall, the project provides a foundation for understanding more advanced IPC mechanisms used in Linux applications, operating systems, servers, and distributed software environments.
