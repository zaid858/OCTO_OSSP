#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <signal.h>
#include <string.h>

#define MAX_CLIENTS 3

pid_t handlers[MAX_CLIENTS];

char client_to_server[MAX_CLIENTS][50] = {
    "client1_to_server",
    "client2_to_server",
    "client3_to_server"
};

char server_to_client[MAX_CLIENTS][50] = {
    "server_to_client1",
    "server_to_client2",
    "server_to_client3"
};

void sigchld_handler(int sig)
{
    while (waitpid(-1, NULL, WNOHANG) > 0)
    {
        printf("Child process terminated.\n");
    }
}

void client_handler(int client_no)
{
    int read_fd, write_fd;
    char message[200];

    printf("Handler %d started. PID = %d\n",
           client_no + 1, getpid());

    read_fd = open(client_to_server[client_no], O_RDONLY);

    if (read_fd == -1)
    {
        perror("open client_to_server");
        exit(1);
    }

    write_fd = open(server_to_client[client_no], O_WRONLY);

    if (write_fd == -1)
    {
        perror("open server_to_client");
        exit(1);
    }

    while (1)
    {
        memset(message, 0, sizeof(message));

        int n = read(read_fd, message, sizeof(message) - 1);

        if (n <= 0)
        {
            break;
        }

        message[n] = '\0';

        printf("Client %d sent: %s\n",
               client_no + 1, message);

        if (strncmp(message, "exit", 4) == 0)
        {
            char response[] = "Server: Goodbye Client!\n";
            write(write_fd, response, strlen(response));
            break;
        }

        char response[250];

        snprintf(response, sizeof(response),
                 "Server received from Client %d: %s",
                 client_no + 1, message);

        write(write_fd, response, strlen(response));

        kill(getppid(), SIGUSR1);
    }

    close(read_fd);
    close(write_fd);

    printf("Handler %d exiting.\n", client_no + 1);

    exit(0);
}

void sigusr1_handler(int sig)
{
    printf("Server received SIGUSR1 notification.\n");
}

int main()
{
    int i;

    printf("====================================\n");
    printf("     MULTI-CLIENT FIFO SERVER\n");
    printf("====================================\n");

    printf("Server PID: %d\n\n", getpid());

    for (i = 0; i < MAX_CLIENTS; i++)
    {
        mkfifo(client_to_server[i], 0666);
        mkfifo(server_to_client[i], 0666);
    }

    signal(SIGCHLD, sigchld_handler);
    signal(SIGUSR1, sigusr1_handler);

    printf("All FIFOs created.\n");

    for (i = 0; i < MAX_CLIENTS; i++)
    {
        handlers[i] = fork();

        if (handlers[i] == -1)
        {
            perror("fork");
            exit(1);
        }

        if (handlers[i] == 0)
        {
            client_handler(i);
        }
    }

    printf("All handler processes created.\n");
    printf("Waiting for clients...\n\n");

    while (1)
    {
        pause();
    }

    return 0;
}
