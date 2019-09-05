# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 11:32:50 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2
import numpy as np

#回调函数通常都会含有一个默认参数(滑动条的位置)
def nothing(x):
    pass

img = np.zeros((300,512,3), np.uint8)

cv2.namedWindow('image')
#滑动条的名字,滑动条被放置窗口的名字,滑动条的默认位置,滑动条的最大值,回调函数
cv2.createTrackbar('R', 'image', 0, 255, nothing)
cv2.createTrackbar('G', 'image', 0, 255, nothing)
cv2.createTrackbar('B', 'image', 0, 255, nothing)

#滑动条的另外一个重要应用就是用作转换按钮,不带有按钮函数,使用滑动条来代替
switch='0:OFF\n1:ON'
cv2.createTrackbar(switch, 'image' , 0, 1, nothing)

while(1):
    cv2.imshow('image', img)
    key = cv2.waitKey(1)&0xFF
    if 27 == key:
        break
    r = cv2.getTrackbarPos('R', 'image')#返回值
    g = cv2.getTrackbarPos('G', 'image')
    b = cv2.getTrackbarPos('B', 'image')
    s = cv2.getTrackbarPos(switch, 'image')
    if 0 == s:
        img[:] = 0
    else:
        img[:] = [b, g, r]
        
cv2.destroyAllWindows()