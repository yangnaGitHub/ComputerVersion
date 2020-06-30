#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 17:29:59 2019

@author: yangna
"""
import os
rootpath = '/home/yangna/yangna/code/useful_methods/C3D/C3D-v1.0/examples/c3d_feature_extraction'
with open(os.path.join(rootpath, 'prototxt', 'input_list_video_all.txt'), 'r') as fd:
    inputs = fd.readlines()
with open(os.path.join(rootpath, 'prototxt', 'output_list_video_prefix_all.txt'), 'r') as fd:
    outputs = fd.readlines()
keys = []
vals = []
excelstr = '/home/yangna/yangna/code/useful_methods/C3D/C3D-v1.0/build/tools/extract_image_features.bin'
model = os.path.join(rootpath, 'prototxt', 'c3d_sport1m_feature_extractor_video.prototxt')
weight = os.path.join(rootpath, 'conv3d_deepnetA_sport1m_iter_1900000')
output_prefix = os.path.join(rootpath, 'prototxt', 'output_list_video_prefix.txt')
for index,(key,val) in enumerate(zip(inputs,outputs)):
    keys.append(key)
    vals.append(val)
    if 0 == ((index+1) % 50):
        print(index)
        with open(os.path.join(rootpath, 'prototxt', 'input_list_video.txt'), 'w') as fd:        
            [fd.write(s_key) for s_key in keys]
        with open(output_prefix, 'w') as fd:        
            [fd.write(s_val) for s_val in vals]
        os.system('GLOG_logtosterr=1 '+excelstr+' '+model+' '+weight+' 0 50 1 '+output_prefix+' fc7-1 fc6-1 prob')
        #keys.clear()
        #vals.clear()
        del keys[:]
        del vals[:]
if 0 != len(keys):
    with open(os.path.join(rootpath, 'prototxt', 'input_list_video.txt'), 'w') as fd:        
        [fd.write(s_key) for s_key in keys]
    with open(output_prefix, 'w') as fd:        
        [fd.write(s_val) for s_val in vals]
    os.system('GLOG_logtosterr=1 '+excelstr+' '+model+' '+weight+' 0 50 1 '+output_prefix+' fc7-1 fc6-1 prob')
    del keys[:]
    del vals[:]