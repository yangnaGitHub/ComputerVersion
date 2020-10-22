#include <gst/gst.h>

//gcc basic-tutorial-4.c -o basic-tutorial-4 `pkg-config --cflags --libs gstreamer-1.0`

/* Structure to contain all our information, so we can pass it to callbacks */
typedef struct _CustomData {
  GstElement *pipeline;
  GstElement *source;
  GstElement *convert;
  GstElement *sink;
} CustomData;

/* Handler for the pad-added signal */
static void pad_added_handler (GstElement *src, GstPad *pad, CustomData *data);

int main(int argc, char *argv[]) {
  CustomData data;
  GstBus *bus;
  GstMessage *msg;
  GstStateChangeReturn ret;
  gboolean terminate = FALSE;

  /* Initialize GStreamer */
  gst_init (&argc, &argv);

  /*创建Element
  uridecodebin会内部实例化所需的Elements(source,demuxer,decoder)将URI所指向的媒体文件中的各种媒体数据分别提取出来,因为其包含了demuxer,所以Source Pad在初始化阶段无法访问,只有在收到相应事件后去动态连接Pad
  audioconvert用于在不同的音频数据格式之间进行转换
  autoaudiosink会自动查找声卡设备,将音频数据传输到声卡上进行输出
  */
  data.source = gst_element_factory_make ("uridecodebin", "source");
  data.convert = gst_element_factory_make ("audioconvert", "convert");
  data.sink = gst_element_factory_make ("autoaudiosink", "sink");

  /* Create the empty pipeline */
  data.pipeline = gst_pipeline_new ("test-pipeline");

  if (!data.pipeline || !data.source || !data.convert || !data.sink) {
    g_printerr ("Not all elements could be created.\n");
    return -1;
  }

  /*将converter和sink连接起来,没有连接source与convert,因为uridecode bin在Pipeline初始阶段还没有Source Pad*/
  gst_bin_add_many (GST_BIN (data.pipeline), data.source, data.convert , data.sink, NULL);
  if (!gst_element_link (data.convert, data.sink)) {
    g_printerr ("Elements could not be linked.\n");
    gst_object_unref (data.pipeline);
    return -1;
  }

  /*设置播放文件的uri,uridecodebin会自动解析该地址,并读取媒体数据*/
  g_object_set (data.source, "uri", "file:///home/yangna/yangna/code/mixCode/GStreamer/1234.mp4", NULL);

  /*监听事件GSignals
  在GLib中的信号通过信号名来进行识别,每个GObject对象都有其自己的信号
  通过g_signal_connect将pad_added_handler回调连接到uridecodebin的“pad-added”信号上,附带回调函数的私有参数
  GstElement可能会发出多个信号,可以使用gst-inspect工具查看具体到信号及参数Element Signals
  Source Element收集到足够到信息,能产生数据时,它会创建Source Pad并且触发“pad-added”信号
  */
  g_signal_connect (data.source, "pad-added", G_CALLBACK (pad_added_handler), &data);

  /* Start playing */
  ret = gst_element_set_state (data.pipeline, GST_STATE_PLAYING);
  if (ret == GST_STATE_CHANGE_FAILURE) {
    g_printerr ("Unable to set the pipeline to the playing state.\n");
    gst_object_unref (data.pipeline);
    return -1;
  }

  /* Listen to the bus */
  bus = gst_element_get_bus (data.pipeline);
  do {
    msg = gst_bus_timed_pop_filtered (bus, GST_CLOCK_TIME_NONE,
        GST_MESSAGE_STATE_CHANGED | GST_MESSAGE_ERROR | GST_MESSAGE_EOS);

    /* Parse message */
    if (msg != NULL) {
      GError *err;
      gchar *debug_info;

      switch (GST_MESSAGE_TYPE (msg)) {
        case GST_MESSAGE_ERROR:
          gst_message_parse_error (msg, &err, &debug_info);
          g_printerr ("Error received from element %s: %s\n", GST_OBJECT_NAME (msg->src), err->message);
          g_printerr ("Debugging information: %s\n", debug_info ? debug_info : "none");
          g_clear_error (&err);
          g_free (debug_info);
          terminate = TRUE;
          break;
        case GST_MESSAGE_EOS:
          g_print ("End-Of-Stream reached.\n");
          terminate = TRUE;
          break;
        case GST_MESSAGE_STATE_CHANGED:
          /* We are only interested in state-changed messages from the pipeline */
          if (GST_MESSAGE_SRC (msg) == GST_OBJECT (data.pipeline)) {
            GstState old_state, new_state, pending_state;
            gst_message_parse_state_changed (msg, &old_state, &new_state, &pending_state);
            g_print ("Pipeline state changed from %s to %s:\n",
                gst_element_state_get_name (old_state), gst_element_state_get_name (new_state));
          }
          break;
        default:
          /* We should not reach here */
          g_printerr ("Unexpected message received.\n");
          break;
      }
      gst_message_unref (msg);
    }
  } while (!terminate);

  /* Free resources */
  gst_object_unref (bus);
  gst_element_set_state (data.pipeline, GST_STATE_NULL);
  gst_object_unref (data.pipeline);
  return 0;
}

/*src指向触发这个事件的GstElement对象实例(uridecodebin),new_pad指向被创建的src中被创建的GstPad对象实例,data私有数据
source(src)->convert(sink)->convert(src)->sink(sink)
        Not OK           OK             OK
*/
static void pad_added_handler (GstElement *src, GstPad *new_pad, CustomData *data) {
  //gst_element_get_static_pad()获取其Sink Pad
  GstPad *sink_pad = gst_element_get_static_pad (data->convert, "sink");//convert(sink)
  GstPadLinkReturn ret;
  GstCaps *new_pad_caps = NULL;
  GstStructure *new_pad_struct = NULL;
  const gchar *new_pad_type = NULL;

  g_print ("Received new pad '%s' from '%s':\n", GST_PAD_NAME (new_pad), GST_ELEMENT_NAME (src));

  /*避免重复连接Pad*/
  if (gst_pad_is_linked (sink_pad)) {
    g_print ("We are already linked. Ignoring.\n");
    goto exit;
  }

  /*source(src)
  new_pad_type is audio/x-raw or not
  */
  new_pad_caps = gst_pad_get_current_caps (new_pad);//gst_pad_get_current_caps()可以获取当前Pad的能力,Pad所支持的所有Caps可以通过gst_pad_query_caps()得到
  //由于一个Pad可能包含多个Caps,因此GstCaps可以包含一个或多个GstStructure,每个都代表所支持的不同数据的能力
  //gst_pad_get_current_caps()获取到的当前Caps只会包含一个GstStructure用于表示唯一的数据类型
  //如果无法获取到当前所使用到Caps,直接返回NULL
  new_pad_struct = gst_caps_get_structure (new_pad_caps, 0);
  new_pad_type = gst_structure_get_name (new_pad_struct);//通过gst_structure_get_name() 获取该Cap支持的数据类型
  if (!g_str_has_prefix (new_pad_type, "audio/x-raw")) {
    g_print ("It has type '%s' which is not raw audio. Ignoring.\n", new_pad_type);
    goto exit;
  }

  /* Attempt the link */
  ret = gst_pad_link (new_pad, sink_pad);//使用gst_pad_link()将其与Sink Pad进行连接
  if (GST_PAD_LINK_FAILED (ret)) {
    g_print ("Type is '%s' but link failed.\n", new_pad_type);
  } else {
    g_print ("Link succeeded (type '%s').\n", new_pad_type);
  }

exit:
  /* Unreference the new pad's caps, if we got them */
  if (new_pad_caps != NULL)
    gst_caps_unref (new_pad_caps);

  /* Unreference the sink pad */
  gst_object_unref (sink_pad);
}