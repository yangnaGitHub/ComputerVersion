#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 16:07:52 2019

@author: yangna
"""

import cv2
import numpy as np
srcPath = '/home/yangna/2.jpg'
img = cv2.imread(srcPath)

def on_EVENT_LBUTTONDOWN(event, x, y, flags, param):
    global flag
    if event == cv2.EVENT_LBUTTONDOWN:
        flag = True
    if event == cv2.EVENT_MOUSEMOVE and flag:
        cv2.circle(img, (x, y), 10, (255, 0, 0), thickness=-1)
        cv2.imshow('image', img)
    if event == cv2.EVENT_LBUTTONUP:
        flag = False
    if event == cv2.EVENT_LBUTTONDBLCLK:
        findRect()

def findRect():
    mask = cv2.inRange(img, lowerb=np.array([255,0,0]), upperb=np.array([255,0,0]))
    dst = cv2.bitwise_and(img, img, mask=mask)
    diff_gray = cv2.cvtColor(dst, cv2.COLOR_RGB2GRAY)
    cv2.imshow('diff_gray', diff_gray)
    if cv2.__version__[-5] == '4':
        contours, _ = cv2.findContours(diff_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    else:
        _, contours, _ = cv2.findContours(diff_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnt_area = [cv2.contourArea(cnt) for cnt in contours]
    for index,contour in enumerate(contours):
        if cnt_area[index] > 100:# and cnt_area[index] < 2000:
            polygon = contour.reshape(-1, 2)
            prbox = cv2.boxPoints(cv2.minAreaRect(polygon))
            print(prbox)
            x,y,w,h = cv2.boundingRect(contour)
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            rbox_in_img = np.int0(prbox.flatten()).reshape((-1, 1, 2))
            cv2.polylines(img, [rbox_in_img], True, (255, 255, 0), 3)
    cv2.imshow('image', img)
    
cv2.namedWindow('image')
cv2.setMouseCallback('image', on_EVENT_LBUTTONDOWN)
cv2.imshow('image', img)

while(True):
    try:
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break
            break
    except Exception:
        cv2.destroyAllWindows()
        break

cv2.waitKey(0)
cv2.destroyAllWindows()


srcPath = '/home/yangna/yangna/code/object_detection/darknet_origin/temp.jpg'
img = cv2.imread(srcPath)

#cap = cv2.VideoCapture('/home/yangna/yangna/project/grocery/video/6/20190802_20190802182743_20190802183000_181521.mp4')
cap = cv2.VideoCapture('/home/yangna/yangna/code/object_detection/darknet/hidden_1.mp4')
ret,img = cap.read()
while(True):
    r = cv2.selectROI(img)
    print(r)    
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

cv2.waitKey(0)
cv2.destroyAllWindows()