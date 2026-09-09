#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

int main()
{
    int pipefd[2];
    pid_t producer, consumer;

    if (pipe(pipefd) == -1)
    {
        perror("pipe");
        exit(1);
    }


    producer = fork();

    if (producer == -1)
    {
        perror("fork");
        exit(1);
    }

    if (producer == 0)
    {

        close(pipefd[0]);


        dup2(pipefd[1], STDOUT_FILENO);

        close(pipefd[1]);


        execlp("ls", "ls", "-l", NULL);

        perror("execlp");
        exit(1);
    }


    consumer = fork();

    if (consumer == -1)
    {
        perror("fork");
        exit(1);
    }

    if (consumer == 0)
    {

        close(pipefd[1]);

        dup2(pipefd[0], STDIN_FILENO);

        close(pipefd[0]);

        execlp("grep", "grep", ".c", NULL);

        perror("execlp");
        exit(1);
    }

    close(pipefd[0]);
    close(pipefd[1]);

    waitpid(producer, NULL, 0);
    waitpid(consumer, NULL, 0);

    printf("Pipeline execution completed.\n");

    return 0;
}
