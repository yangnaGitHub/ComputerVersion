#include <stdio.h>
#include <iostream>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>

extern "C"
{
#include <libavformat/avformat.h>
#include <libavcodec/avcodec.h>
#include <libswscale/swscale.h>
}
 
#pragma comment(lib, "avcodec.lib")
#pragma comment(lib, "avformat.lib")
#pragma comment(lib, "avutil.lib")	
#pragma comment(lib ,"swscale.lib")
 
using namespace std;
using namespace cv;

void PRINT_ERROR(char* printstr){
	cout << printstr << endl;
	exit(0);
}

Mat avframe_to_cvmat(AVFrame *frame)
{
	AVFrame dst;
	memset(&dst, 0, sizeof(dst));
	int width = frame->width, height = frame->height;
	cv::Mat temp = cv::Mat(width, height, CV_8UC3);
	dst.data[0] = (uint8_t *)temp.data;
	avpicture_fill((AVPicture *)&dst, dst.data[0], AV_PIX_FMT_BGR24, width, height);

	struct SwsContext *convert_ctx = NULL;
	AVPixelFormat src_pixfmt = (AVPixelFormat)frame->format;
	AVPixelFormat dst_pixfmt = AV_PIX_FMT_BGR24;
	convert_ctx = sws_getContext(width, height, src_pixfmt, width, height, dst_pixfmt, SWS_FAST_BILINEAR, NULL, NULL, NULL);
	sws_scale(convert_ctx, frame->data, frame->linesize, 0, height, dst.data, dst.linesize);
	sws_freeContext(convert_ctx);
	return temp;
}

int main(int argc, const char * argv[]){
	AVFormatContext *pFormatCtx = NULL;//结构体AVFormatContext:包含码流参数较多
	char filepath[] = "rtsp://admin:admin12345@192.168.41.7:554/h264";//码流的获取路径
	av_register_all();//注册编解码器
	avformat_network_init();//加载socket库以及网络加密协议相关的库
	if(avformat_open_input(&pFormatCtx, filepath, NULL, NULL) != 0) PRINT_ERROR("avformat_open_input");
	if(avformat_find_stream_info(pFormatCtx, NULL) < 0) PRINT_ERROR("avformat_find_stream_info");
	av_dump_format(pFormatCtx, 0, filepath, false);//手工调试函数，看到pFormatCtx->streams的内容
	int videoStream = -1;
 
	for(int index = 0; index < pFormatCtx->nb_streams; index++){
		if(pFormatCtx->streams[index]->codec->codec_type == AVMEDIA_TYPE_VIDEO){
			videoStream = index;
			break;
		}
	}

	if(-1 == videoStream) PRINT_ERROR("videoStream");
	AVCodecContext *pCodecCtx = pFormatCtx->streams[videoStream]->codec;
	AVCodec *pCodec = avcodec_find_decoder((AVCodecID)28);//查找解码器
	if(pCodec == NULL) PRINT_ERROR("avcodec_find_decoder");
	if(avcodec_open2(pCodecCtx, pCodec, 0) < 0) PRINT_ERROR("avcodec_open2");
	AVFrame* pFrame = av_frame_alloc();//分配内存
	AVPacket packet;
	int ret, got_picture;
	while(true){
		if(av_read_frame(pFormatCtx, &packet) >= 0){
			if(packet.stream_index == videoStream){
				ret = avcodec_decode_video2(pCodecCtx, pFrame, &got_picture, &packet);//开始解码
				if(ret < 0) PRINT_ERROR("avcodec_decode_video2");
				if(got_picture){
					Mat test = avframe_to_cvmat(pFrame);
					//imwrite("test.jpg", test);
				}
			}
			av_free_packet(&packet);
		}
	}
 	av_free(pFrame);
	avcodec_close(pCodecCtx);
	avformat_close_input(&pFormatCtx);
	return 0;
}
