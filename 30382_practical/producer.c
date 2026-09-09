#include <stdio.h>
#include <stdlib.h>
#include <sys/ipc.h>
#include <sys/shm.h>

#define SM_NAME "shmfile"
#define NUM_MARKS 5

int main() {
    key_t key;
    int shmid;
    int *marks;

    /* Generate key */
    key = ftok(SM_NAME, 65);

    if (key == -1) {
        perror("ftok");
        exit(1);
    }

    /* Create shared memory */
    shmid = shmget(key, NUM_MARKS * sizeof(int), 0666 | IPC_CREAT);

    if (shmid == -1) {
        perror("shmget");
        exit(1);
    }

    /* Attach shared memory */
    marks = (int *)shmat(shmid, NULL, 0);

    if (marks == (int *)-1) {
        perror("shmat");
        exit(1);
    }

    printf("Enter marks of 5 students:\n");

    for (int i = 0; i < NUM_MARKS; i++) {
        scanf("%d", &marks[i]);
    }
    printf("Producer Process\n");
    printf("------------------\n");

    printf("Marks written to shared memory successfully.\n");

    /* Detach shared memory */
    shmdt(marks);

    return 0;
}
