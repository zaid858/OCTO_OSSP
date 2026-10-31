/*
 * =====================================================================================
 *  Filename:      fifo_reader.c
 *  Description:   Linux Named FIFO Reader Process (Process B)
 *                 Works with both interactive Ubuntu terminal and Website Backend.
 *  Course:        Operating Systems and System Programming (OSSP)
 *  System Calls:  open(), read(), close(), flock()
 *  Compilation:   gcc -Wall -Wextra fifo_reader.c -o fifo_reader
 * =====================================================================================
 */

#include "fifo_common.h"
#include <signal.h>

static volatile int g_keep_running = 1;

static void sigint_handler(int sig) {
    (void)sig;
    g_keep_running = 0;
    printf("\n[PROCESS B] Interrupted. Shutting down reader.\n");
}

static void timeout_handler(int sig) {
    (void)sig;
    fprintf(stderr, "\n[TIMEOUT] Reader timed out waiting for writer process.\n");
    exit(3);
}

static int read_single_message(const char *fifo_path, int is_interactive, int timeout_sec) {
    char buffer[BUFFER_SIZE];
    memset(buffer, 0, sizeof(buffer));

    if (is_interactive) {
        printf("[PROCESS B - READER] Opening FIFO %s with flag O_RDONLY...\n", fifo_path);
        printf("(Waiting for Writer Process A to transmit data...)\n");
        fflush(stdout);
    }

    /* Set up timeout if requested */
    if (timeout_sec > 0) {
        signal(SIGALRM, timeout_handler);
        alarm(timeout_sec);
    }

    /* 1. Open FIFO for reading (blocks until writer process attaches O_WRONLY) */
    int fd = open(fifo_path, O_RDONLY);
    if (fd == -1) {
        if (errno == EINTR) {
            return -1;
        }
        perror("System call open() failed on FIFO");
        return -1;
    }

    if (is_interactive) {
        printf("✓ [PROCESS B] FIFO opened successfully. File descriptor: %d\n", fd);
        printf("[PROCESS B] Reading payload from Shared FIFO queue buffer...\n");
        fflush(stdout);
    }

    /* 2. Read data bytes from FIFO */
    ssize_t bytes_read = read(fd, buffer, sizeof(buffer) - 1);
    if (bytes_read <= 0) {
        if (bytes_read == -1 && errno != EINTR) {
            perror("System call read() failed");
        }
        close(fd);
        /* Failed read: do NOT clear display file prematurely */
        return -1;
    }

    /* Cancel timeout alarm */
    if (timeout_sec > 0) {
        alarm(0);
    }

    /*
     * REQUIREMENT: Immediately after Process B successfully receives the message,
     * clear myfifo_display.txt. Truncates file to 0 bytes without any sleep() or delay,
     * only if matching the received payload to prevent wiping newer messages.
     */
    clear_display_file_if_matching(buffer);

    /* 3. Output received message */
    printf("✓ [PROCESS B] Read %ld bytes from Shared FIFO.\n", (long)bytes_read);
    printf("\n=========================================================\n");
    printf(" [PROCESS B RECEIVED OUTPUT]: \"%s\"\n", buffer);
    printf("=========================================================\n\n");
    fflush(stdout);

    /* 4. Append to persistent message history log */
    append_to_history(buffer, is_interactive ? "Ubuntu Terminal" : "Website Simulator");

    /* 5. Close file descriptor */
    close(fd);

    return 0;
}

int main(int argc, char *argv[]) {
    char fifo_path[PATH_MAX];
    char reader_lock_path[PATH_MAX];
    int lock_fd = -1;
    int timeout_sec = 0;
    int run_once = 0;

    get_fifo_path(fifo_path, sizeof(fifo_path));
    get_reader_lock_path(reader_lock_path, sizeof(reader_lock_path));

    /* Parse optional command-line flags */
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--timeout") == 0 && i + 1 < argc) {
            timeout_sec = atoi(argv[i + 1]);
            run_once = 1;
            i++;
        } else if (strcmp(argv[i], "--once") == 0) {
            run_once = 1;
        }
    }

    /* 1. Acquire exclusive session lock to prevent simultaneous conflicts */
    lock_fd = acquire_session_lock(reader_lock_path);
    if (lock_fd < 0) {
        /* Prints: "FIFO is currently being used by another communication session. Please try again." */
        return 2;
    }

    /* 2. Ensure FIFO exists and is verified */
    if (ensure_fifo_exists(fifo_path, 0) != 0) {
        release_session_lock(lock_fd);
        return 1;
    }

    signal(SIGINT, sigint_handler);

    /* Mode A: Single-shot execution (Backend / Automated scripts) */
    if (run_once) {
        int ret = read_single_message(fifo_path, 0, timeout_sec);
        release_session_lock(lock_fd);
        return (ret == 0) ? 0 : 1;
    }

    /* Mode B: Interactive Ubuntu terminal loop - supports multiple consecutive messages */
    printf("=========================================================\n");
    printf("      LINUX NAMED FIFO READER PROCESS (PROCESS B)       \n");
    printf("=========================================================\n");
    printf("Shared FIFO Target: %s\n", fifo_path);
    printf("Display File Target: %s\n", DISPLAY_FILE_NAME);
    printf("History Log Target: %s\n", HISTORY_FILE_NAME);
    printf("(Press Ctrl+C to terminate reader)\n\n");

    while (g_keep_running) {
        int ret = read_single_message(fifo_path, 1, 0);
        if (ret != 0 || !g_keep_running) {
            break;
        }
        printf("[PROCESS B] Ready for next message...\n");
        printf("---------------------------------------------------------\n");
    }

    release_session_lock(lock_fd);
    printf("[PROCESS B] Closed descriptors. Reader session finished.\n");
    printf("ℹ️ Shared FIFO \"%s\" remains persistent in project directory.\n", fifo_path);

    return 0;
}
