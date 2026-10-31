/*
 * =====================================================================================
 *  Filename:      fifo_common.h
 *  Description:   Shared configuration, path resolution, FIFO verification,
 *                 session locking, display file synchronization, and message logging
 *                 for Linux FIFO IPC.
 *  Course:        Operating Systems and System Programming (OSSP)
 * =====================================================================================
 */

#ifndef FIFO_COMMON_H
#define FIFO_COMMON_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/file.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include <libgen.h>
#include <limits.h>

#define FIFO_NAME           "myfifo"
#define DISPLAY_FILE_NAME   "myfifo_display.txt"
#define HISTORY_FILE_NAME   "received_messages.txt"
#define LOCK_READER_NAME    ".fifo_reader.lock"
#define LOCK_WRITER_NAME    ".fifo_writer.lock"
#define BUFFER_SIZE         512

/* Windows mirror path when running inside WSL environment */
#define WIN_MIRROR_DISPLAY_PATH "/mnt/c/Users/G Jashwanth Reddy/Downloads/DBMS Project/OCTO_OSSP-project/linux-implementation/myfifo_display.txt"

/*
 * Dynamic Absolute Path Resolution:
 * Resolves the directory where the binary or source files are located so that
 * running from any working directory always targets the exact same shared FIFO.
 */
static inline const char *resolve_project_path(const char *filename, char *buffer, size_t buf_size) {
    char exe_path[PATH_MAX];
    ssize_t len = readlink("/proc/self/exe", exe_path, sizeof(exe_path) - 1);
    if (len > 0) {
        exe_path[len] = '\0';
        char *dir = dirname(exe_path);
        snprintf(buffer, buf_size, "%s/%s", dir, filename);
        return buffer;
    }

    /* Fallback: Check if running inside linux-implementation or from project root */
    struct stat st;
    if (stat("fifo_writer.c", &st) == 0 || stat("fifo_reader.c", &st) == 0) {
        snprintf(buffer, buf_size, "%s", filename);
    } else {
        snprintf(buffer, buf_size, "linux-implementation/%s", filename);
    }
    return buffer;
}

static inline const char *get_fifo_path(char *buffer, size_t buf_size) {
    return resolve_project_path(FIFO_NAME, buffer, buf_size);
}

static inline const char *get_display_file_path(char *buffer, size_t buf_size) {
    return resolve_project_path(DISPLAY_FILE_NAME, buffer, buf_size);
}

static inline const char *get_history_file_path(char *buffer, size_t buf_size) {
    return resolve_project_path(HISTORY_FILE_NAME, buffer, buf_size);
}

static inline const char *get_reader_lock_path(char *buffer, size_t buf_size) {
    return resolve_project_path(LOCK_READER_NAME, buffer, buf_size);
}

static inline const char *get_writer_lock_path(char *buffer, size_t buf_size) {
    return resolve_project_path(LOCK_WRITER_NAME, buffer, buf_size);
}

/*
 * Verify that path exists and is actually a POSIX FIFO.
 * If it already exists, verify using stat() and S_ISFIFO().
 * Never overwrite a regular file.
 * If it does not exist, create it using mkfifo().
 */
static inline int ensure_fifo_exists(const char *path, int verbose) {
    struct stat st;

    if (stat(path, &st) == 0) {
        if (!S_ISFIFO(st.st_mode)) {
            fprintf(stderr, "Error: '%s' exists but is NOT a FIFO special file! Refusing to overwrite.\n", path);
            return -1;
        }
        if (verbose) {
            printf("ℹ️ Verified existing Linux FIFO node at: %s\n", path);
        }
        return 0;
    }

    if (errno == ENOENT) {
        if (mkfifo(path, 0666) == -1) {
            if (errno == EEXIST) {
                return 0;
            }
            perror("System call mkfifo() failed");
            return -1;
        }
        if (verbose) {
            printf("✓ System call mkfifo() created shared FIFO node at: %s\n", path);
        }
        return 0;
    }

    perror("stat() failed on FIFO path");
    return -1;
}

/*
 * Acquire exclusive non-blocking lock.
 */
static inline int acquire_session_lock(const char *lock_file_path) {
    int fd = open(lock_file_path, O_RDWR | O_CREAT, 0666);
    if (fd == -1) {
        perror("Failed to open lock file");
        return -1;
    }

    if (flock(fd, LOCK_EX | LOCK_NB) != 0) {
        if (errno == EWOULDBLOCK || errno == EAGAIN) {
            fprintf(stderr, "FIFO is currently being used by another communication session. Please try again.\n");
        } else {
            perror("flock() failed");
        }
        close(fd);
        return -1;
    }

    return fd;
}

static inline void release_session_lock(int lock_fd) {
    if (lock_fd >= 0) {
        flock(lock_fd, LOCK_UN);
        close(lock_fd);
    }
}

/*
 * Update the temporary display file (myfifo_display.txt) with the exact message in transit.
 * Also synchronizes the Windows project folder file if running in WSL.
 */
static inline void update_display_file(const char *message) {
    char path[PATH_MAX];
    get_display_file_path(path, sizeof(path));

    FILE *f = fopen(path, "w");
    if (f) {
        if (message && strlen(message) > 0) {
            fprintf(f, "%s\n", message);
        }
        fflush(f);
        fclose(f);
    }

    /* Synchronize Windows mirror if path exists */
    struct stat st;
    if (stat(WIN_MIRROR_DISPLAY_PATH, &st) == 0) {
        FILE *fw = fopen(WIN_MIRROR_DISPLAY_PATH, "w");
        if (fw) {
            if (message && strlen(message) > 0) {
                fprintf(fw, "%s\n", message);
            }
            fflush(fw);
            fclose(fw);
        }
    }
}

/*
 * Clear the temporary display file unconditionally (used during cleanup or error abort).
 */
static inline void clear_display_file(void) {
    char path[PATH_MAX];
    get_display_file_path(path, sizeof(path));
    FILE *f = fopen(path, "w");
    if (f) fclose(f);

    struct stat st;
    if (stat(WIN_MIRROR_DISPLAY_PATH, &st) == 0) {
        FILE *fw = fopen(WIN_MIRROR_DISPLAY_PATH, "w");
        if (fw) fclose(fw);
    }
}

/*
 * Clear the temporary display file IMMEDIATELY after Process B confirms receipt.
 * Ensures synchronization: only clears if the file currently matches the message
 * that Process B just received, preventing a previous message's cleanup from
 * erasing a newer message.
 */
static inline void clear_display_file_if_matching(const char *received_msg) {
    if (!received_msg || strlen(received_msg) == 0) {
        return; /* Do not clear if read failed or was empty */
    }

    char path[PATH_MAX];
    get_display_file_path(path, sizeof(path));

    /* 1. Clear local Linux file immediately if matching */
    FILE *f = fopen(path, "r+");
    if (f) {
        char current[BUFFER_SIZE];
        memset(current, 0, sizeof(current));
        if (fgets(current, sizeof(current), f) != NULL) {
            current[strcspn(current, "\r\n")] = '\0';
            if (strcmp(current, received_msg) == 0) {
                if (ftruncate(fileno(f), 0) != 0) {
                    FILE *tmp = freopen(path, "w", f);
                    (void)tmp;
                }
            }
        }
        fclose(f);
    }

    /* 2. Clear Windows mirror file immediately if matching */
    struct stat st;
    if (stat(WIN_MIRROR_DISPLAY_PATH, &st) == 0) {
        FILE *fw = fopen(WIN_MIRROR_DISPLAY_PATH, "r+");
        if (fw) {
            char current[BUFFER_SIZE];
            memset(current, 0, sizeof(current));
            if (fgets(current, sizeof(current), fw) != NULL) {
                current[strcspn(current, "\r\n")] = '\0';
                if (strcmp(current, received_msg) == 0) {
                    if (ftruncate(fileno(fw), 0) != 0) {
                        FILE *tmp = freopen(WIN_MIRROR_DISPLAY_PATH, "w", fw);
                        (void)tmp;
                    }
                }
            }
            fclose(fw);
        }
    }
}

/*
 * Append received message to received_messages.txt for persistent history tracking.
 */
static inline void append_to_history(const char *message, const char *source) {
    char hist_path[PATH_MAX];
    get_history_file_path(hist_path, sizeof(hist_path));

    FILE *f = fopen(hist_path, "a");
    if (!f) return;

    time_t now = time(NULL);
    char time_str[64];
    struct tm *tm_info = localtime(&now);
    strftime(time_str, sizeof(time_str), "%Y-%m-%d %H:%M:%S", tm_info);

    fprintf(f, "[%s] [%s] %s\n", time_str, source, message);
    fflush(f);
    fclose(f);
}

#endif /* FIFO_COMMON_H */
