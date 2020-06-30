#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 11:07:48 2019

@author: yangna
"""

import cv2
import random
import os

rootpath='/home/yangna/yangna/project/grocery/video/30'
cap = cv2.VideoCapture(os.path.join(rootpath, '20190802_20190802172433_20190802172435_171212.mp4'))
while(cap.isOpened()):
    ret, frame = cap.read()
    if ret:
        cv2.imshow('frame', frame)
        cv2.imwrite(os.path.join(rootpath, 'yangna.jpg'), frame)
    if cv2.waitKey(1)&0xFF == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()

def get_skipwindows_crop(frame, weight=100, height=200, skip=50):
    wstart = 0
    hstart = 0
    wend = 0
    hend = hstart + height + random.randint(-100, 200)
    index = 0
    while True:
        wend = wstart + weight + random.randint(-30, 100)
        if hend > frame.shape[0]:
            hend = frame.shape[0]
        if wend > frame.shape[1]:
            wend = frame.shape[1]
        cv2.imshow('frame', frame[hstart:hend, wstart:wend])
        cv2.imwrite(os.path.join(rootpath, '%06d.jpg'%index), frame[hstart:hend, wstart:wend])
        index += 1
        if (hend == frame.shape[0]) and (wend == frame.shape[1]):
            break
        if wend == frame.shape[1]:
            hstart = hstart + skip + random.randint(-40, 40)
            hend = hstart + height + random.randint(-100, 200)   
            wstart = 0
        else:
            wstart = wstart + skip + random.randint(-40, 40)
        if cv2.waitKey(1000)&0xFF == ord("q"):
            break
    cv2.destroyAllWindows()

frame = cv2.imread(os.path.join(rootpath, 'yangna.jpg'))
get_skipwindows_crop(frame)
cv2.destroyAllWindows()