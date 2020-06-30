#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
//export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.
//g++ shmop_lib.cpp -o main -lopencv_highgui -lopencv_imgproc -lopencv_core -L ./ -lshmop
#include "shmop.h"


int main(int ragc, char** argv){
    if(0 == shm_init(0, 1)){
        printf("init error\n");
        return -1;
    }
    return 0;
}
