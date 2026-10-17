#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <string.h>

int main() {
    int fd[2];
    pid_t pid;
    char buffer[100];

    if (pipe(fd) == -1) {
        perror("Pipe failed");
        return 1;
    }

    pid = fork();

    if (pid < 0) {
        perror("Fork failed");
        return 1;
    }

    if (pid == 0) {
        close(fd[0]);

        char *message = "Velocity: 120 km/h, GPS: 17.3850, 78.4867";

        write(fd[1], message, strlen(message) + 1);
        printf("Child: Telemetry data sent.\n");

        close(fd[1]);
        exit(0);
    } else {
        close(fd[1]);

        read(fd[0], buffer, sizeof(buffer));
        printf("Parent: Received telemetry: %s\n", buffer);
        printf("Parent: Receipt confirmed.\n");

        close(fd[0]);
        wait(NULL);
    }

    return 0;
}
