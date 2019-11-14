
from __future__ import print_function
import time
import numpy as np
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit

from infer_processing import PreprocessYOLO, PostprocessYOLO, draw_bboxes, allocate_buffers, do_inference
import sys, os
# import common
import argparse
import cv2



def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", default='./kite.jpg', type=str, help="image path")
    return parser.parse_args()
args = arg_parse()


## main configs
engine_file_path = "yolov3.trt"
label_file_path= 'coco_labels.txt'
category_num = 80
input_image_path=args.image #'person.jpg'
output_image_path = 'prediction.png'
input_resolution_yolov3_HW = (608,608) # (608, 608)  # (416,416) should suit the following "output_shapes"
output_shapes = [(1, 255, 19, 19), (1, 255, 38, 38), (1, 255, 76, 76)]  # [(1, 255, 13, 13), (1, 255, 26, 26), (1, 255, 52, 52)] for (416,416)
masks = [(6, 7, 8), (3, 4, 5), (0, 1, 2)]
anchors = [(10, 13), (16, 30), (33, 23), (30, 61), (62, 45), (59, 119), (116, 90), (156, 198), (373, 326)]
obj_thresh = 0.6
nms_thresh = 0.5




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


def main():
    """Create a TensorRT engine for ONNX-based YOLOv3 and run inference."""

    # Create a pre-processor object by specifying the required input resolution for YOLOv3
    preprocessor = PreprocessYOLO(input_resolution_yolov3_HW)
    t1 = time.time()
    # Load an image from the specified input path, and return it together with  a pre-processed version
    image_raw, image = preprocessor.process(input_image_path)
    # Store the shape of the original input image in WH format, we will need it for later
    shape_orig_WH = image_raw.size
    print("preprocess time: {}\n".format(time.time()-t1))
    # Do inference with TensorRT
    trt_outputs = []
    with get_engine(engine_file_path) as engine, engine.create_execution_context() as context:
        # inputs, outputs, bindings, stream = common.allocate_buffers(engine)
        inputs, outputs, bindings, stream = allocate_buffers(engine)

        # Do inference
        print('Running inference on image {}...'.format(input_image_path))
        # Set host input to the image. The common.do_inference function will copy the input to the GPU before executing.
        inputs[0].host = image
        
        # trt_outputs = common.do_inference(context, bindings=bindings, inputs=inputs, outputs=outputs, stream=stream)
        trt_outputs = do_inference(context, bindings=bindings, inputs=inputs, outputs=outputs, stream=stream)

        # print(trt_outputs)

    # Before doing post-processing, we need to reshape the outputs as the common.do_inference will give us flat arrays.
    trt_outputs = [output.reshape(shape) for output, shape in zip(trt_outputs, output_shapes)]
    
    postprocessor_args = {"yolo_masks": masks,                    # A list of 3 three-dimensional tuples for the YOLO masks
                          "yolo_anchors": anchors,                # A list of 9 two-dimensional tuples for the YOLO anchors
                          "obj_threshold": obj_thresh,            # Threshold for object coverage, float value between 0 and 1
                          "nms_threshold": nms_thresh,            # Threshold for non-max suppression algorithm, float value between 0 and 1
                          "yolo_input_resolution": input_resolution_yolov3_HW,
                          "category_num": category_num}

    postprocessor = PostprocessYOLO(**postprocessor_args)
    t4 = time.time()
    # Run the post-processing algorithms on the TensorRT outputs and get the bounding box details of detected objects
    boxes, classes, scores = postprocessor.process(trt_outputs, (shape_orig_WH))
    t5 = time.time()
    print("postprocess time: {}".format(t5-t4))
    # load label catgories
    all_categories = load_label_categories(label_file_path)
    # Draw the bounding boxes onto the original input image and save it as a PNG file
    obj_detected_img = draw_bboxes(image_raw, boxes, scores, classes, all_categories)
    obj_detected_img.save(output_image_path, 'PNG')
    print('Saved image with bounding boxes of detected objects to {}.'.format(output_image_path))
    img = cv2.cvtColor(np.asarray(obj_detected_img),cv2.COLOR_RGB2BGR)
    cv2.imshow("frame", img)
    cv2.waitKey(5000) 

if __name__ == '__main__':
    main()
