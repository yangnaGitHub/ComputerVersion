# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 13:51:27 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2
import numpy as np

#直方图可以对整幅图像的灰度分布有一个整体的了解
# 直方图的x轴是灰度值,y轴是图片中具有同一个灰度值的点的数目
# 直方图是根据灰度图像绘制,越靠左越暗,越靠右越亮
# 每一个小组就被成为BIN,比如256个值,一个值一个BIN要256个BIN,16个值一个BIN要16个BIN(histSize)
# DIMS收集数据的参数数目
# RANGE统计的灰度值范围
# cv2.calcHist统计一幅图像的直方图<=[原图像],[通道],mask(掩模图像,统计图像某一部分的直方图),[histSize](BIN的数目),像素值范围
#  [通道]:灰度图[0] + B:[0] + G:[1] + R:[2]
img = cv2.imread('0001.jpg', 0)
# 1.统计直方图
hist = cv2.calcHist([img], [0], None, [256], [0,256])#(256*1)
'''
#img.ravel()将图像转成一维数组
hist,bins = np.histogram(img.ravel(), 256, [0,256])#bins是257
#np.bincount()运行速度是np.histgram()的十倍
hist = np.bincount(img.ravel(), minlength=256)
'''
# 2.绘制直方图
#  简单方法:Matplotlib
from matplotlib import pyplot as plt
plt.plot(hist)
'''
plt.hist(img.ravel(), 256, [0,256])
'''
plt.show()

img2 = cv2.imread('0002.jpg')
color = ('b', 'g', 'r')
for index,col in enumerate(color):
    histr = cv2.calcHist([img2], [index], None, [256], [0,256])
    plt.plot(histr, color = col)
    plt.xlim([0,256])
plt.show()
#  复杂方法:OpenCV

# 3.使用掩模
#  统计图像某个局部区域的直方图只需要构建一副掩模图像,将要统计的部分设置成白色(255),其余部分为黑色(0)<=and
mask = np.zeros(img.shape[:2], np.uint8)
mask[100:300, 100:400] = 255
masked_img = cv2.bitwise_and(img, img, mask = mask)
hist_mask = cv2.calcHist([img], [0], mask, [256], [0,256])
cv2.imshow('img', img)
cv2.imshow('mask', mask)
cv2.imshow('masked_img', masked_img)
plt.plot(hist_mask)

cv2.waitKey(0)
cv2.destroyAllWindows()