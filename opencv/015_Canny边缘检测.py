# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 13:46:57 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2

#Canny边缘检测算法
#1.使用kernel=5的高斯滤波器去除噪声,边缘检测很容易受到噪声的影响
#2.计算图像梯度
# 对平滑后的图像使用Sobel算子计算水平方向和竖直方向的一阶导数,得到Gx和Gy边界的梯度和方向
#  G = sqrt(Gx**2+Gy**2)
#  θ = [tan(Gx/Gy)]_-1
# 梯度的方向一般总是与边界垂直,被分为四类:垂直,水平,两个对角线
#3.非极大值抑制=>包含窄边界的二值图像
# 整幅图像做一个扫描,去除非边界上的点,对每一个像素检查,看这个像素的梯度是不是周围具有相同梯度方向的点中最大的
#4.滞后阈值=>确定哪些边界才是真正的边界
# 阈值,当图像灰度图高于maxVal的时候被认为是真的边界,低于minVal的边界会被抛弃
# 介于之间的要看这个点是否与某个被确定为真正的边界点相连,如果相连就认为也是边界点
# 选择合适的阈值对于是否能得到好的结果是非常重要的
# 在这一步一些小的噪声也会被除去
#cv2.Canny()<=输入图像,maxVal,minVal,Sobel卷积核的大小(默认是3),L2gradient(设定求梯度大小的方程,默认值False)
# L2gradient:True<=上面提到过的方程
#            False<=G = abs(Gx**2)+abs(Gy**2)

img = cv2.imread('0001.jpg', 0)
edges = cv2.Canny(img, 100, 200)

cv2.imshow('edges', edges)

cv2.waitKey(0)
cv2.destroyAllWindows()