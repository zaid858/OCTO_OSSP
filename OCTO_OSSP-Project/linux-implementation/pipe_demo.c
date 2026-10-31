/*
 * =====================================================================================
 *  Filename:      pipe_demo.c
 *  Description:   Linux Anonymous Pipe Inter-Process Communication (IPC) Demonstration
 *  Course:        Operating Systems and System Programming (OSSP)
 *  System Calls:  pipe(), fork(), write(), read(), close()
 *  Compilation:   gcc -Wall -Wextra pipe_demo.c -o pipe_demo
 * =====================================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

#define BUFFER_SIZE 256

int main(void) {
    int fd[2];
    pid_t pid;
    char write_msg[BUFFER_SIZE];
    char read_msg[BUFFER_SIZE];

    printf("=========================================================\n");
    printf("     LINUX ANONYMOUS PIPE IPC DEMONSTRATION (OSSP)      \n");
    printf("=========================================================\n\n");

    // Prompt user for input message
    printf("[PROCESS A - PARENT] Enter a message to send through Pipe: ");
    if (fgets(write_msg, sizeof(write_msg), stdin) == NULL) {
        perror("Error reading input");
        exit(EXIT_FAILURE);
    }
    // Strip trailing newline character
    write_msg[strcspn(write_msg, "\n")] = '\0';

    // 1. Create anonymous pipe channel: fd[0] = Read end, fd[1] = Write end
    if (pipe(fd) == -1) {
        perror("System call pipe() failed");
        exit(EXIT_FAILURE);
    }
    printf("✓ System call pipe() succeeded. Descriptors: read_fd=%d, write_fd=%d\n", fd[0], fd[1]);

    // 2. Fork process context to create Process B (Child)
    pid = fork();

    if (pid < 0) {
        perror("System call fork() failed");
        exit(EXIT_FAILURE);
    }

    if (pid > 0) {
        /* -------------------------------------------------------------
         * PROCESS A: PARENT PROCESS (PRODUCER / WRITER)
         * ------------------------------------------------------------- */
        printf("\n[PROCESS A (PID: %d)] Active. Closing unneeded read descriptor fd[0]...\n", getpid());
        close(fd[0]); // Close unused read end

        printf("[PROCESS A] Writing data \"%s\" to pipe write descriptor fd[1]...\n", write_msg);
        ssize_t bytes_written = write(fd[1], write_msg, strlen(write_msg) + 1);
        if (bytes_written == -1) {
            perror("System call write() failed");
            exit(EXIT_FAILURE);
        }
        printf("✓ [PROCESS A] Successfully wrote %ld bytes into kernel pipe buffer.\n", (long)bytes_written);

        close(fd[1]); // Close write descriptor to signal EOF to child
        wait(NULL);   // Wait for child process B to complete
        printf("[PROCESS A] Child process finished. Exiting parent.\n");

    } else {
        /* -------------------------------------------------------------
         * PROCESS B: CHILD PROCESS (CONSUMER / READER)
         * ------------------------------------------------------------- */
        printf("\n[PROCESS B (PID: %d)] Spawned via fork(). Closing unneeded write descriptor fd[1]...\n", getpid());
        close(fd[1]); // Close unused write end

        printf("[PROCESS B] Waiting to read from pipe read descriptor fd[0]...\n");
        ssize_t bytes_read = read(fd[0], read_msg, sizeof(read_msg));
        if (bytes_read == -1) {
            perror("System call read() failed");
            exit(EXIT_FAILURE);
        }

        printf("✓ [PROCESS B] Successfully read %ld bytes from pipe.\n", (long)bytes_read);
        printf("\n=========================================================\n");
        printf(" [PROCESS B RECEIVED OUTPUT]: \"%s\"\n", read_msg);
        printf("=========================================================\n\n");

        close(fd[0]); // Close read descriptor
        exit(EXIT_SUCCESS);
    }

    return 0;
}
