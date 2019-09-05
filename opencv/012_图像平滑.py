# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 15:04:44 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2
import numpy as np

#对2D图像实施低通滤波(LPF)[去除噪音,模糊图像],高通滤波(HPF)[找到图像的边缘]
#cv.filter2D()可以让我们对一幅图像进行卷积操作
#5*5的平均滤波器的kernel
# K = 1/25{[1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1]}
# 与K对应图像上的25(5*5)个像素的和,在取平均数,用这个平均数代替像素A上的值
img = cv2.imread('0001.jpg')
kernel = np.ones((5,5), np.float32)/25
#-1输出和输入是一样的深度
dst = cv2.filter2D(img, -1, kernel)
cv2.imshow('dst', dst)#模糊的效果

#使用低通滤波器可以达到图像模糊的目的,这对去除噪音很有帮助,其实就是去除图像中的高频成分(噪音,边界)
#4种模糊技术
# 平均:是由一个归一化卷积框完成的,只是用卷积框覆盖区域上所有像素的平均值来代替中心元素
#  cv2.blur()+cv2.boxFilter()[不是用归一化卷积框的时候参数normalize=False]
blur = cv2.blur(img, (5,5))
cv2.imshow('blur', blur)
# 高斯模糊:卷积核换成高斯核,之前平均每个框中的值是相等的,现在是符合高斯分布的
#         方框中心的值最大,其余方框根据距离中心元素的距离递减,现在求加权平均数
#         可以有效的从图像中去除高斯噪音
#  cv2.GaussianBlur()需要指定高斯核的宽和高(注意必须是奇数)+高斯函数沿X,Y方向的标准差,为0就自己算
# 可以使用函数cv2.getGaussianKernel()自己构建一个高斯核
blur_g = cv2.GaussianBlur(img, (5,5), 0)#0标准差自己算
cv2.imshow('blur_g', blur_g)
# 中值模糊:卷积框对应像素的中值来代替中心像素的值,这个滤波一般用来去除椒盐噪声,卷积核大小也是一个奇数
#  cv2.medianBlur
median = cv2.medianBlur(img, 5)
cv2.imshow('median', median)
# 双边滤波:在保持边界清晰的情况下有效的去除噪音,操作比较慢
#         高斯只会考虑像素之间的空间关系,而不会考虑像素值之间的关系(像素的相似度),不会考虑一个像素是否位于边界=>边界也会模糊
#         在同时使用空间高斯权重和灰度值相似性高斯权重(确保只有与中心像素灰度值相近的才会被用来做模糊运算)=>边界处的灰度值变化比较大
#  cv2.bilateralFilter()
#领域直径:9,75分别是空间和灰度值相似度高斯函数的标准差
blur_b = cv2.bilateralFilter(img, 9, 75, 75)
cv2.imshow('blur_b', blur_b)

cv2.waitKey(0)
cv2.destroyAllWindows()