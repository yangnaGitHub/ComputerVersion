#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <iostream>
#include <sys/shm.h>

#define SHMID_BASE 0x12340000
#define MAX_SHM_STRIP 8
#define MAX_THREAD 8

using namespace std;

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

typedef struct{
    int shmid;
    int shmsize;
    int shmoffset;
    void* t_ptr;
    void* c_ptr;
}TRANS_INFO;

typedef struct{
    unsigned char id;
    CAM_DATA thread[MAX_THREAD];
}SHM_DATA;

int get_sh(unsigned int offset, unsigned int sh_size){
    int shmid = shmget(SHMID_BASE+offset, sh_size, IPC_CREAT | 0666);
    #ifdef DEBUG
    printf("get_sh::addr(%x)\n", SHMID_BASE+offset);
    #endif
    if(0 > shmid){
        cout<<"get_sh::shmget error"<<endl;
    }
    return shmid;
}

bool delete_sh(void* g_ptr){
    if(0 > shmdt(g_ptr)){
        cout<<"delete_sh::shmdt error"<<endl;
        return false;
    }
    return true;
}

bool get_sh_ptr(int shmid, void** g_ptr){
    *g_ptr = shmat(shmid, NULL, 0);
    if(*g_ptr == (void*)-1) return false;
    return true;
}

bool remove_sh(int shmid){
    if(shmctl(shmid, IPC_RMID,NULL) < 0){
        cout<<"remove_sh::shmctl error"<<endl;
        return false;
    }
    return true;
}

int get_size(int shmid){
    struct shmid_ds buf;
    if (shmctl(shmid, IPC_STAT, &buf) < 0){
        cout<<"get_size::shmctl error"<<endl;
        return 0;
    }
    return buf.shm_segsz;
}

size_t calc_checksum(char* cc_ptr, int str_len){
    size_t return_val = 0;
    int index = 0;

    while(index < str_len){
        return_val += cc_ptr[index];
        index += 0x80;
    }
    return return_val&0xffffffff;
}

TRANS_INFO* init(int cam_id, int thread_id){
    int camid = cam_id;
    int shmid = get_sh(MAX_SHM_STRIP*cam_id, sizeof(SHM_DATA));
    SHM_DATA* ptr = NULL;
    if(0 > (shmid)){
        cout<<"init::create_sh error"<<endl;
        return NULL;
    }

    if(!get_sh_ptr(shmid, (void**)&(ptr))){
        cout<<"init::get_sh_ptr error"<<endl;
        return NULL;
    }
    TRANS_INFO* info = (TRANS_INFO*)malloc(sizeof(TRANS_INFO));
    memset((void*)info, 0, sizeof(TRANS_INFO));
    info->t_ptr = &((ptr)->thread[thread_id]);
    info->c_ptr = NULL;
    info->shmoffset = MAX_SHM_STRIP*cam_id;
    return info;
}

int get_data_size(TRANS_INFO* info){
    CAM_DATA* t_ptr = (CAM_DATA*)(info->t_ptr);
    size_t data_len = 0;
    if(1 == (t_ptr)->flag){
        if(0 == (t_ptr)->description){//使用案例1,和线程0搭配
            #ifdef DEBUG
            cout<<"get_data_size::file name: "<<(t_ptr)->value<<endl;
            #endif
            info->c_ptr = (t_ptr)->value;
            data_len = strlen((t_ptr)->value);
        }else{////使用案例2,和线程1搭配
            size_t datalen = ((size_t*)(t_ptr->value))[1];
            size_t a_shm_size = ((size_t*)(t_ptr->value))[2];
            size_t checksum = ((size_t*)(t_ptr->value))[3];
            #ifdef DEBUG
            cout<<"get_data_size::datalen: "<<datalen<<" a_shm_size: "<<a_shm_size<<endl;
            #endif
            if((info->shmsize) < a_shm_size){
                if((0 != (info->shmsize)) && (NULL != info->c_ptr)) delete_sh((void*)(info->c_ptr));
                info->shmsize = a_shm_size;
                info->shmid = get_sh(info->shmoffset+(t_ptr)->expandid, info->shmsize);
                if(0 > (info->shmid)){
                    cout<<"get_data_size::create_sh error"<<endl;
                    info->shmsize = 0;
                }
                if(!get_sh_ptr(info->shmid, (void**)&(info->c_ptr))){
                    cout<<"get_data_size::get_sh_ptr error"<<endl;
                    info->shmsize = 0;
                }
            }
            if(info->shmsize){
                data_len = datalen;
            }else{
                data_len = 0;
            }
            #ifdef DEBUG
            printf("%p\n", c_ptr);
            printf("%02x %02x %02x %02x %02x %02x %02x %02x %02x %02x\n", c_ptr[0x0], c_ptr[0x10], c_ptr[0x20], c_ptr[0x30], c_ptr[0x100], c_ptr[0x200], c_ptr[0x300], c_ptr[0x1000], c_ptr[0x2000], c_ptr[0x3000]);
            #endif
            if(datalen && (checksum != calc_checksum((char*)(info->c_ptr), datalen))){
                cout<<"get_data_size::checksum("<<checksum<<") r_checksum("<<calc_checksum((char*)(info->c_ptr), datalen)<<")"<<endl;
                data_len = 0;
            }
        }
        if(0 == data_len){
            memset(t_ptr->value, 0, 128);
            t_ptr->flag = 2;
        }
    }
    return data_len;
}

int get_data(char* dest, TRANS_INFO* info, int data_len){
    memcpy((void*)dest, (void*)(info->c_ptr), data_len);
    return ((CAM_DATA*)(info->t_ptr))->description;
}

bool send_data(char* src, int str_len, char* expand, TRANS_INFO* info){
    bool return_val = false;
    CAM_DATA* t_ptr = (CAM_DATA*)(info->t_ptr);
    if(1 != (t_ptr)->flag){
        return return_val;
    }
    size_t r_len = str_len;
    #ifdef DEBUG
    cout<<"send_data::str_len: "<<str_len<<" "<<expand<<endl;
    #endif

    if(0 == t_ptr->description){
        if((str_len > 128) || (0 > str_len)){
            cout<<"send_data::too long"<<endl;
        }else{
            memset((void*)(info->c_ptr), 0, 128);
            if(0 != str_len) memcpy((void*)(info->c_ptr), (void*)src, str_len);
            return_val = true;
        }
    }else{
        if(str_len > info->shmsize){
            if(0 != info->shmsize){
                delete_sh((void*)(info->c_ptr));
                remove_sh(info->shmid);
            }
            info->shmsize = str_len + 0x100;
            info->shmid = get_sh(info->shmoffset+(t_ptr)->expandid, info->shmsize);
            if(0 > info->shmid){
                cout<<"send_data::create_sh error"<<endl;
                info->shmsize = 0;
            }
            if(!get_sh_ptr(info->shmid, (void**)&(info->c_ptr))){
                cout<<"send_data::get_sh_ptr error"<<endl;
                info->shmsize = 0;
            }
        }
        #ifdef DEBUG
        cout<<"send_data::str_len: "<<str_len<<" new_shm_size: "<<shm_size<<endl;
        #endif
        if(info->shmsize){
            if(0 != str_len){
                memcpy((void*)(info->c_ptr), (void*)src, str_len);
            }else{
                memset((void*)(info->c_ptr), 0, info->shmsize);
            }
            memset(t_ptr->value, 0, 128);
            if(0 != str_len){
                memcpy((void*)(t_ptr->value), (void*)expand, sizeof(size_t));
                memcpy((void*)(t_ptr->value+sizeof(size_t)), (void*)&r_len, sizeof(size_t));
                size_t shmsize = info->shmsize;
                memcpy((void*)(t_ptr->value+2*sizeof(size_t)), (void*)&shmsize, sizeof(size_t));
                size_t checksum = calc_checksum((char*)(info->c_ptr), str_len);
                #ifdef DEBUG
                printf("send_data::checksum(%d)\n", checksum);
                #endif
                memcpy((void*)(t_ptr->value+3*sizeof(size_t)), (void*)&checksum, sizeof(size_t));
            }
            return_val = true;
        }
    }
    t_ptr->flag = 2;
    return return_val;
}
