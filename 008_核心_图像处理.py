# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 19:00:08 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2
import numpy as np
#############转化颜色空间
#cv2.cvtColor(input_image, flag)
# BGR->GRAY:cv2.COLOR_BGR2GRAY
# BGR->HSV:cv2.COLOR_BGR2HSV
#H:色彩/色度[0,179],S:饱和度[0,255],V亮度[0,255]
#opencv中HSV值和其他软件中的HSV值比对的时候要归一化
flags = [index for index in dir(cv2) if index.startswith('COLOR_')]
print(flags)

#############物体跟踪
#BGR->HSV之后,可以利用这一点来提取带有某个特定颜色的物体
#在HSV颜色空间中要比BGR空间中更容易表示一个特定的颜色
#比如提取一个蓝色的物体
# 视频中获取每一帧图像
# 图像转换到HSV空间
# 设置HSV阈值到蓝色范围
# 获取蓝色物体,进行其他操作
cap = cv2.VideoCapture(0)

while True:
    #获取每一帧视频
    ret,frame = cap.read()
    if ret:
        #转换称HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    else:
        break
    #设置蓝色的阈值
    '''怎样找到要跟踪对象的HSV值
    cvArray,cvMat,IplImage
    green = np.uint8([[[0,255,0]]])
    hsv_green = cv2.cvtColor(green, cv2.COLOR_BGR2HSV)
    print(hsv_green)
    '''
    lower_b = np.array([110, 50, 50])
    upper_b = np.array([130, 255, 255])
    
    #构建掩模
    mask = cv2.inRange(hsv, lower_b, upper_b)#除了蓝色区域是白色255的,其他部分就是黑色的
    #位运算
    res = cv2.bitwise_and(frame, frame, mask=mask)
    #显示图像
    cv2.imshow('frame', frame)
    cv2.imshow('mask', mask)
    cv2.imshow('res', res)
    key = cv2.waitKey(5)&0xFF
    if 27 == key:
        break
cap.release()#使用过摄像头之后一定要记得释放,不然在次使用会报错
cv2.destroyAllWindows()