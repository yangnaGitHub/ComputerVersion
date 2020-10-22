#include <gst/gst.h>
#include <stdio.h>

//gcc basic-tutorial-1.c -o basic-tutorial-1 `pkg-config --cflags --libs gstreamer-1.0`
//./basic-tutorial-1.c
/*
gst_init初始化
gst_parse_launch创建Pipeline(简单)
gst_element_set_state设置播放状态
gst_element_get_bus+gst_bus_timed_pop_filtered等待播放结束
释放资源
*/

int main (int argc, char *argv[]){
  printf("1234.mp4 start\n");
  GstElement *pipeline;
  GstBus *bus;
  GstMessage *msg;

  /*1.GStreamer初始化(初始化函数必须在其他gstreamer接口之前被调用)
  初始化GStreamer库
  注册内部element
  加载插件列表,扫描列表中及相应路径下的插件
  解析并执行命令行参数
  在不需要gst_init处理命令行参数时,可以NULL作为其参数,例如:gst_init(NULL, NULL);
  */
  gst_init (&argc, &argv);

  /*2.创建Pipeline
  在pipeline中,首先通过“source” element获取媒体数据,然后通过一个或多个element对编码数据进行解码,最后通过“sink” element输出声音和画面
  创建较复杂的pipeline时,需要通过gst_element_factory_make来创建element,然后将其加入到GStreamer Bin中,并连接起来
  当pipeline比较简单并且我们不需要对pipeline中的element进行过多的控制时,可以采用gst_parse_launch来简化pipeline的创建
    gst_parse_launch巧妙的将pipeline的文本描述转化为pipeline对象
    经常需要通过文本方式构建pipeline来查看GStreamer是否支持相应的功能(gst-launch-1.0命令行工具)
  
  此行代码解释:
    通过gst_parse_launch创建了只包含一个element的Pipeline
    playbin element内部会根据文件的类型自动去查找所需要的“source”,“decoder”,“sink”并将它们连接起来,同时提供了部分接口用于控制pipeline中相应的element
    playbin后跟了一个uri参数,指定了我们想要播放的媒体文件地址,playbin会根据uri所使用的协议(“https://”,“ftp://”,“file://”等)自动选择合适的source element获取数据
  */
  pipeline = gst_parse_launch ("playbin uri=file:///home/yangna/yangna/code/mixCode/GStreamer/1234.mp4", NULL);

  /*3.设置播放状态(state)
  每个GStreamer element都有相应都状态
  
  此行代码解释:
    gst_element_set_state通过pipeline将playbin的状态设置为PLAYING,使playbin开始播放视频文件
  */
  gst_element_set_state (pipeline, GST_STATE_PLAYING);

  /*4.等待播放结束
  GStreamer框架会通过bus,将所发生的事件通知到应用程序,这里首先取得pipeline的bus对象gst_element_get_bus
  gst_bus_timed_pop_filtered以同步的方式等待bus上的ERROR或EOS(End of Stream)消息,该函数收到消息后才会返回
  
  此行代码解释:
    会等待pipeline播放结束或者播放出错
  */
  bus = gst_element_get_bus (pipeline);
  msg = gst_bus_timed_pop_filtered (bus, GST_CLOCK_TIME_NONE, GST_MESSAGE_ERROR | GST_MESSAGE_EOS);

  /*5.释放资源
  将不再使用的msg,bus对象进行销毁
  并将pipeline状态设置为NULL(在NULL状态时GStreamer会释放为pipeline分配的所有资源）
  最后销毁pipeline对象
  由于GStreamer是继承自GObject,所以需要通过gst_object_unref来减少引用计数,当对象的引用计数为0时,函数内部会自动释放为其分配的内存
  */
  if (msg != NULL) gst_message_unref (msg);
  gst_object_unref (bus);
  gst_element_set_state (pipeline, GST_STATE_NULL);
  gst_object_unref (pipeline);
  return 0;
}