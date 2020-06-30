#include <stdio.h> 
#ifdef __cplusplus
extern "C"
{
#endif
 
#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libswscale/swscale.h>
#include <libavutil/imgutils.h>
#ifdef __cplusplus
};
#endif
 
int main()
{
	//文件格式上下文
	AVFormatContext	*pFormatCtx;
	int		i = 0, videoindex;
	AVCodecContext	*pCodecCtx;
	AVCodec			*pCodec;
	AVFrame	*pFrame, *pFrameYUV;
	unsigned char *out_buffer;
	//AVPacket *packet;
        AVPacket packet;
 
	int y_size;
	int ret, got_picture;
	struct SwsContext *img_convert_ctx;
	char filepath[] = "rtsp://admin:admin12345@192.168.41.7:554/h264";
	//FILE *fp_yuv = fopen("output.yuv", "wb+");
	av_register_all();
	avformat_network_init();
	pFormatCtx = avformat_alloc_context();
	if(avformat_open_input(&pFormatCtx, filepath, NULL, NULL) != 0) 
	{
		printf("Couldn't open input stream.\n");
		return -1;
	}
	//读取一部分视音频数据并且获得一些相关的信息
	if (avformat_find_stream_info(pFormatCtx, NULL) < 0) 
	{
		printf("Couldn't find stream information.\n");
		return -1;
	}
 
	//查找视频编码索引
        printf("%d\n", pFormatCtx->nb_streams);
	videoindex = -1;
	for (i = 0; i < pFormatCtx->nb_streams; i++)
	{
		if (pFormatCtx->streams[i]->codec->codec_type == AVMEDIA_TYPE_VIDEO)
		{
			videoindex = i;
			break;
		}
	}
 
	if (videoindex == -1)
	{
		printf("Didn't find a video stream.\n");
		return -1;
	}
 
	//编解码上下文
	pCodecCtx = pFormatCtx->streams[videoindex]->codec;
	printf("%d\n", pCodecCtx->codec_id);
	//查找解码器
	pCodec = avcodec_find_decoder(pCodecCtx->codec_id);
	if (pCodec == NULL) 
	{
		printf("Codec not found.\n");
		return -1;
	}
	//打开解码器
	if (avcodec_open2(pCodecCtx, pCodec, NULL) < 0) 
	{
		printf("Could not open codec.\n");
		return -1;
	}
 
	//申请AVFrame，用于原始视频
	/*pFrame = av_frame_alloc();
	//申请AVFrame，用于RGB视频
	pFrameRGB = av_frame_alloc();
	

	//分配内存，用于图像格式转换
	out_buffer = (unsigned char *)av_malloc(av_image_get_buffer_size(AV_PIX_FMT_YUV420P, pCodecCtx->width, pCodecCtx->height, 1));
	av_image_fill_arrays(pFrameYUV->data, pFrameYUV->linesize, out_buffer,AV_PIX_FMT_YUV420P, pCodecCtx->width, pCodecCtx->height, 1);
	//Output Info-----------------------------
	printf("--------------- File Information ----------------\n");
	//手工调试函数，输出tbn、tbc、tbr、PAR、DAR的含义
	av_dump_format(pFormatCtx, 0, argv[1], 0);
	printf("-------------------------------------------------\n");
 
	//申请转换上下文
	img_convert_ctx = sws_getContext(pCodecCtx->width, pCodecCtx->height, pCodecCtx->pix_fmt,
	pCodecCtx->width, pCodecCtx->height, AV_PIX_FMT_YUV420P, SWS_BICUBIC, NULL, NULL, NULL);
 
	//读取数据
	while (av_read_frame(pFormatCtx, packet) >= 0) 
	{
		if (packet->stream_index == videoindex) 
		{
			ret = avcodec_decode_video2(pCodecCtx, pFrame, &got_picture, packet);
			if (ret < 0) 
			{
				printf("Decode Error.\n");
				return -1;
			}
 
			if (got_picture >= 1) 
			{
				//成功解码一帧
				sws_scale(img_convert_ctx, (const unsigned char* const*)pFrame->data, pFrame->linesize, 0, pCodecCtx->height,
					pFrameYUV->data, pFrameYUV->linesize);//转换图像格式
 
				y_size = pCodecCtx->width*pCodecCtx->height;
				fwrite(pFrameYUV->data[0], 1, y_size, fp_yuv);    //Y 
				fwrite(pFrameYUV->data[1], 1, y_size / 4, fp_yuv);  //U
				fwrite(pFrameYUV->data[2], 1, y_size / 4, fp_yuv);  //V
				printf("Succeed to decode 1 frame!\n");
			}
			else
			{
				//未解码到一帧，可能时结尾B帧或延迟帧，在后面做flush decoder处理
			}
		}
		av_free_packet(packet);
	}
 
	//flush decoder
	//FIX: Flush Frames remained in Codec
	while (true) 
	{
		if (!(pCodec->capabilities & CODEC_CAP_DELAY))
			return 0;
 
		ret = avcodec_decode_video2(pCodecCtx, pFrame, &got_picture, packet);
		if (ret < 0)
		{
			break;
		}
		if (!got_picture)
		{
			break;
		}
 
		sws_scale(img_convert_ctx, (const unsigned char* const*)pFrame->data, pFrame->linesize, 0, pCodecCtx->height,
			pFrameYUV->data, pFrameYUV->linesize);
 
		int y_size = pCodecCtx->width*pCodecCtx->height;
		fwrite(pFrameYUV->data[0], 1, y_size, fp_yuv);    //Y 
		fwrite(pFrameYUV->data[1], 1, y_size / 4, fp_yuv);  //U
		fwrite(pFrameYUV->data[2], 1, y_size / 4, fp_yuv);  //V
		printf("Flush Decoder: Succeed to decode 1 frame!\n");
	}
 
	sws_freeContext(img_convert_ctx);
	av_frame_free(&pFrameYUV);
	av_frame_free(&pFrame);
	avcodec_close(pCodecCtx);
	avformat_close_input(&pFormatCtx);
	fclose(fp_yuv);*/
 
    return 0;
}
