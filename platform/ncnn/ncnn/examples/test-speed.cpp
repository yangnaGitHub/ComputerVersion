// Tencent is pleased to support the open source community by making ncnn available.
//
// Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
//
// Licensed under the BSD 3-Clause License (the "License"); you may not use this file except
// in compliance with the License. You may obtain a copy of the License at
//
// https://opensource.org/licenses/BSD-3-Clause
//
// Unless required by applicable law or agreed to in writing, software distributed
// under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
// CONDITIONS OF ANY KIND, either express or implied. See the License for the
// specific language governing permissions and limitations under the License.

#include <stdio.h>
#include <algorithm>
#include <vector>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>

#include "platform.h"
#include "net.h"
#if NCNN_VULKAN
#include "gpu.h"
#endif // NCNN_VULKAN

#define TEST_COUNT 5000
#include <sys/time.h>
double getTime(){
    struct timeval tv;
    char buf[64];
    gettimeofday(&tv,NULL);
    double current = tv.tv_sec + (tv.tv_usec / 1000);
    return current;
}

static int detect_test(const cv::Mat& bgr)
{
    ncnn::Net testnet;

#if NCNN_VULKAN
    testnet.opt.use_vulkan_compute = true;
#endif // NCNN_VULKAN

    testnet.load_param("test.param");
    testnet.load_model("test.bin");
    const float mean_vals[3] = {104.f, 117.f, 123.f};
    double starttime = getTime();
    for(int index = 0; index < TEST_COUNT; index++){
        //printf("%d\n", index);
        ncnn::Mat in = ncnn::Mat::from_pixels_resize(bgr.data, ncnn::Mat::PIXEL_BGR, bgr.cols, bgr.rows, 227, 227);
        in.substract_mean_normalize(mean_vals, 0);
        ncnn::Extractor ex = testnet.create_extractor();
        ex.input("data", in);
        ncnn::Mat out;
        ex.extract("prob", out);
    }
    double endtime = getTime();
    printf("%lf\n", TEST_COUNT/(endtime - starttime));
    
    return 0;
}

int main(int argc, char** argv)
{
    if (argc != 2)
    {
        fprintf(stderr, "Usage: %s [imagepath]\n", argv[0]);
        return -1;
    }

    const char* imagepath = argv[1];

    cv::Mat m = cv::imread(imagepath, 1);
    if (m.empty())
    {
        fprintf(stderr, "cv::imread %s failed\n", imagepath);
        return -1;
    }

#if NCNN_VULKAN
    ncnn::create_gpu_instance();
#endif // NCNN_VULKAN

    detect_test(m);

#if NCNN_VULKAN
    ncnn::destroy_gpu_instance();
#endif // NCNN_VULKAN

    return 0;
}
