# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 13:51:27 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2
import numpy as np
from matplotlib import pyplot as plt

#大多数像素点的像素值都集中在一个像素值范围之内
#一幅图片整体很亮,所有的像素值应该都会很高
#一副高质量的图像的像素值分布应该很广泛<=应该把它的直方图做一个横向拉伸
#直方图均衡化:直方图做一个横向拉伸(改善图像的对比度)

img = cv2.imread('0001.jpg', 0)

########numpy的直方图均衡化
#flatten将数组变成一维
hist,bins = np.histogram(img.flatten(), 256, [0,256])
#计算累积分布图
cdf = hist.cumsum()
cdf_normalized = cdf * hist.max()/cdf.max()
plt.plot(cdf_normalized, color = 'b')
plt.hist(img.flatten(), 256, [0,256], color = 'r')
plt.xlim([0,256])
plt.legend(('cdf','histogram'), loc = 'upper left')
plt.show()
#希望直方图的分布比较分散,能够涵盖整个x轴
#把现在的直方图映射到一个广泛分布的直方图<=直方图均衡化
#Numpy的掩模数组,掩模数组的所有操作都只对non-masked元素有效
cdf_m = np.ma.masked_equal(cdf, 0)#当数组元素为0时,掩盖(计算被忽略)
cdf_m = (cdf_m-cdf_m.min())*255 / (cdf_m.max()-cdf_m.min())
cdf = np.ma.filled(cdf_m,0).astype('uint8')#对被掩盖的元素赋值,这里赋值为0
img2 = cdf[img]
#绘制直方图和累积分布图


#直方图均衡化经常用来使所有的图片具有相同的亮度条件的参考工具
# 脸部识别<=训练分类器前,所有图片都要先进行直方图均衡化从而使它们达到相同的亮度条件

########opencv的直方图均衡化
# cv2.equalizeHist()直方图均衡化函数<=输入图片仅仅是一副灰度图像
equ = cv2.equalizeHist(img)
res = np.hstack((img, equ))
cv2.imshow('res', res)

########CLAHE有限对比适应性直方图均衡化
#整幅图像会被分成很多小块(tiles,默认大小是8*8),对每一个小块分别进行直方图均衡化
#每一个的区域中,直方图会集中在某一个小的区域中(有噪声的话,噪声会被放大,避免这种情况的出现要使用对比度限制)
#对于每个小块,直方图中的bin超过对比度的上限的话,就把其中的像素点均匀分散到其他bins中,然后在进行直方图均衡化
#为了去除每一个小块之间'人造的'(由于算法造成)边界,再使用双线性差值,对小块进行缝合
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
cl1 = clahe.apply(img)
cv2.imshow('cl1', cl1)

cv2.waitKey(0)
cv2.destroyAllWindows()