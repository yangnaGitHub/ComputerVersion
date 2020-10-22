//
// Created by yangna on 20-10-22.
//

#ifndef MASK_APP_MODEL_H
#define MASK_APP_MODEL_H
#include "net.h"
//#include <opencv2/core/core.hpp>
//#include <opencv2/opencv.hpp>

struct Object
{
    cv::Rect_<float> rect;
    int label;
    float prob;
    std::vector<float> maskdata;
    cv::Mat mask;
};

class model {
public:
    model(){};
    ~model(){};
    int init(AAssetManager *mgr, const std::string crnn_param, const std::string crnn_bin);
    int forward(const cv::Mat image, std::string &result);
    //int forward(const std::string image_path, std::string &result);
private:
    ncnn::Net yolact;
    int target_size = 550;
    const float mean_vals[3] = {123.68f, 116.78f, 103.94f};
    const float norm_vals[3] = {1.0 / 58.40f, 1.0 / 57.12f, 1.0 / 57.38f};
};


#endif //MASK_APP_MODEL_H
