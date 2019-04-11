# -*- coding: utf-8 -*-
"""
Created on Sun Apr  7 16:06:13 2019

@author: yangna

e-mail:ityangna0402@163.com
"""

#书香苏州
import cv2
#import numpy as np

#cv2.getTickCount:从参考点到这个函数被执行的时钟数
#cv2.getTickFrequency:返回时钟频率,或者说每秒钟的时钟数

img1 = cv2.imread('0002.jpg')
e1 = cv2.getTickCount()
for index in range(5, 49, 2):
    img1 = cv2.medianBlur(img1, index)#中值滤波
e2 = cv2.getTickCount()
time = (e2 - e1)/ cv2.getTickFrequency()#用了多久的时间
print(time)

#编译时优化是被默认开启的
#cv2.useOptimized()查看优化是否被开启
#cv2.setUseOptimized()开启优化
#这是IPython的魔法命令%time
#%timeit res = cv2.medianBlur(img, 49)

#尽量避免使用循环
#算法中尽量使用向量操作,Numpy和OpenCV都对向量操作进行了优化
#利用高速缓存一致性
#没有必要的话就不要复制数组,使用视图来代替复制
#Cython加速程序