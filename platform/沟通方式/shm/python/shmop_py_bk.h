#include <stdio.h>
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
}CAM_DATA;

typedef struct{
    unsigned char id;
    CAM_DATA thread[MAX_THREAD];
}SHM_DATA;

class shm_py{
private:
    int shmid;
    int camid;
    int description;
    int data_len;
    size_t shm_size;

    SHM_DATA* ptr = NULL;
    CAM_DATA* t_ptr = NULL;
    char* c_ptr = NULL;
    char* s_ptr = NULL;

    int get_sh(unsigned int offset, unsigned int sh_size){
        #ifdef DEBUG
        printf("get_sh::addr(%x)\n", SHMID_BASE+offset)
        #endif
        int shmid = shmget(SHMID_BASE+offset, sh_size, IPC_CREAT | 0666);
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
public:
    bool init(int cam_id, int thread_id){
        camid = cam_id;
        shmid = get_sh(MAX_SHM_STRIP*cam_id, sizeof(SHM_DATA));
        if(0 > (shmid)){
            cout<<"init::create_sh error"<<endl;
            return false;
        }

        if(!get_sh_ptr(shmid, (void**)&(ptr))){
            cout<<"init::get_sh_ptr error"<<endl;
            return false;
        }
        t_ptr = &((ptr)->thread[thread_id]);
        shm_size = 0;
        return true;
    }

    int get_data_size(){
        while(true){
            if(1 == (t_ptr)->flag){
                data_len = 0;
                description = (t_ptr)->description;
                if(0 == (t_ptr)->description){//使用案例1,和线程0搭配
                    #ifdef DEBUG
                    cout<<"get_data_size::file name: "<<(t_ptr)->value<<endl;
                    #endif
                    s_ptr = (t_ptr)->value;
                    data_len = strlen((t_ptr)->value);
                }else{////使用案例2,和线程1搭配
                    size_t datalen = ((size_t*)(t_ptr->value))[1];
                    size_t a_shm_size = ((size_t*)(t_ptr->value))[2];
                    size_t checksum = ((size_t*)(t_ptr->value))[3];
                    #ifdef DEBUG
                    cout<<"get_data_size::datalen: "<<datalen<<" a_shm_size: "<<a_shm_size<<endl;
                    #endif
                    if(shm_size < a_shm_size){
                        if(0 != shm_size) delete_sh((void*)(c_ptr));
                        shm_size = a_shm_size;
                        shmid = get_sh(MAX_SHM_STRIP*camid+(t_ptr)->expandid, shm_size);
                        if(0 > shmid){
                            cout<<"get_data_size::create_sh error"<<endl;
                            shm_size = 0;
                        }
                        if(!get_sh_ptr(shmid, (void**)&(c_ptr))){
                            cout<<"get_data_size::get_sh_ptr error"<<endl;
                            shm_size = 0;
                        }
                    }
                    if(shm_size){
                        s_ptr = c_ptr;
                        data_len = datalen;
                    }else{
                        data_len = 0;
                    }
                    #ifdef DEBUG
                    printf("%p\n", c_ptr);
                    printf("%02x %02x %02x %02x %02x %02x %02x %02x %02x %02x\n", c_ptr[0x0], c_ptr[0x10], c_ptr[0x20], c_ptr[0x30], c_ptr[0x100], c_ptr[0x200], c_ptr[0x300], c_ptr[0x1000], c_ptr[0x2000], c_ptr[0x3000]);
                    #endif
                    if(datalen && (checksum != calc_checksum(c_ptr, datalen))){
                        cout<<"get_data_size::checksum("<<checksum<<") r_checksum("<<calc_checksum(s_ptr, datalen)<<")"<<endl;
                        data_len = 0;
                    }
                }
                if(0 == data_len){
                    memset(t_ptr->value, 0, 128);
                    t_ptr->flag = 2;
                }
                return data_len;
            }
        }
    }

    int get_data(char* dest){
        memcpy((void*)dest, (void*)s_ptr, data_len);
        return description;
    }

    bool send_data(char* src, int str_len, char* expand){
        bool return_val = false;
        if(1 != (t_ptr)->flag){
            return return_val;
        }
        size_t r_len = str_len;
        #ifdef DEBUG
        cout<<"send_data::str_len: "<<str_len<<" "<<expand<<endl;
        #endif

        if(0 == description){
            if((str_len > 128) || (0 > str_len)){
                cout<<"send_data::too long"<<endl;
            }else{
                memset((void*)s_ptr, 0, data_len);
                if(0 != str_len) memcpy((void*)s_ptr, (void*)src, str_len);
                return_val = true;
            }
        }else{
            if(str_len > shm_size){
                if(0 != shm_size){
                    delete_sh((void*)(c_ptr));
                    remove_sh(shmid);
                }
                shm_size = str_len + 0x100;
                shmid = get_sh(MAX_SHM_STRIP*camid+(t_ptr)->expandid, shm_size);
                if(0 > shmid){
                    cout<<"send_data::create_sh error"<<endl;
                    shm_size = 0;
                }
                if(!get_sh_ptr(shmid, (void**)&(c_ptr))){
                    cout<<"send_data::get_sh_ptr error"<<endl;
                    shm_size = 0;
                }
            }
            #ifdef DEBUG
            cout<<"send_data::str_len: "<<str_len<<" new_shm_size: "<<shm_size<<endl;
            #endif
            if(shm_size){
                if(0 != str_len){
                    memcpy((void*)c_ptr, (void*)src, str_len);
                }else{
                    memset((void*)c_ptr, 0, shm_size);
                }
                memset(t_ptr->value, 0, 128);
                if(0 != str_len){
                    memcpy((void*)(t_ptr->value), (void*)expand, sizeof(size_t));
                    memcpy((void*)(t_ptr->value+sizeof(size_t)), (void*)&r_len, sizeof(size_t));
                    memcpy((void*)(t_ptr->value+2*sizeof(size_t)), (void*)&shm_size, sizeof(size_t));
                    size_t checksum = calc_checksum(c_ptr, str_len);
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

    void stop(){
        if(ptr != NULL){
            delete_sh((void*)ptr);
        }
        if(c_ptr != NULL){
            delete_sh((void*)c_ptr);
        }
        _exit(0);
    }
};
