# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 16:36:27 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2
import numpy as np

def nothing(x):
    pass

drawing = False
mode = True
ix,iy = -1,-1

def draw_circle(event, x, y, flags, param):
    r = cv2.getTrackbarPos('R', 'image')
    g = cv2.getTrackbarPos('G', 'image')
    b = cv2.getTrackbarPos('B', 'image')
    color = (b,g,r)
    global ix,iy,drawing,mode
    if cv2.EVENT_LBUTTONDOWN == event:
        drawing = True
        ix,iy = x,y
    elif cv2.EVENT_FLAG_LBUTTON == flags and cv2.EVENT_MOUSEMOVE == event and drawing:
        if mode:
            cv2.rectangle(img, (ix,iy), (x,y), color, -1)
        else:
            r = int(np.sqrt((x-ix)**2+(y-iy)**2))
            cv2.circle(img, (x,y), r, color, -1)
    elif cv2.EVENT_LBUTTONUP == event:
        drawing = False

img = np.zeros((512,512,3), np.uint8)

cv2.namedWindow('image')
cv2.createTrackbar('R', 'image', 0, 255, nothing)
cv2.createTrackbar('G', 'image', 0, 255, nothing)
cv2.createTrackbar('B', 'image', 0, 255, nothing)
cv2.setMouseCallback('image', draw_circle)
while True:
    cv2.imshow('image', img)
    key = cv2.waitKey(1)&0xFF
    if ord('m') == key:
        mode = not mode
    elif 27 == key:
        break
cv2.destroyAllWindows()