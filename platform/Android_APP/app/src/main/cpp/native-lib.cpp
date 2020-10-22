#include <jni.h>
#include <string>
#include <android/asset_manager_jni.h>
#include <android/bitmap.h>
#include <android/log.h>
#include "model.h"


model *ocr = new model();

extern "C" JNIEXPORT jstring JNICALL
Java_com_example_myapplication_MainActivity_stringFromJNI(
        JNIEnv* env,
        jobject /* this */) {
    LOGI("loading assetmanager");
    static AAssetManager * mgr = NULL;
    mgr = AAssetManager_fromJava( env, assetManager);

    LOGI("convert bitmap to cv::Mat");
    // convert bitmap to mat
    int *data = NULL;
    AndroidBitmapInfo info = {0};
    AndroidBitmap_getInfo(env, bitmap, &info);
    AndroidBitmap_lockPixels(env, bitmap, (void **) &data);

    // 这里偷懒只写了RGBA格式的转换
    LOGI("info format RGBA ? %d", info.format == ANDROID_BITMAP_FORMAT_RGBA_8888);
    cv::Mat test(info.height, info.width, CV_8UC4, (char*)data); // RGBA
    cv::Mat img_bgr;
    cvtColor(test, img_bgr, CV_RGBA2BGR);

    LOGI("loading model");
    std::string crnn_param = "yolact.param";
    std::string crnn_bin = "yolact.bin";
    int ret = ocr->init(mgr, crnn_param, crnn_bin);
    std::string result;
    if(ret){
        result = "Model loading failed";
        return env->NewStringUTF(result.c_str());
    }
    LOGI("running model");
    ocr->forward(img_bgr, result);
    return env->NewStringUTF(result.c_str());
}