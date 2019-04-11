# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 18:59:03 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import numpy as np
import cv2

#############图像的加法<=图像的大小类型一致
#opencv的加法操作是一种饱和操作,numpy是一种模操作
x_val = np.uint8([250])
y_val = np.uint8([10])
print(cv2.add(x_val, y_val))#250+10=260 => 255
print(x_val+y_val)#250+10=260 % 256=4

#############图像的混合
#图像的加法就是图像的权重不同,会给人一种混合或者是透明的感觉
#g(x) = (1-α)*f_0(x) + α*f_1(x) + γ混合结果和α的取值有关系
img1 = cv2.imread('0001.jpg')
img2 = cv2.imread('0002.jpg')
dst = cv2.addWeighted(img1, 0.7, img2, 0.3, 0)#0.7*img1 + 0.3*img2 + 0
cv2.imshow('image', dst)
cv2.waitKey(0)
cv2.destroyAllWindows()

#############按位运算
#AND, OR, NOT, XOR<=非矩形ROI的时候这些操作很有用
#若想将某个标志放置在另一幅图上
# 使用加法,颜色会改变,使用混合会得到透明的效果
# 如果是矩形的可以使用ROI，如果不是矩形可以通过按位运算
img2 = cv2.imread('0003.jpg')
rows,cols,channels = img2.shape
roi = img1[0:rows, 0:cols]#放置到左上角
img2gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)#转化称灰度图
#img2gray中灰度值大于175的重置像素值为255=>mask
#函数cv2.threshold()将灰度图二值化
ret, mask = cv2.threshold(img2gray, 175, 255, cv2.THRESH_BINARY)
#bitwise_and bitwise_or bitwise_xor bitwise_not
#颠倒黑白
mask_inv = cv2.bitwise_not(mask)#每个像素值进行二进制非操作,对mask的反转

#对操作区域掩膜
img1_bg = cv2.bitwise_and(roi, roi, mask = mask)
#https://blog.csdn.net/weixin_35732969/article/details/83748054
img2_fg = cv2.bitwise_and(img2, img2, mask = mask_inv)
dst = cv2.add(img1_bg, img2_fg)
img1[0:rows, 0:cols] = dst
cv2.imshow('res', img1)
cv2.waitKey(0)
cv2.destroyAllWindows()