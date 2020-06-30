#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <iostream>

#include <vector>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
//g++ shmop.cpp -o shmop -lopencv_highgui -lopencv_imgproc -lopencv_core
/*libopencv_videostab.so.2.4.9
libopencv_ts.so.2.4.9
libopencv_superres.so.2.4.9
libopencv_stitching.so.2.4.9
libopencv_ocl.so.2.4.9
libopencv_gpu.so.2.4.9
libopencv_contrib.so.2.4.9
libopencv_photo.so.2.4.9
libopencv_legacy.so.2.4.9
libopencv_video.so.2.4.9
libopencv_objdetect.so.2.4.9
libopencv_ml.so.2.4.9
libopencv_calib3d.so.2.4.9
libopencv_features2d.so.2.4.9
libopencv_highgui.so.2.4.9
libopencv_imgproc.so.2.4.9
libopencv_flann.so.2.4.9
libopencv_core.so.2.4.9*/

using namespace std;

//shm start
#include <sys/types.h>
#include <signal.h>
#include <sys/shm.h>
#define SHMID_BASE 0x12340000
#define MAX_SHM_STRIP 8
#define MAX_THREAD 8

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

int get_sh(unsigned int offset, unsigned int sh_size){
    //cout<<SHMID_BASE+offset<<endl;
    int shmid = shmget(SHMID_BASE+offset, sh_size, IPC_CREAT | 0666);
    if(0 > shmid){
        cout<<"get_sh:shmget error"<<endl;
    }
    return shmid;
}

bool delete_sh(void* ptr){
    if(0 > shmdt(ptr)){
        cout<<"delete_sh:shmdt error"<<endl;
        return false;
    }
    return true;
}

bool get_sh_ptr(int shmid, void** ptr){
    *ptr = shmat(shmid, NULL, 0);
    if(*ptr == (void*)-1) return false;
    return true;
}

bool remove_sh(int shmid){
    if(shmctl(shmid, IPC_RMID,NULL) < 0){
		cout<<"remove_sh:shmctl error"<<endl;
		return false;
	}
	return true;
}

SHM_DATA* ptr = NULL;
void abort_handler(int sig){
    delete_sh((void*)ptr);
    _exit(0);
}
//shm end

int main(int ragc, char** argv){
    //shm start
    int cam_id = 0;
    int shmid = get_sh(MAX_SHM_STRIP*cam_id, sizeof(SHM_DATA));
    if(0 > shmid){
        cout<<"create_sh error"<<endl;
        return 0;
    }

    if(!get_sh_ptr(shmid, (void**)&ptr)){
        cout<<"get_sh_ptr error"<<endl;
        return 0;
    }
    signal(SIGINT, abort_handler);
    //shm end
    int thread_id = 1;
    size_t datalen = 0;
    size_t shm_size = 0;
    unsigned char* c_ptr = NULL;
    CAM_DATA* t_ptr = &(ptr->thread[thread_id]);//第几个算法线程和他对接

    while(true){
        //printf("%d\n", ptr->id);
        if(1 == t_ptr->flag){


            if(0 == t_ptr->description){//使用案例1,和线程0搭配
                cout<<"file name: "<<t_ptr->value<<endl;

                //your function

                //if return value
                int val = 1;
                strncpy(t_ptr->value, (char*)&val, sizeof(val));
            }else if(1 == t_ptr->description){////使用案例2,和线程1搭配
                datalen = ((size_t*)t_ptr->value)[0];
                //cout<<"datalen: "<<datalen<<" shm_size: "<<shm_size<<endl;
                if(shm_size < datalen){
                    if(shm_size){
                        delete_sh((void*)c_ptr);
                    }
                    shmid = get_sh(MAX_SHM_STRIP*cam_id+t_ptr->expandid, datalen);
                    if(0 > shmid){
                        cout<<"create_sh error"<<endl;
                        return 0;
                    }
                    shm_size = datalen;
                    if(!get_sh_ptr(shmid, (void**)&c_ptr)){
                        cout<<"get_sh_ptr error"<<endl;
                        return 0;
                    }
                }
                vector<unsigned char> buffer;
                for(int index=0; index<datalen; index++) buffer.push_back(c_ptr[index]);
                cv::Mat image = cv::imdecode(buffer, CV_LOAD_IMAGE_COLOR);
                cv::imshow("yangna", image);
                //cv::waitKey(0);

                //your function

                //if return value
                int val = 1;//图片或是boxes
                size_t returnlen = 10;
                memset(t_ptr->value, 0, 128);
                strncpy(t_ptr->value, (char*)&val, sizeof(val));
                memset(c_ptr, 0, datalen);
                //构造返回结果
                strncpy(t_ptr->value+sizeof(val), (char*)&returnlen, sizeof(returnlen));
                //构造返回值c_ptr
            }
            t_ptr->flag = 2;
        }
    }
    return 0;
}
