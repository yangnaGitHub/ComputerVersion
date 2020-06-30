#include "shmop_py.h"
#include <sys/types.h>
#include <signal.h>
//g++ -shared -fPIC shmop_py.cpp -o libshmop.so

TRANS_INFO* shm_init(int cam_id, int thread_id){
    return init(cam_id, thread_id);
}

int shm_get_data_size(TRANS_INFO* info){
    return get_data_size(info);
}

int shm_get_data(char* dest, TRANS_INFO* info, int data_len){
    return get_data(dest, info, data_len);
}

bool shm_send_data(char* src, int str_len, char* expand, TRANS_INFO* info){
    return send_data(src, str_len, expand, info);
}

void shm_stop(TRANS_INFO* info){
    if(info){
        free(info);
        info = NULL;
    }
    return ;
}

