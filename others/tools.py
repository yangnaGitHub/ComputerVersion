#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 14:05:45 2019

@author: yangna
"""

import cv2
import os
def savePic(cap, s_path='/home/yangna/savePic', index=0, s_format='.jpg', skip=50, maxIndex=200):
    if not os.path.exists(s_path):
        os.makedirs(s_path)
    skipnumber = 0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret:
            if maxIndex <= index:
                break
            if 0 == (skipnumber % skip):
                cv2.imwrite(os.path.join(s_path, '%06d'%index+s_format), frame)
                index += 1
            skipnumber += 1
        else:
            break
        if ord('q') == cv2.waitKey(1)&0xFF:
            break
    cap.release()
    cv2.destroyAllWindows()
    return index
#examples
import glob
#videolist = glob.glob('/home/yangna/视频/*.mp4')
#index = 0
#for videopath in videolist:
#    cap = cv2.VideoCapture(videopath)
#    index = savePic(cap, index=index, maxIndex=2000)

def cropVideo(cap, s_path='/home/yangna/cropVideo', s_format='.avi', prefix=''):
    if not os.path.exists(s_path):
        os.makedirs(s_path)
    index = 0
    record = False
    writer = None
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret:
            cv2.imshow('frame', frame)
            if record and writer:
                writer.write(frame)
        else:
            break
        keyvalue = cv2.waitKey(1)&0xFF
        if ord('b') == keyvalue:
            writer = cv2.VideoWriter(os.path.join(s_path, '%06d_%s'%(index, prefix)+'.avi'), cv2.VideoWriter_fourcc(*'XVID'), 25, (frame.shape[1],frame.shape[0]), True)
            record = True
        elif ord('e') == keyvalue:
            writer.release()
            index += 1
            record = False
        elif ord('s') == keyvalue:
            cv2.imwrite(os.path.join(s_path, '%06d_%s'%(index, prefix)+s_format), frame)
            index += 1
        elif ord('q') == keyvalue:
            break
    cap.release()
    cv2.destroyAllWindows()
#examples
#path='rtsp://admin:shenlan2018@171.211.125.67:1554/h264/ch1/main/av_stream'
#cap = cv2.VideoCapture(path)
#cropVideo(cap, s_format='.jpg')
#source activate 35
#python tools.py 'rtsp://admin:shenlan2018@171.211.125.44:1554/h264/ch1/main/av_stream' '44' '.jpg'
import sys
if __name__ == '__main__':
    cap = cv2.VideoCapture(sys.argv[1])
    cropVideo(cap, s_format=sys.argv[3], prefix=sys.argv[2])

import shutil
def mixData(src_1, src_2, s_formats=['.jpg', '.png'], s_path='/home/yangna/mixData'):
    if not os.path.exists(s_path):
        os.makedirs(s_path)
    filenames = []
    for s_format in s_formats:
        filenames += glob.glob(os.path.join(src_1, '*'+s_format)) + glob.glob(os.path.join(src_2, '*'+s_format))
    index = 0
    for filename in filenames:
        shutil.copyfile(filename, os.path.join(s_path, '%06d%s'%(index, filename[-4:])))
        index += 1
#examples
#mixData('/home/yangna/savePic', '/home/yangna/cropVideo')

def convertToJpg(s_path, s_formats=['.png']):
    filenames = []
    for s_format in s_formats:
        filenames += glob.glob(os.path.join(s_path, '*'+s_format))
    for filename in filenames:
        image = cv2.imread(filename)
        cv2.imwrite(filename[:-3]+'jpg', image)
#examples
#convertToJpg('/home/yangna/mixData')

def convertToPng(s_path, s_formats=['.png', '.jpg']):
    filenames = []
    for s_format in s_formats:
        filenames += glob.glob(os.path.join(s_path, '*'+s_format))
    print(filenames)
    for filename in filenames:
        image = cv2.imread(filename)
#        cv2.imshow('test', image)
#        cv2.waitKey(0)
        print(filename[:-3]+'png')
        cv2.imwrite(filename[:-3]+'bmp', image)
convertToPng('/home/yangna/btv')

import cv2
import numpy as np
def convertColor(basepath = '/home/yangna/yangna/code/useful_methods/DeepNudeCLI/mask'):
    files = glob.glob(os.path.join(basepath, '*'))
    for filename in files:
        frame = cv2.imread(filename)
        new_frame = frame.astype(np.int8)
        new_frame = new_frame - 255
        new_frame = np.abs(new_frame) % 256
        new_frame[new_frame < 128] = 0
        new_frame[new_frame > 128] = 255
        cv2.imwrite(filename[:-4]+'_r'+filename[-4:], new_frame)