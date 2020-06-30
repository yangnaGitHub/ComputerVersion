#include "shmop_py.h"
#include <sys/types.h>
#include <signal.h>
//g++ -shared -fPIC shmop_py.c -o libshmop.so
extern "C" {
shm_py op;

void abort_handler(int sig){
    op.stop();
}

unsigned char shm_init(int cam_id, int thread_id){
    return op.init(cam_id, thread_id);
}

int shm_get_data_size(){
    signal(SIGINT, abort_handler);
    return op.get_data_size();
}

int shm_get_data(char* dest){
    return op.get_data(dest);
}

unsigned char shm_send_data(char* src, int str_len, char* expand){
    return op.send_data(src, str_len, expand);
}

void shm_stop(){
    op.stop();
}
}
