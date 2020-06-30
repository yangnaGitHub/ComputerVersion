#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 16:14:59 2019

@author: yangna
"""
import cv2
import os

def divide_to_small_video(videoname, frames=512):
    count = 0
    namestr = 0
    cap = cv2.VideoCapture(os.path.join(rootpath, videoname))
    while cap.isOpened():
        ret,frame = cap.read()
        if ret:
            if 0 == count:
                out = cv2.VideoWriter(os.path.join(rootpath, '%06d.avi'%namestr), cv2.VideoWriter_fourcc(*'XVID'), 25, (1280,720), True)
            out.write(frame)
            count += 1
            if frames and (frames == count):    
                out.release()
                namestr += 1
                count = 0
        else:
            if not frames:
                out.release()
                print(count)
            break
    cap.release()
    
rootpath = '/home/yangna/yangna/project/grocery/video/13/'
divide_to_small_video('13.mp4', frames=160)

import glob

def generate_files(frames=512):
    features = frames//16
    startframe = [index*16 for index in range(features)]
    files = glob.glob(os.path.join(rootpath, '*.avi'))
    def getbasename(filename):
        return os.path.basename(filename)[:-4]
    files.sort(key=getbasename)
    with open(os.path.join(rootpath, 'input_list_video_all.txt'), 'w') as fd:
        with open(os.path.join(rootpath, 'output_list_video_prefix_all.txt'), 'w') as fd_w:
            with open(os.path.join(rootpath, 'cmd.txt'), 'w') as fd_c:
                for filename in files:
                    basename = os.path.basename(filename)
                    if int(basename[:-4]) < 76:
                        [fd.write('input/hidden/{} {} 0\n'.format(basename, no)) for no in startframe]
                    else:
                        [fd.write('input/nohidden/{} {} 1\n'.format(basename, no)) for no in startframe]
                    [fd_w.write('output/%s/%06d\n'%(basename[:-4], no)) for no in startframe]
                    fd_c.write('mkdir -p output/{}\n'.format(basename[:-4]))
                #fd_c.write('GLOG_logtosterr=1 ../../build/tools/extract_image_features.bin prototxt/c3d_sport1m_feature_extractor_video.prototxt conv3d_deepnetA_sport1m_iter_1900000 0 50 1 prototxt/output_list_video_prefix.txt fc7-1 fc6-1 prob')
generate_files(frames=160)