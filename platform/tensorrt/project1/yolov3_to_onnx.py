#!/usr/bin/env python2

from __future__ import print_function
from collections import OrderedDict
import hashlib
import os.path

import wget

import onnx
from onnx import helper
from onnx import TensorProto
import numpy as np

# import sys

from utils import * 

yolo_cfg_path = "./yolov3.cfg"
yolo_weights_path = "./yolov3.weights"
output_file_path = "yolov3.onnx"

# three outputs that we need to know, shape of (in CHW format):
## YOLOv3-608
output_tensor_dims = OrderedDict()
output_tensor_dims['082_convolutional'] = [255, 19, 19]
output_tensor_dims['094_convolutional'] = [255, 38, 38]
output_tensor_dims['106_convolutional'] = [255, 76, 76]


def main():
    """Run the DarkNet-to-ONNX conversion for YOLOv3-608."""
    # Have to use python 2 due to hashlib compatibility
   
    # These are the only layers DarkNetParser will extract parameters from. The three layers of
    # type 'yolo' are not parsed in detail because they are included in the post-processing later:
    supported_layers = ['net', 'convolutional', 'shortcut',
                        'route', 'upsample']

    # Create a DarkNetParser object, and the use it to generate an OrderedDict with all
    # layer's configs from the cfg file:
    parser = DarkNetParser(supported_layers)
    # layer_configs = parser.parse_cfg_file(cfg_file_path)
    layer_configs = parser.parse_cfg_file(yolo_cfg_path)
    # We do not need the parser anymore after we got layer_configs:
    del parser

    # # In above layer_config, there are three outputs that we need to know the output
    # # shape of (in CHW format):
    # output_tensor_dims = OrderedDict()
    # output_tensor_dims['082_convolutional'] = [255, 19, 19]
    # output_tensor_dims['094_convolutional'] = [255, 38, 38]
    # output_tensor_dims['106_convolutional'] = [255, 76, 76]

    # Create a GraphBuilderONNX object with the known output tensor dimensions:
    builder = GraphBuilderONNX(output_tensor_dims)


    # Now generate an ONNX graph with weights from the previously parsed layer configurations
    # and the weights file:
    yolov3_model_def = builder.build_onnx_graph(
        layer_configs=layer_configs,
        weights_file_path=yolo_weights_path,
        verbose=True)
    # Once we have the model definition, we do not need the builder anymore:
    del builder

    # Perform a sanity check on the ONNX model definition:
    # onnx.checker.check_model(yolov3_model_def)

    # Serialize the generated ONNX graph to this file:
    
    with open(output_file_path, 'wb') as f:
        f.write(yolov3_model_def.SerializeToString())

if __name__=="__main__":
    main()
