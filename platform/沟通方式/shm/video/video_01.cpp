#include <stdio.h>
#include <pthread.h>
#include <iostream>
#include <string>

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>

#include <json/json.h>

#include <algorithm>
#include <iosfwd>
#include <memory>
#include <string>
#include <utility>
#include <vector>

#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <signal.h>
#include <sys/shm.h>
#include <dirent.h>

#include "../include/MpiPerson.h"
#include "../include/video.h"
#include "../include/ReadIni.h"
#include "ZBase64.h"
#include "httpClient.h"

Global global;
std::string g_str_send_video_path;

void makeDir(string dir);
int mskeDirectory(std::string strPathName_);
string getTime();
string getDay();
string getSendMessageTime();

void *detectImg(void *i);
void *sendImg(void *i);
int send_face_detect(string face_base64Pic);

#define CREATE_THREAD(x,y,z) pthread_create(x, NULL, y, z)
int get_sh(unsigned int offset, unsigned int sh_size){
    cout<<SHMID_BASE+offset<<endl;
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
unsigned char* c_ptr = NULL;
void abort_handler(int sig){
    delete_sh((void*)ptr);
    if(c_ptr != NULL){
        delete_sh((void*)c_ptr);
    }
    _exit(0);
}

//description==0的线程,就是传最多128个字符,可以是文件名字,也可以是其他的字串
void *func_0(void *args){
    int t_index = 0;
    CAM_DATA* t_ptr = &(ptr->thread[t_index]);
    while(true){
        if(global.nDetectFlag & (1<<t_index)) continue;
        if(global.mDetectImg.empty()){
            global.nDetectFlag |= (1<<t_index);
            continue;
        }
        //核心位置开始(不要修改核心之外的)

        //要发送的string,你修改的第一个地方
        string imgPath = "/home/yangna/deepblue/temp/" + to_string(global.nCameraID)+".jpg";
        //string imgPath = "/home/server/project/" + to_string(global.nCameraID)+".jpg";
        /*是否要画出检测框
        cv::rectangle(global.mDrawImage, cv::Point(global.minX, global.minY), cv::Point(global.maxX, global.maxY), cv::Scalar(0, 255, 0), 3, 8, 0);*/
        //第一个地方修改结束


        cv::imwrite(imgPath.c_str(), global.mDetectImg);
        int result = 0;
        unsigned int r_count = 0;
        while(true){
            if(0 == t_ptr->flag){
                memset(t_ptr->value, 0, 256);
                strncpy(t_ptr->value, imgPath.c_str(), imgPath.length());
                t_ptr->description = 0;//传的名字
                t_ptr->flag = 1;
            }else if(1 == t_ptr->flag){
                sleep(0.01);
            }else if(2 == t_ptr->flag){
                //得到的结果,你要porting args，你要修改的第二个地方

                //基本用例
                result = ((int*)t_ptr->value)[0];
                cout<<"result: "<<result<<endl;
                ((THREAD_DATA*)args)->occur = (result & 1);
                ((THREAD_DATA*)args)->type = NOT_EXIST_RANGE;

                //第二个地方修改结束
                t_ptr->flag = 0;
                break;
            }
            r_count++;
            if(100000 < r_count){
                break;
            }
        }

        //核心位置结束(不要修改核心之外的)
        if(((THREAD_DATA*)args)->occur && (START_SAVE_VIDEO != global.nSaveVideo)){
            global.nSaveVideo = START_SAVE_VIDEO;
        }
        global.nDetectFlag |= (1<<t_index);
    }
}

//description==1的线程,传图片等大数据,需要新开shm
void *func_1(void *args){
    int t_index = 1;
    CAM_DATA* t_ptr = &(ptr->thread[t_index]);

    size_t shm_size = 0;
    int shmid = 0;

    while(true){
        if(global.nDetectFlag & (1<<t_index)) continue;
        if(global.mDetectImg.empty()){
            global.nDetectFlag |= (1<<t_index);
            continue;
        }
        //核心位置开始(不要修改核心之外的)
        unsigned int r_count = 0;
        while(true){
            if(0 == t_ptr->flag){
                vector<unsigned char> shm_vec;
                //要修改的第一个地方,传的图片的对象,若是传其他的大数据需要重新构造要传的数据
                imencode(".jpg", global.mDetectImg, shm_vec);
                size_t datalen = shm_vec.size();
                if(datalen > shm_size){
                    if(0 != shm_size){
                        delete_sh((void*)c_ptr);
                        remove_sh(shmid);
                    }
                    shm_size = datalen + 0x100;
                    shmid = get_sh(MAX_SHM_STRIP*global.nCameraID+t_index, shm_size);
                    if(0 > shmid){
                        cout<<"func_1::get_sh error"<<endl;
                        shm_size = 0;
                        continue;
                    }
                    if(!get_sh_ptr(shmid, (void**)&c_ptr)){
                        cout<<"func_1::get_sh_ptr error"<<endl;
                        shm_size = 0;
                        continue;
                    }
                    cout<<"datalen: "<<datalen<<" shm_size: "<<shm_size<<endl;
                }
                memset(c_ptr, 0, shm_size);
                for(int index=0; index<datalen; index++) *(c_ptr+index) = shm_vec[index];

                memset(t_ptr->value, 0, 256);
                strncpy(t_ptr->value+sizeof(size_t), (char*)&datalen, sizeof(size_t));//要传的数据的大小
                strncpy(t_ptr->value+2*sizeof(size_t), (char*)&shm_size, sizeof(size_t));
                t_ptr->description = 1;//传的大数据
                t_ptr->flag = 1;
                t_ptr->expandid = t_index;//新申请的SHM的offset
                //cout<<"datalen: "<<datalen<<endl;
            }else if(1 == t_ptr->flag){
                sleep(0.01);
            }else if(2 == t_ptr->flag){
                //要修改的第2个地方开始,根据你的返回来构造args
                //使用用例
                size_t result_len = ((size_t*)(t_ptr->value))[1];
                size_t new_shm_size = ((size_t*)(t_ptr->value))[2];
                //size_t result_len = ((size_t*)((unsigned long)(t_ptr->value) + sizeof(size_t)))[0];
                cout<<"result_len: "<<result_len<<" new_shm_size: "<<new_shm_size<<endl;
                ((THREAD_DATA*)args)->ptr_len = result_len;
                if(((THREAD_DATA*)args)->ptr) free(((THREAD_DATA*)args)->ptr);//delete[]((THREAD_DATA*)args)->ptr);
                ((THREAD_DATA*)args)->ptr = (unsigned char*)malloc(result_len);//new unsigned char(result_len);
                ((THREAD_DATA*)args)->occur = ((size_t*)t_ptr->value)[0] & 0xff;//我的用例1是图片，2是boxes,你可以自己合理使用
                ((THREAD_DATA*)args)->type = NOT_EXIST_RANGE;

                if(new_shm_size > shm_size){
                    if(0 != shm_size) delete_sh((void*)c_ptr);
                    shm_size = new_shm_size;
                    shmid = get_sh(MAX_SHM_STRIP*global.nCameraID+t_index, shm_size);
                    if(0 > shmid){
                        cout<<"func_1::get_sh error"<<endl;
                        shm_size = 0;
                        continue;
                    }
                    if(!get_sh_ptr(shmid, (void**)&c_ptr)){
                        cout<<"func_1::get_sh_ptr error"<<endl;
                        shm_size = 0;
                        continue;
                    }
                }
                for(int index=0; index<result_len; index++) ((THREAD_DATA*)args)->ptr[index] = *(c_ptr+index);
                //要修改的第2个地方结束
                t_ptr->flag = 0;
                break;
            }
            r_count++;
            if(100000 < r_count){
                break;
            }
        }

        //核心位置结束(不要修改核心之外的)
        if(((THREAD_DATA*)args)->occur && (START_SAVE_VIDEO != global.nSaveVideo)){
            global.nSaveVideo = START_SAVE_VIDEO;
        }
        global.nDetectFlag |= (1<<t_index);
    }
}

void *func_2(void *args){
    int t_index = 2;
    CAM_DATA* t_ptr = &(ptr->thread[t_index]);
    while(true){
        if(global.nDetectFlag & (1<<t_index)) continue;
        if(global.mDetectImg.empty()){
            global.nDetectFlag |= (1<<t_index);
            continue;
        }
        //your method start


        //edit here


        //your method end
        if(((THREAD_DATA*)args)->occur && (START_SAVE_VIDEO != global.nSaveVideo)){
            global.nSaveVideo = START_SAVE_VIDEO;
        }
        global.nDetectFlag |= (1<<t_index);
    }
}

void *func_3(void *args){
    int t_index = 3;
    CAM_DATA* t_ptr = &(ptr->thread[t_index]);
    while(true){
        if(global.nDetectFlag & (1<<t_index)) continue;
        if(global.mDetectImg.empty()){
            global.nDetectFlag |= (1<<t_index);
            continue;
        }
        //your method start


        //edit here


        //your method end
        if(((THREAD_DATA*)args)->occur && (START_SAVE_VIDEO != global.nSaveVideo)){
            global.nSaveVideo = START_SAVE_VIDEO;
        }
        global.nDetectFlag |= (1<<t_index);
    }
}

void *func_4(void *args){
    int t_index = 4;
    CAM_DATA* t_ptr = &(ptr->thread[t_index]);
    while(true){
        if(global.nDetectFlag & (1<<t_index)) continue;
        if(global.mDetectImg.empty()){
            global.nDetectFlag |= (1<<t_index);
            continue;
        }
        //your method start


        //edit here


        //your method end
        if(((THREAD_DATA*)args)->occur && (START_SAVE_VIDEO != global.nSaveVideo)){
            global.nSaveVideo = START_SAVE_VIDEO;
        }
        global.nDetectFlag |= (1<<t_index);
    }
}

void *func_5(void *args){
    int t_index = 5;
    CAM_DATA* t_ptr = &(ptr->thread[t_index]);
    while(true){
        if(global.nDetectFlag & (1<<t_index)) continue;
        if(global.mDetectImg.empty()){
            global.nDetectFlag |= (1<<t_index);
            continue;
        }
        //your method start


        //edit here


        //your method end
        if(((THREAD_DATA*)args)->occur && (START_SAVE_VIDEO != global.nSaveVideo)){
            global.nSaveVideo = START_SAVE_VIDEO;
        }
        global.nDetectFlag |= (1<<t_index);
    }
}

void *func_6(void *args){
    int t_index = 6;
    CAM_DATA* t_ptr = &(ptr->thread[t_index]);
    while(true){
        if(global.nDetectFlag & (1<<t_index)) continue;
        if(global.mDetectImg.empty()){
            global.nDetectFlag |= (1<<t_index);
            continue;
        }
        //your method start


        //edit here


        //your method end
        if(((THREAD_DATA*)args)->occur && (START_SAVE_VIDEO != global.nSaveVideo)){
            global.nSaveVideo = START_SAVE_VIDEO;
        }
        global.nDetectFlag |= (1<<t_index);
    }
}

void *func_7(void *args){
    int t_index = 7;
    CAM_DATA* t_ptr = &(ptr->thread[t_index]);
    while(true){
        if(global.nDetectFlag & (1<<t_index)) continue;
        if(global.mDetectImg.empty()){
            global.nDetectFlag |= (1<<t_index);
            continue;
        }
        //your method start


        //edit here


        //your method end
        if(((THREAD_DATA*)args)->occur && (START_SAVE_VIDEO != global.nSaveVideo)){
            global.nSaveVideo = START_SAVE_VIDEO;
        }
        global.nDetectFlag |= (1<<t_index);
    }
}

void send_to_remote(THREAD_DATA* d_thread){
    Json::Value jsonItem;
    Json::Value jsonArrayvalue[MAX_THREAD];
    bool _bsafe_statue = true;
    ZBase64 zBase64;
	CHttpClient httpClient;

    for(int index=0; index<MAX_THREAD; index++){
        if(d_thread->occur){
            //cout<<"send_to_remote: "<<index<<" "<<d_thread->occur<<endl;
            if(_bsafe_statue){
                _bsafe_statue = false;
            }
            jsonArrayvalue[index]["event_type"] = d_thread->type;
            jsonArrayvalue[index]["event_count"] = d_thread->e_count;
            jsonArrayvalue[index]["personId"] = d_thread->personId;
            jsonItem["events"].append(jsonArrayvalue[index]);
            cout<<"d_thread->ptr_len: "<<d_thread->ptr_len<<endl;
            if(d_thread->ptr_len){
                if(1 == d_thread->occur){
                    vector<unsigned char> buffer;
                    for(int index=0; index<d_thread->ptr_len; index++) buffer.push_back((d_thread->ptr)[index]);
                    cv::Mat image = cv::imdecode(buffer, CV_LOAD_IMAGE_COLOR);
                    //cv::imshow("yangna", image);
                    //cv::waitKey(0);
                }else if(2 == d_thread->occur){
                }
                if(d_thread->ptr){
                    //delete[]d_thread->ptr;
                    free(d_thread->ptr);
                    d_thread->ptr = NULL;
                }
            }
        }
        d_thread++;
    }

    if (_bsafe_statue == false){
        if (global.mDrawImage.empty()){
            return;
        }
        cv::Mat _event_img;
        cv::resize(global.mDrawImage, _event_img, cv::Size(640,360), 0, 0, cv::INTER_LINEAR);
        if (_event_img.empty()){
            return;
        }
        vector<uchar> vecImg3;
        cv::imencode(".jpg", _event_img, vecImg3);
        string base64Pic = zBase64.Encode(vecImg3.data(), vecImg3.size());
        jsonItem["result_image"] = base64Pic.c_str();
        jsonItem["camera_num"] = global.nCameraID;
        string _str_time_now = getSendMessageTime();
        jsonItem["event_time"] = _str_time_now.c_str();
        jsonItem["event_video"] = g_str_send_video_path.c_str();
        //natasha edit
        /*string response;
        cout << jsonItem.toStyledString().length() << endl;
        httpClient.Post(global.strRecordUrl.c_str(), jsonItem.toStyledString().c_str(), response);
        cout << "end send video : " << global.nSaveVideo << endl;
        cout << "record response : " << response.c_str() << endl;*/
        global.is_mkdir_video_path = false;
    }
}

int main(int argc, char**argv){
    try{
        /*string jsonInfo = argv[1];
		cout << "jsonInfo: " << jsonInfo.c_str() << endl;
        Json::Reader jReader;
		Json::Value jObject;

		jReader.parse(jsonInfo.c_str(), jObject);

		global.nCameraID = jObject["camera_num"].asInt();
		global.strLiveUrl = jObject["live_url"].asString();
		global.strRecordUrl = jObject["record_url"].asString();
		global.rtsp = jObject["rtsp"].asString();
		global.minX = jObject["coordinate"]["minX"].asInt()*3;
		global.minY = jObject["coordinate"]["minY"].asInt()*3;
		global.maxX = jObject["coordinate"]["maxX"].asInt()*3;
		global.maxY = jObject["coordinate"]["maxY"].asInt()*3;*/

		global.nCameraID = 0;
		global.strLiveUrl = "";
		global.strRecordUrl = "";
		global.rtsp = "/home/yangna/yangna/code/object_detection/darknet/2.mp4";
		global.minX = 0;
		global.minY = 0;
		global.maxX = 1920;
		global.maxY = 1080;
        global.nSaveVideo = EXCEPTION;
		global.nSendFlag = READY_SEND;

        //不同的摄像头不同的算法运行
        //算法在thead0和thread1=>值就是3
        //算法在thead0和thread2=>值就是5
        int ready_detect = 0;
        switch(global.nCameraID){
        case 0:
            ready_detect = 3;
            break;
        case 1:
            ready_detect = 3;
            break;
        default:
            break;
        }
        global.nDetectFlag = ready_detect;
        //cout<<"ready_detect: "<<ready_detect<<endl;

        //打开摄像头
        cv::VideoCapture capture;
		cv::Mat img;
        try{
			capture.open(global.rtsp.c_str());
		}
		catch (...){
			cout << "打开摄像机/视频失败\n,请检测您的rtsp地址和视频文件\n" << endl;
		}

        //创建共享内存
		int shmid = get_sh(MAX_SHM_STRIP*global.nCameraID, sizeof(SHM_DATA));
        if(0 > shmid){
            cout<<"create_sh error"<<endl;
            return 0;
        }

        if(!get_sh_ptr(shmid, (void**)&ptr)){
            cout<<"get_sh_ptr error"<<endl;
            return 0;
        }
        ptr->id = 0x10;//设置ID,决定共享内存的地址

        signal(SIGINT, abort_handler);//ctrl-c中断执行函数

        pthread_t threads[MAX_THREAD];
        THREAD_DATA d_thread[MAX_THREAD];
        memset(d_thread, 0, sizeof(THREAD_DATA)*MAX_THREAD);
        void* (*func)(void*) = NULL;
        for(int index=0; index<MAX_THREAD; index++){
            if(ready_detect & (1<<index)){
                //cout<<"thread id: "<<index<<endl;
                switch(index){
                case 0:
                    func = func_0;
                    break;
                case 1:
                    func = func_1;
                    break;
                case 2:
                    func = func_2;
                    break;
                case 3:
                    func = func_3;
                    break;
                case 4:
                    func = func_4;
                    break;
                case 5:
                    func = func_5;
                    break;
                case 6:
                    func = func_6;
                    break;
                case 7:
                    func = func_7;
                    break;
                default:
                    func = NULL;
                    break;
                }
                if(func){
                    int rc = CREATE_THREAD(&threads[index], func, (void *)&(d_thread[index]));
                    if (rc){
                        cout << "Error:无法创建线程," << rc << endl;
                        exit(-1);
                    }
                }
            }
        }

		pthread_t sendThreads[1];
		try{
			pthread_create(&sendThreads[1], NULL, sendImg, 0);
		}
		catch (...){
			cout << "error line :" << __LINE__ << endl;
		}

        cv::VideoWriter writer;
		int count = -1;
		global.is_mkdir_video_path = false;

        while (true){
			capture >> img;
			while (img.empty()){
				capture.open(global.rtsp.c_str());
				if (capture.isOpened()){
					capture >> img;
					break;
				}
				cv::waitKey(1000 * 5);
			}

			if (global.nDetectFlag == ready_detect && !img.empty()){
                if(global.nSaveVideo != START_SAVE_VIDEO){
                    send_to_remote(d_thread);
                    img.copyTo(global.mDetectImg);
                    img.copyTo(global.mDrawImage);
                    memset(d_thread, 0, sizeof(THREAD_DATA)*MAX_THREAD);
                    global.nDetectFlag = 0;
                }
			}
			if (global.nSendFlag == READY_SEND && !img.empty()){
				img.copyTo(global.mSendImg);
				global.nSendFlag = SEND;
			}

			if (img.empty())
				continue;

			if (global.nSaveVideo == START_SAVE_VIDEO){
				cv::Mat resizeImg;
				if(global.is_mkdir_video_path == false){
					//string _strVideoDir = "/home/server/environment/JAVA_ENVIRONMENT/apache/webapps/" + getDay() + "/";
                    string _strVideoDir = "/home/yangna/deepblue/temp" + getDay() + "/";
                    makeDir(_strVideoDir);
                    g_str_send_video_path = _strVideoDir + getTime() + "-" + to_string(global.nCameraID) + ".mkv";
                    global.is_mkdir_video_path = true;
				}

				cv::resize(img, resizeImg, cv::Size(640, 360), 0, 0, cv::INTER_LINEAR);
				if(count < 0){
					cout << "start save video : " << g_str_send_video_path << endl;
					writer.open(g_str_send_video_path.c_str(), CV_FOURCC('M', 'J', 'P', 'G'), 25, cv::Size(640, 360));
					count = 0;
				}

				writer << resizeImg;
				++count;
				if(count > 125){
					writer.release();
					count = -1;
					global.nSaveVideo = STOP_SAVE_VIDEO;
				}
			}
			cv::waitKey(10);
		}
    }catch (exception &e){
		cout << "error, at line:" << __LINE__ << endl;
		cout << "error, ---msg:" << e.what() << endl;
	}
	catch (...){
		cout << "exception" << endl;
	}
	system("pause");
	return 0;
}

std::string videofile_to_base64string(std::string video_path_)
{

	ZBase64 _zBase64;
	unsigned char *pVideoData = NULL;
	FILE *_fp = fopen(video_path_.c_str(), "r");

	// 把文件指针移动到文件末尾统计一下文件大小
	fseek(_fp, 0L, SEEK_END);
	int flen = ftell(_fp);
	std::cout << " file length : " << flen << endl;
	pVideoData = (unsigned char *)malloc(flen + 1);

	// 把文件指针移动到文件的开始的地方
	fseek(_fp, 0L, SEEK_SET);
	fread(pVideoData, flen, 1, _fp);
	pVideoData[flen] = 0;
	std::string strVideoData = _zBase64.Encode(pVideoData, flen);
	std::cout << " base64 length : " << strVideoData.length() << endl;
	fclose(_fp);
	return strVideoData;
}

// 把直播图片传给后台，后台进行直播显示（绑定摄像机ID）
void *sendImg(void *i)
{
    //natasha edit
	/*std::cout << " sendImg" << std::endl;

	ZBase64 zBase64;
	CHttpClient httpClient;

	while (true)
	{
		if (global.nSendFlag == SEND)
		{
			cv::Mat img;

			// 缩放图片的尺寸为原来的三分之一为640x480的分辨率。
			if (global.mSendImg.empty())
			{
				global.nSendFlag == READY_SEND;
				continue;
			}
			cv::resize(global.mSendImg, img, cv::Size(640, 360), 0, 0, cv::INTER_LINEAR);

			std::vector<uchar> vecImg;
			cv::imencode(".jpg", img, vecImg);
			std::string base64Pic = zBase64.Encode(vecImg.data(), vecImg.size());

			Json::Value jsonItem;
			jsonItem["cameraId"] = global.nCameraID;
			jsonItem["snapPhoto"] = base64Pic.c_str();

			std::string response;
			httpClient.Post(global.strLiveUrl.c_str(), jsonItem.toStyledString().c_str(), response);
			Json::Value j_return_value;
			Json::Reader j_read_value;

			j_read_value.parse(response.c_str(), j_return_value);
			int _json_msg_return_state = j_return_value["result"].asInt();
			std::string _json_return_str_msg = j_return_value["msg"].asString();

			// 这里是调试用，实战项目可以不用，这里发生错误的时候会打印错误消息
			if (_json_msg_return_state != 1)
			{
				std::cout << "live image send error\n------------------\n|\n|\n|\n|" << std::endl;
				std::cout << _json_return_str_msg.c_str() << std::endl;
				std::cout << "live image send error\n------------------\n|\n|\n|\n|" << std::endl;
			}
			//std::cout << "live reponse : " << response.c_str() << std::endl;
			global.nSendFlag = READY_SEND;
		}
		cv::waitKey(80);
	}

	std::cout << "send  image  close" << std::endl;*/
	return 0;
}

string getTime()
{
	struct timeval tv;
	char buf[64];
	//char timeBuf[70];
	gettimeofday(&tv, NULL);
	strftime(buf, sizeof(buf) - 1, "%Y%m%d%H%M%S", localtime(&tv.tv_sec));
	sprintf(buf, "%s%03d", buf, (int)(tv.tv_usec / 1000));
	return buf;
}

string getSendMessageTime()
{
	struct timeval tv;
	char buf[64];
	//char timeBuf[70];
	gettimeofday(&tv, NULL);
	strftime(buf, sizeof(buf) - 1, "%F %T", localtime(&tv.tv_sec));
	//sprintf(buf,"%s%03d",buf,(int)(tv.tv_usec / 1000));
	return buf;
}

string getDay()
{
	struct timeval tv;
	char buf[64];
	gettimeofday(&tv, NULL);
	strftime(buf, sizeof(buf) - 1, "%Y%m%d", localtime(&tv.tv_sec));
	return buf;
}

void makeDir(string dir)
{

	uint32_t dirPathLen = dir.length();
	if (dirPathLen > 2000)
	{
		printf("xx\nxxxxxx\nxxxxx\nxxx\n");
		return;
	}
	char tmpDirPath[2000] = {0};
	for (uint32_t i = 0; i < dirPathLen; ++i)
	{
		tmpDirPath[i] = dir[i];
		if (tmpDirPath[i] == '\\' || tmpDirPath[i] == '/')
		{
			if (access(tmpDirPath, 0) != 0)
			{
				int32_t ret = mkdir(tmpDirPath, 0777);
			}
			else
			{
				continue;
			}
		}
		else
		{
			continue;
		}
	}
}

int mskeDirectory(std::string strPathName_)
{
	char DirName[256];
	const char *sPathName = strPathName_.c_str();
	strcpy(DirName, sPathName);
	int i, len = strlen(DirName);
	for (i = 1; i < len; i++)
	{
		if (DirName[i] == '/')
		{
			DirName[i] = 0;
			if (access(DirName, NULL) != 0)
			{
				if (mkdir(DirName, 0755) == -1)
				{
					printf("mkdir   error\n");
					return -1;
				}
			}
			DirName[i] = '/';
		}
	}

	return 0;
}
