#include <gst/gst.h>

//gcc basic-tutorial-2.c -o basic-tutorial-2 `pkg-config --cflags --libs gstreamer-1.0`
//./basic-tutorial-2

int main (int argc, char *argv[])
{
  GstElement *pipeline, *source, *filter, *sink;
  GstBus *bus;
  GstMessage *msg;
  GstStateChangeReturn ret;

  /* Initialize GStreamer */
  gst_init (&argc, &argv);

  /*创建Element
  第一个参数是element的类型,可以通过这个字符串,找到对应的类型,从而创建element对象
  第二个参数指定了创建element的名字,如果第二个参数为NULL,GStreamer内部会为该element自动生成一个唯一的名字
  没有保存创建element的对象指针时,可以通过gst_bin_get_by_name从pipeline中取得该element的对象指针
  
  videotestsrc是一个source element,用于产生视频数据,通常用于调试
  timeoverlay是一个filter-like element,可以在视频数据中叠加一个时间字符串
  autovideosink一个sink element,用于自动选择视频输出设备,创建视频显示窗口,并显示其收到的数据
  */
  source = gst_element_factory_make ("videotestsrc", "source");
  filter = gst_element_factory_make ("timeoverlay", "filter");
  sink = gst_element_factory_make ("autovideosink", "sink");

  /*创建Pipeline
  Pipeline通过gst_pipeline_new创建,参数为pipeline的名字
  */
  pipeline = gst_pipeline_new ("test-pipeline");

  if (!pipeline || !source || !filter || !sink) {
    g_printerr ("Not all elements could be created.\n");
    return -1;
  }

  /*将多个element加入到pipeline中,将element连接起来
  只有被加入到同一个bin的element才能够被连接在一起,在连接前,将element加入到pipeline/bin中
  
  pipeline会提供播放所必须的时钟以及对消息的处理,要把创建的element添加到pipeline中
  pipeline是继承自bin,所有bin的方法都可以应用于pipeline,通过相应的宏(这里是GST_BIN)来将子类转换为父类,宏内部会对其做类型检查
  使用gst_bin_add_many将多个element加入到pipeline中,函数接受任意多个参数,最后以NULL表示参数列表的结束,如果一次只加入一个,可使用gst_bin_add函数
  在将element加入bin后,将其连接起来才能完成相应的功能,由于有多个element,所以使用gst_element_link_many,element会根据参数的顺序依次将element连接起来
  */
  gst_bin_add_many (GST_BIN (pipeline), source, filter, sink, NULL);
  if (gst_element_link_many (source, filter, sink, NULL) != TRUE) {
    g_printerr ("Elements could not be linked.\n");
    gst_object_unref (pipeline);
    return -1;
  }

  /*设置element属性
  大部分的element都有自己的属性,有的只能被读取,这种属性常用于查询element的状态,有的同时支持修改,这种属性常用于控制element的行为
  GstElement继承于GObject,GObject对象系统提供了g_object_get()用于读取属性,g_object_set()用于修改属性,g_object_set()支持以NULL结束的属性-值的键值对,可一次修改element的多个属性
  g_object_set()来修改videotestsrc的pattern属性,pattern属性可以控制测试图像的类型
  可以通过gst-inspect-1.0 videotestsrc命令来查看pattern所支持的所有值
  */
  g_object_set (source, "pattern", 0, NULL);

  /*设置播放状态
  */
  ret = gst_element_set_state (pipeline, GST_STATE_PLAYING);
  if (ret == GST_STATE_CHANGE_FAILURE) {
    g_printerr ("Unable to set the pipeline to the playing state.\n");
    gst_object_unref (pipeline);
    return -1;
  }

  /*等待播放结束*/
  bus = gst_element_get_bus (pipeline);
  msg = gst_bus_timed_pop_filtered (bus, GST_CLOCK_TIME_NONE, GST_MESSAGE_ERROR | GST_MESSAGE_EOS);

  /*打印错误消息*/
  if (msg != NULL) {
    GError *err;
    gchar *debug_info;

    switch (GST_MESSAGE_TYPE (msg)) {
      case GST_MESSAGE_ERROR:
        gst_message_parse_error (msg, &err, &debug_info);
        g_printerr ("Error received from element %s: %s\n",
            GST_OBJECT_NAME (msg->src), err->message);
        g_printerr ("Debugging information: %s\n",
            debug_info ? debug_info : "none");
        g_clear_error (&err);
        g_free (debug_info);
        break;
      case GST_MESSAGE_EOS:
        g_print ("End-Of-Stream reached.\n");
        break;
      default:
        /* We should not reach here because we only asked for ERRORs and EOS */
        g_printerr ("Unexpected message received.\n");
        break;
    }
    gst_message_unref (msg);
  }

  /*释放资源*/
  gst_object_unref (bus);
  gst_element_set_state (pipeline, GST_STATE_NULL);
  gst_object_unref (pipeline);
  return 0;
}