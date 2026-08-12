#include<stdio.h>
#include<unistd.h>
#include<sys/wait.h>
#include<sys/types.h>

int main(){
    int num;
    pid_t pid;
    long long factorial=1;

    printf("Enter a number: ");
    scanf("%d",&num);

    pid=fork();

    if(pid<0){
        printf("Fork failed\n");
        return 1;
    }

    if(pid==0){
        for(int i=1;i<=num;i++)
            factorial=factorial*i;

        printf("Child Process: Factorial of %d = %lld\n",num,factorial);
    }
    else{
        wait(NULL);
        printf("Parent Process: Child process completed\n");
    }

    return 0;
}

