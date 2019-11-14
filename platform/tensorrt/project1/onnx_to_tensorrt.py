#!/usr/bin/env python2

from __future__ import print_function
import time
import numpy as np
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit
import sys, os

onnx_file_path = './yolov3.onnx'
engine_file_path = "./yolov3.trt"  ## "./yolov3_fp16.trt"  "./yolov3_int8.trt"
mode_fp16 = False ##default is fp32, 1080ti seems not support fp16


TRT_LOGGER = trt.Logger()
def get_engine(onnx_file_path, engine_file_path=""):
    """builds a new TensorRT engine and saves it."""
    def build_engine():
        """Takes an ONNX file and creates a TensorRT engine to run inference with"""
        with trt.Builder(TRT_LOGGER) as builder, builder.create_network() as network, trt.OnnxParser(network, TRT_LOGGER) as parser:
            builder.max_workspace_size = 1 << 30 # 1GB
            builder.max_batch_size = 1
            builder.fp16_mode = mode_fp16
            # builder.int8_mode = mode_int8
            # Parse model file
            if not os.path.exists(onnx_file_path):
                print('ONNX file {} not found, please run yolov3_to_onnx.py first to generate it.'.format(onnx_file_path))
                exit(0)
            print('Loading ONNX file from path {}...'.format(onnx_file_path))
            with open(onnx_file_path, 'rb') as model:
                print('Beginning ONNX file parsing')
                parser.parse(model.read())
            print('Completed parsing of ONNX file')
            print('Building an engine from file {}; this may take a while...'.format(onnx_file_path))
            engine = builder.build_cuda_engine(network)
            print("Completed creating Engine")
            with open(engine_file_path, "wb") as f:
                f.write(engine.serialize())
            return engine

    if os.path.exists(engine_file_path):
        # If a serialized engine exists, use it instead of building an engine.
        print("engine file already exits at {}".format(engine_file_path))
        
    else:
        return build_engine()

def main():
    """Create a TensorRT engine for ONNX-based YOLOv3-608 and run inference."""
    get_engine(onnx_file_path, engine_file_path)
    

if __name__ == '__main__':
    main()
