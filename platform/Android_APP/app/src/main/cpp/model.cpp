//
// Created by yangna on 20-10-22.
//
//https://zhuanlan.zhihu.com/p/137453394
#include "model.h"

int model::init(AAssetManager *mgr, const std::string crnn_param, const std::string crnn_bin)
{
    int ret1 = yolact.load_param(mgr, crnn_param.c_str());
    int ret2 = yolact.load_model(mgr, crnn_bin.c_str());
    LOGI("ret1 is %d, ret2 is %d", ret1, ret2);
    return (ret1||ret2);
}

int model::forward(const cv::Mat image, std::string &result){
    ncnn::Mat in = ncnn::Mat::from_pixels_resize(image.data, ncnn::Mat::PIXEL_BGR2RGB, image.cols, image.rows, target_size, target_size);
    in.substract_mean_normalize(mean_vals, norm_vals);
    //LOGI("input size : %d, %d, %d", in.w, in.h, in.c);
    ncnn::Extractor ex = yolact.create_extractor();
    ex.input("input.1", in);

    ncnn::Mat maskmaps;
    ncnn::Mat mask;
    ncnn::Mat confidence;

    ex.extract("619", maskmaps); // 138x138x32
    ex.extract("818", mask);       // maskdim 32 x 19248
    ex.extract("820", confidence); // 81 x 19248
    int num_class = confidence.w;
    int num_priors = confidence.h;

    const float confidence_thresh = 0.05f;
    const float nms_threshold = 0.5f;
    const int keep_top_k = 200;

    std::vector<std::vector<Object> > class_candidates;
    class_candidates.resize(num_class);

    for (int i = 0; i < num_priors; i++)
    {
        const float* conf = confidence.row(i);
        const float* maskdata = mask.row(i);

        // find class id with highest score
        // start from 1 to skip background
        int label = 0;
        float score = 0.f;
        for (int j = 1; j < num_class; j++)
        {
            float class_score = conf[j];
            if (class_score > score)
            {
                label = j;
                score = class_score;
            }
        }

        // ignore background or low score
        if (label == 0 || score <= confidence_thresh)
            continue;

        // append object
        Object obj;
        obj.label = label;
        obj.prob = score;
        obj.maskdata = std::vector<float>(maskdata, maskdata + mask.w);

        class_candidates[label].push_back(obj);
    }

    /*objects.clear();
    for (int i = 0; i < (int)class_candidates.size(); i++)
    {
        std::vector<Object>& candidates = class_candidates[i];

        qsort_descent_inplace(candidates);

        std::vector<int> picked;
        nms_sorted_bboxes(candidates, picked, nms_threshold);

        for (int j = 0; j < (int)picked.size(); j++)
        {
            int z = picked[j];
            objects.push_back(candidates[z]);
        }
    }

    qsort_descent_inplace(objects);

    // keep_top_k
    if (keep_top_k < (int)objects.size())
    {
        objects.resize(keep_top_k);
    }

    // generate mask
    for (int i = 0; i < objects.size(); i++)
    {
        Object& obj = objects[i];

        cv::Mat mask(maskmaps.h, maskmaps.w, CV_32FC1);
        {
            mask = cv::Scalar(0.f);

            for (int p = 0; p < maskmaps.c; p++)
            {
                const float* maskmap = maskmaps.channel(p);
                float coeff = obj.maskdata[p];
                float* mp = (float*)mask.data;

                // mask += m * coeff
                for (int j = 0; j < maskmaps.w * maskmaps.h; j++)
                {
                    mp[j] += maskmap[j] * coeff;
                }
            }
        }

        cv::Mat mask2;
        cv::resize(mask, mask2, cv::Size(img_w, img_h));

        // crop obj box and binarize
        obj.mask = cv::Mat(img_h, img_w, CV_8UC1);
        {
            obj.mask = cv::Scalar(0);

            for (int y = 0; y < img_h; y++)
            {
                if (y < obj.rect.y || y > obj.rect.y + obj.rect.height)
                    continue;

                const float* mp2 = mask2.ptr<const float>(y);
                uchar* bmp = obj.mask.ptr<uchar>(y);

                for (int x = 0; x < img_w; x++)
                {
                    if (x < obj.rect.x || x > obj.rect.x + obj.rect.width)
                        continue;

                    bmp[x] = mp2[x] > 0.5f ? 255 : 0;
                }
            }
        }
    }*/
    return 0;
}