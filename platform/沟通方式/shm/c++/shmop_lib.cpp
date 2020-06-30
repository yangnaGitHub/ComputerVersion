#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <iostream>

#include <vector>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
//export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:.
//g++ shmop_lib.cpp -o main -lopencv_highgui -lopencv_imgproc -lopencv_core -L ./ -lshmop
#include "shmop.h"

using namespace std;

int main(int ragc, char** argv){
    if(false == init(0, 1)){
        cout<<"init error"<<endl;
        return -1;
    }
    int data_size = 0;
    int description = 0;
    char* ptr = NULL;

    char temp[4];
    while(true){
        data_size = get_data_size();
        if(0 == data_size) continue;
        ptr = (char*)malloc(data_size);
        memset(ptr, 0, data_size);
        description = get_data(ptr);
        cout<<"data_size: "<<data_size<<" description: "<<description<<endl;
        if(0 == description){
            cout<<"file name: "<<ptr<<endl;
            int val = 2;
            memset(temp, 0, sizeof(size_t));
            memcpy(temp, (char*)&val, sizeof(size_t));
            send_data(temp, sizeof(size_t), NULL);
        }else if(1 == description){
            vector<unsigned char> buffer;
            cv::Mat image;
            for(int index=0; index<data_size; index++) buffer.push_back(ptr[index]);
            try{
                image = cv::imdecode(buffer, CV_LOAD_IMAGE_COLOR);
            }catch(exception &e){
                cout << "error, at line:" << __LINE__ << endl;
                cout << "error, ---msg:" << e.what() << endl;
            }
            //cv::imshow("yangna", image);
            //cv::waitKey(0);
            cv::rectangle(image, cv::Point(100, 100), cv::Point(300, 300), cv::Scalar(0, 255, 0), 3, 8, 0);


            vector<unsigned char> shm_vec;
            try{
                cv::imencode(".jpg", image, buffer);
            }catch(exception &e){
                cout << "error, at line:" << __LINE__ << endl;
                cout << "error, ---msg:" << e.what() << endl;
            }
            if(ptr) free(ptr);
            size_t r_len = buffer.size();
            ptr = (char*)malloc(r_len);
            memset(ptr, 0, r_len);
            for(int index=0; index<r_len; index++) ptr[index] = buffer[index];
            int val = 1;
            memset(temp, 0, sizeof(size_t));
            memcpy(temp, (char*)&val, sizeof(size_t));
            cout<<"return_data_size: "<<r_len<<endl;
            send_data(ptr, r_len, temp);
        }
    }
    return 0;
}
