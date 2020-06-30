#ifndef SHMOP_H_INCLUDED
#define SHMOP_H_INCLUDED
#include <signal.h>

typedef struct{
    int shmid;
    int shmsize;
    int shmoffset;
    void* t_ptr;
    void* c_ptr;
}TRANS_INFO;

typedef enum{
    NOT_EXIST_RANGE = 0,
    EXIST_RANGE,
    HINDDEN_OBJECT
}EVENT_TYPE;

typedef struct{
    unsigned char flag;
    unsigned char description;
    unsigned char expandid;
    EVENT_TYPE type;
    char value[128];
    size_t shmsize;
}CAM_DATA;

TRANS_INFO* shm_init(int cam_id, int thread_id);
int shm_get_data_size(TRANS_INFO* info);
int shm_get_data(char* dest, TRANS_INFO* info, int data_len);
bool shm_send_data(char* src, int str_len, char* expand, TRANS_INFO* info);
void shm_stop(TRANS_INFO* info);

#endif // SHMOP_H_INCLUDED
