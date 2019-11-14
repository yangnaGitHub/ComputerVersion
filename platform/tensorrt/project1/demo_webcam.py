from __future__ import print_function
import time
import numpy as np
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit
# from PIL import Image
from infer_processing import PreprocessYOLO, PostprocessYOLO, allocate_buffers, do_inference , draw_bboxes_video, reshape_image
import sys, os

import cv2
import argparse


def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--webcam", default="rtsp://admin:admin12345@192.168.41.7:554/h264", help="video or webcam")
    parser.add_argument("--engine_file_path", default='./yolov3.trt', type=str, help="engine model path")
    parser.add_argument("--label_file_path", default = "coco_labels.txt")
    parser.add_argument("--category_num", default = 80, type=int)
    parser.add_argument("--input_size",default = 608, type = int)
    return parser.parse_args()
args = arg_parse()

## configs
engine_file_path = args.engine_file_path #"yolov3.trt"
label_file_path= args.label_file_path
category_num = args.category_num  # 80
input_resolution = (args.input_size, args.input_size) # (608, 608)  # (416,416) should suit the following "output_shapes"
output_shapes = [(1, 255, 19, 19), (1, 255, 38, 38), (1, 255, 76, 76)] # [(1, 255, 13, 13), (1, 255, 26, 26), (1, 255, 52, 52)] for (416,416)
masks = [(6, 7, 8), (3, 4, 5), (0, 1, 2)]
anchors = [(10, 13), (16, 30), (33, 23), (30, 61), (62, 45), (59, 119), (116, 90), (156, 198), (373, 326)]
obj_thresh = 0.6
nms_thresh = 0.5
webcam = args.webcam



TRT_LOGGER = trt.Logger()
def get_engine(engine_file_path=engine_file_path):
    """load a serialized engine if available."""
    
    if not os.path.exists(engine_file_path):
        print("error:engine file {} is not exits".format(engine_file_path))
        
    else:
        # If a serialized engine exists, use it instead of building an engine.
        print("Reading engine from file {}".format(engine_file_path))
        with open(engine_file_path, "rb") as f, trt.Runtime(TRT_LOGGER) as runtime:
            return runtime.deserialize_cuda_engine(f.read())

def load_label_categories(label_file_path):
    """load labels."""
    categories = [line.rstrip('\n') for line in open(label_file_path)]
    return categories

def draw_message(image, message):
    cv2.putText(image, message, (32, 32), \
        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)



def main():
    preprocessor = PreprocessYOLO(input_resolution)
    all_categories = load_label_categories(label_file_path)

    postprocessor_args = {"yolo_masks": masks,                    # A list of 3 three-dimensional tuples for the YOLO masks
                          "yolo_anchors": anchors,                # A list of 9 two-dimensional tuples for the YOLO anchors
                          "obj_threshold": obj_thresh,            # Threshold for object coverage, float value between 0 and 1
                          "nms_threshold": nms_thresh,            # Threshold for non-max suppression algorithm, float value between 0 and 1
                          "yolo_input_resolution": input_resolution,
                          "category_num": category_num}
    postprocessor = PostprocessYOLO(**postprocessor_args)

    cap = cv2.VideoCapture(webcam)
    act_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    act_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    frame_info = 'Frame: %d x %d'%(act_width, act_height)


    trt_outputs = []
    num_frames = 0
    fps = 0.0
    time_list = np.zeros(10)

    # start = time.time()
    with get_engine(engine_file_path) as engine, engine.create_execution_context() as context:
        inputs, outputs, bindings, stream = allocate_buffers(engine)
        
        while(cap.isOpened()):
            start_t = time.time()
            ret, frame = cap.read()
            if ret != True:
                continue

            t0 = time.time()
            src_img = reshape_image(frame, input_resolution)
            t1 = time.time()
            print("image prepreprocess time: {}".format(t1-t0))
            
            inputs[0].host = src_img
            trt_outputs = do_inference(context, bindings=bindings, inputs=inputs, outputs=outputs, stream=stream)
            
            # t4 = time.time()
            trt_outputs = [output.reshape(shape) for output, shape in zip(trt_outputs, output_shapes)]
            t4 = time.time()
            # Calculates the bounding boxes
            boxes, classes, scores = postprocessor.process(trt_outputs, (act_width, act_height))
            # print(boxes)
            t5 = time.time()
            print("postprocess time: {}".format(t5-t4))
            # Draw the bounding boxes
            if boxes is not None:
                draw_bboxes_video(frame, boxes, scores, classes, all_categories)
            
            
            if num_frames > 10:
                print("speed: {:5.2f} fps\n".format(fps))
                # fps_info = '{0}{1:.2f}'.format('FPS:', fps)
                # msg = '%s %s'%(frame_info, fps_info)
                # draw_message(frame, msg)
            
            
            ## calculate fps
            elapsed_t = time.time() - start_t
            time_list = np.append(time_list, elapsed_t)
            time_list = np.delete(time_list, 0)
            avg_time = np.average(time_list)
            fps = 1.0 / avg_time
            num_frames += 1

            t7 = time.time()
            print("total time for one frame: {}\n\n".format(t7-start_t))

            cv2.imshow("frame", frame) 
            # if cv2.waitKey(25) & 0xFF == ord('q'):
            key = cv2.waitKey(1)
            if key == 27: ## ESC
                break
    cap.release()
    # cv2.destroyAllWindows()


if __name__ == '__main__':
    main()


