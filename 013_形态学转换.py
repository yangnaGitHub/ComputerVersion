# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 15:34:14 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2
import numpy as np

#形态学操作:根据图形进行简单的操作,一般情况下是对二值化图像进行的操作
# 原始图像,kernel(决定如何操作)
# 1.腐蚀:会把前景物体的边界腐蚀掉(前景仍旧是白色)
#  卷积核沿着图像滑动,如果与卷积核对应的原图像的所有像素值都是1,那么中心元素就保持原来的像素值,否则就是0
#  靠近前景的所有像素都会被腐蚀掉变成0,前景物体也会变小,整幅图像的白色区域会减少
#  除去白噪声很有用,也可以用来断开两个连在一块的物体
img = cv2.imread('0001.jpg', 0)
kernel = np.ones((5,5), np.uint8)
erosion = cv2.erode(img, kernel, iterations = 1)
cv2.imshow('erosion', erosion)

# 2.膨胀:卷积核对应的原图像的像素值中只要有一个是1,中心元素的像素值就是1
#  操作会增加图像中的白色区域(前景),可以用来连接两个分开的物体
#  去噪音的时候一般先腐蚀后膨胀
dilation = cv2.dilate(img,kernel,iterations = 1)
cv2.imshow('dilation', dilation)

# 3.开运算:腐蚀->膨胀,用作去除噪声dilate(erosion, kernel)
#  cv2.morphologyEx()
opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
cv2.imshow('opening', opening)

# 4.闭运算:膨胀->腐蚀,经常被用来填充前景物体中的小洞,或者前景物体上的小黑点erode(dilation, kernel)
closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
cv2.imshow('closing', closing)

# 5.形态学梯度:一幅图膨胀与腐蚀的差别,就像前景物体的轮廓dilation-erosion
gradient = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel)
cv2.imshow('gradient', gradient)

# 6.礼帽:原始图像与进行开运算之后得到的图像的差(img-opening)
tophat = cv2.morphologyEx(img, cv2.MORPH_TOPHAT, kernel)
cv2.imshow('tophat', tophat)

# 7.黑帽:闭运算之后得到的图像与原始图像的差((closing-img))
blackhat = cv2.morphologyEx(img, cv2.MORPH_BLACKHAT, kernel)
cv2.imshow('blackhat', blackhat)

#构建一个椭圆形/圆形的核cv2.getStructuringElement()
cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
#array([[1, 1, 1, 1, 1],
#       [1, 1, 1, 1, 1],
#       [1, 1, 1, 1, 1],
#       [1, 1, 1, 1, 1],
#       [1, 1, 1, 1, 1]], dtype=uint8)
cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
#array([[0, 0, 1, 0, 0],
#       [1, 1, 1, 1, 1],
#       [1, 1, 1, 1, 1],
#       [1, 1, 1, 1, 1],
#       [0, 0, 1, 0, 0]], dtype=uint8)
cv2.getStructuringElement(cv2.MORPH_CROSS, (5,5))
#array([[0, 0, 1, 0, 0],
#       [0, 0, 1, 0, 0],
#       [1, 1, 1, 1, 1],
#       [0, 0, 1, 0, 0],
#       [0, 0, 1, 0, 0]], dtype=uint8)

cv2.waitKey(0)
cv2.destroyAllWindows()