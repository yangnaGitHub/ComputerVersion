# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 15:59:05 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2

#求导,提供三种不同的梯度滤波器(高通滤波器)
#Sobel一阶导数,Scharr(对Sobel使用小的卷积核求解梯度角度的优化)和Laplacian二阶导数
# Sobel算子:算是高斯平滑与微分操作的结合体,抗噪声能力很好,可以设定求导的方向和使用卷积核的大小
#  若卷积核大小是-1,会使用3*3的Scharr滤波器,效果比3*3的Sobel滤波器好(速度相同)
#  3*3的Scharr滤波器
#   x方向:[[-3, 0, 3], [-10, 0, 10], [-3, 0, 3]]
#   y方向:[[-3, -10, -3], [0, 0, 0], [3, 10, 3]]
# Laplacian算子:可以使用二阶导数的形式定义,假设其离散实现类似于二阶Sobel导数
#  K = [[0, 1, 0], [1, -4, 1], [0, 1, 0]]

img = cv2.imread('0001.jpg', 0)
laplacian = cv2.Laplacian(img, cv2.CV_64F)#输出图像的深度cv2.CV_64F,如果是-1就和输入保持一致
sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=5)#只在(1,0)x方向求一阶导数,最大可以求二阶导数
sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=5)#只在(0,1)y方向求一阶导数,最大可以求二阶导数
cv2.imshow('laplacian', laplacian)
cv2.imshow('sobelx', sobelx)
cv2.imshow('sobely', sobely)

'''为何使用cv2.CV_64F
 从黑到白的边界的导数是整数
 从白到黑的边界点导数是负数
 若原图像的深度是np.int8时,所有的负值都会被截断变成0(把边界丢失掉)
 如果这两种边界你都想检测到,最好的办法就是将输出的数据类型设置的更高
 取绝对值然后再把它转回到cv2.CV_8U'''
sobelx8u = cv2.Sobel(img, cv2.CV_8U, 1,0, ksize=5)
cv2.imshow('sobelx8u', sobelx8u)
import numpy as np
abs_sobel64f = np.absolute(sobelx)
sobel_8u = np.uint8(abs_sobel64f)
cv2.imshow('sobel_8u', sobel_8u)

cv2.waitKey(0)
cv2.destroyAllWindows()