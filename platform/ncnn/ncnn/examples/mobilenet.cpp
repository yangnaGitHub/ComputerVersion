#include <iostream>
#include <vector>
#include <string>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/videoio.hpp>
#include <sstream>

#include "net.h"
//#include "mat.h"
#include "platform.h"

#define TEST_COUNT 100
#include <sys/time.h>
double getTime(){
    struct timeval tv;
    char buf[64];
    gettimeofday(&tv,NULL);
    double current = tv.tv_sec;
    return current;
}

struct Object
{
    cv::Rect_<float> rect;
    int label;
    float prob;
};

static void draw_objects(cv::Mat& inputImage, const std::vector<Object>& objects)
{
    static const char* class_name[] = {"background",
        "aeroplane", "bicycle", "bird", "boat",
        "bottle", "bus", "car", "cat", "chair",
        "cow", "diningtable", "dog", "horse",
        "motorbike", "person", "pottedplant",
        "sheep", "sofa", "train", "tvmonitor"};
    
    //cv::Mat image_c = inputImage.clone();

    for(size_t i = 0; i < objects.size(); i++)
    {
        const Object& obj = objects[i];
        cv::rectangle(inputImage, obj.rect, cv::Scalar(50,205,50));

        //std::string text("");
        /*std::stringstream text;
        text << class_name[obj.label];
        text << obj.prob * 100;
        text << "%";

        int baseline = 0;
        cv::Size textSize = cv::getTextSize(text.str(), cv::FONT_HERSHEY_DUPLEX, 0.5, 1, &baseline);

        int x = obj.rect.x;
        int y = obj.rect.y;
        if(y < 0)
            y = 0;
        if(x + textSize.width > image_c.cols)
            x = image_c.cols - textSize.width;
        
        //y + textSize.height for bottom left corner
        cv::rectangle(image_c, cv::Rect(x, y, textSize.width, textSize.height + 5), cv::Scalar(50,205,50), -1);
        cv::putText(image_c, text.str(), cv::Point(x, y + textSize.height), cv::FONT_HERSHEY_DUPLEX, 0.5, cv::Scalar(255,255,255));*/
    }

    cv::imshow("image", inputImage);
    cv::waitKey(1);
}

void main_method(cv::VideoCapture cap){
    ncnn::Net net;
    net.load_param("mobilenetv2_yolov3.param");
    net.load_model("mobilenetv2_yolov3.bin");
    
    const float probThreshold = 0.5;
    const int input_size = 352;
    const float mean_vals[3] = {127.5f, 127.5f, 127.5f};
    const float norm_vals[3] = {0.007843f, 0.007843f, 0.007843f};
    std::vector<Object> objects;
    int index = 0;
    
    double starttime = getTime();
    cv::Mat frame;
    while(true){
        index++;
        if(index == TEST_COUNT) break;
        frame.release();
        cap.read(frame);
        if(frame.empty()){
            std::cerr<<"ERROR! blank frame grabbed\n";
            break;
        }
        ncnn::Mat ncnnImage = ncnn::Mat::from_pixels_resize(frame.data, ncnn::Mat::PIXEL_BGR, frame.cols, frame.rows, input_size, input_size);
        ncnnImage.substract_mean_normalize(mean_vals, norm_vals);
        
        ncnn::Extractor ex = net.create_extractor();
        ex.set_num_threads(4);
        ex.input("data", ncnnImage);

        ncnn::Mat detectRes;
        ex.extract("detection_out", detectRes);

        objects.clear();
        
        for(int i = 0; i < detectRes.h; i++){
            const float* values = detectRes.row(i);
            
            if(values[1] >= probThreshold){
                Object object;
                object.label = values[0];
                object.prob = values[1];
                object.rect.x = values[2] * frame.cols;
                object.rect.y = values[3] * frame.rows;
                object.rect.width = values[4] * frame.cols - object.rect.x;
                object.rect.height = values[5] * frame.rows - object.rect.y;
                //printf("%d %f %f %f %f\n", object.label, object.rect.x, object.rect.y, object.rect.width, object.rect.height);
    
                objects.push_back(object);
            }
        }
        
        draw_objects(frame, objects);
        
        //cv::imshow("image", frame);
        /*if(cv::waitKey(5) >= 0)
            break;*/
    }
    double endtime = getTime();
    printf("%lf, %lf, %lf\n", endtime, starttime, TEST_COUNT/(endtime - starttime));
    cap.release();
}

int main(int argc, char** argv){
    cv::VideoCapture cap;

    //0 = open default camera
    int deviceID = 0;
    //0 = autodetect default API
    int apiID = cv::CAP_ANY;

    //open camera
    cap.open("rtsp://admin:admin12345@192.168.41.7:554/h264");

    if(!cap.isOpened())
    {
        std::cerr<<"ERROR! Unable to open camera\n";
        return -1;
    }
    
    main_method(cap);
    
    return 0;
}