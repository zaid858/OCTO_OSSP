/*
 * =====================================================================================
 *  Filename:      fifo_writer.c
 *  Description:   Linux Named FIFO Writer Process (Process A)
 *                 Works with both interactive Ubuntu terminal and Website Backend.
 *  Course:        Operating Systems and System Programming (OSSP)
 *  System Calls:  mkfifo(), open(), write(), close(), flock()
 *  Compilation:   gcc -Wall -Wextra fifo_writer.c -o fifo_writer
 * =====================================================================================
 */

#include "fifo_common.h"

static int send_single_message(const char *fifo_path, const char *message, int is_interactive) {
    if (!message || strlen(message) == 0) {
        fprintf(stderr, "Error: Message cannot be empty.\n");
        return -1;
    }

    if (is_interactive) {
        printf("\n[PROCESS A] Opening FIFO %s with flag O_WRONLY...\n", fifo_path);
        printf("(Note: open() will block until Reader Process B attaches O_RDONLY)\n");
    }

    /* 1. Update temporary display file to show message in transit */
    update_display_file(message);

    /* 2. Open FIFO for writing (blocks until reader attaches) */
    int fd = open(fifo_path, O_WRONLY);
    if (fd == -1) {
        perror("System call open() failed on FIFO");
        clear_display_file();
        return -1;
    }

    if (is_interactive) {
        printf("✓ [PROCESS A] FIFO opened successfully. File descriptor: %d\n", fd);
        printf("[PROCESS A] Writing message \"%s\" to FIFO descriptor...\n", message);
    }

    /* 3. Write data bytes into the real FIFO */
    ssize_t bytes_written = write(fd, message, strlen(message) + 1);
    if (bytes_written == -1) {
        perror("System call write() failed");
        close(fd);
        clear_display_file();
        return -1;
    }

    /* Output confirmation */
    printf("✓ [PROCESS A] Wrote %ld bytes into Shared FIFO: \"%s\"\n", (long)bytes_written, message);

    /* 4. Close file descriptor */
    close(fd);

    if (is_interactive) {
        printf("[PROCESS A] Message sent successfully. Descriptor closed.\n");
    }

    return 0;
}

int main(int argc, char *argv[]) {
    char fifo_path[PATH_MAX];
    char writer_lock_path[PATH_MAX];
    char message[BUFFER_SIZE];
    int lock_fd = -1;

    get_fifo_path(fifo_path, sizeof(fifo_path));
    get_writer_lock_path(writer_lock_path, sizeof(writer_lock_path));

    /* Check for --init flag (used during project setup to ensure FIFO exists) */
    if (argc > 1 && strcmp(argv[1], "--init") == 0) {
        if (ensure_fifo_exists(fifo_path, 1) == 0) {
            printf("✓ Shared FIFO initialized at: %s\n", fifo_path);
            return 0;
        } else {
            return 1;
        }
    }

    /* 1. Acquire exclusive session lock to prevent simultaneous conflicts */
    lock_fd = acquire_session_lock(writer_lock_path);
    if (lock_fd < 0) {
        /* Prints: "FIFO is currently being used by another communication session. Please try again." */
        return 2;
    }

    /* 2. Ensure FIFO exists and is verified */
    if (ensure_fifo_exists(fifo_path, 0) != 0) {
        release_session_lock(lock_fd);
        return 1;
    }

    /* Case A: Non-interactive single message (CLI argument or FIFO_MSG environment variable) */
    if (argc > 1) {
        strncpy(message, argv[1], sizeof(message) - 1);
        message[sizeof(message) - 1] = '\0';
        int ret = send_single_message(fifo_path, message, 0);
        release_session_lock(lock_fd);
        return (ret == 0) ? 0 : 1;
    }

    if (getenv("FIFO_MSG") != NULL) {
        strncpy(message, getenv("FIFO_MSG"), sizeof(message) - 1);
        message[sizeof(message) - 1] = '\0';
        int ret = send_single_message(fifo_path, message, 0);
        release_session_lock(lock_fd);
        return (ret == 0) ? 0 : 1;
    }

    /* Case B: Interactive Ubuntu terminal loop - supports multiple consecutive messages with spaces */
    printf("=========================================================\n");
    printf("      LINUX NAMED FIFO WRITER PROCESS (PROCESS A)       \n");
    printf("=========================================================\n");
    printf("Shared FIFO Target: %s\n", fifo_path);
    printf("Display File Target: %s\n", DISPLAY_FILE_NAME);
    printf("(Type a message and press Enter. Type 'exit' or 'quit' to finish)\n\n");

    while (1) {
        printf("[PROCESS A - WRITER] Enter message: ");
        fflush(stdout);

        if (fgets(message, sizeof(message), stdin) == NULL) {
            printf("\nExiting writer process.\n");
            break;
        }

        /* Strip trailing newline */
        message[strcspn(message, "\r\n")] = '\0';

        if (strlen(message) == 0) {
            printf("Warning: Message is empty. Please enter some text.\n");
            continue;
        }

        if (strcmp(message, "exit") == 0 || strcmp(message, "quit") == 0) {
            printf("[PROCESS A] Exit command received. Exiting writer.\n");
            break;
        }

        send_single_message(fifo_path, message, 1);
        printf("\n---------------------------------------------------------\n");
    }

    /* Release lock */
    release_session_lock(lock_fd);
    return 0;
}
