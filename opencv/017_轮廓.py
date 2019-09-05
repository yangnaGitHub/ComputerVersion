# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 13:48:21 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2

#轮廓可以简单的认为将连续的点(连着边界)连在一起的曲线,具有相同的颜色或者灰度=>相同灰度值的边界
#轮廓在形状分析和物体检测和识别中很有用
# 更加准确,要使用二值化图像,寻找轮廓之前,要进行阈值化处理或是Canny边界检测
# 查找轮廓的函数会修改原始图像,在找到轮廓之后还想使用原始图像的话要将原始图像存储在其他变量中
# 要找的应该是白色而背景应该是黑色
#如何在一个二值化的图像中查找轮廓
# cv2.findContours()<=输入图像,轮廓检索模式,轮廓近似方法
#  返回值:图像,轮廓(列表,存储图像中所有的轮廓numpy数组),轮廓的层析接口
#怎么绘制轮廓
# cv2.drawContours()被用来绘制轮廓<=原始图像,轮廓,轮廓的索引(绘制独立轮廓的时候有用,-1的时候绘制所有的轮廓),轮廓的颜色和厚度
#  可以根据你提供的边界点绘制任何形状

img = cv2.imread('0001.jpg')
imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret,thresh = cv2.threshold(imgray, 127, 255, 0)#做threshold要是在二值化的图像上操作
#轮廓的近似方法
#会存贮形状边界上所有的(x,y)坐标,需要将所有的这些边界点都存储吗
#参数如果被设置为cv2.CHAIN_APPROX_NONE所有的边界点都会被存储
#cv2.CHAIN_APPROX_SIMPLE会将轮廓上的冗余点都去掉,压缩轮廓,从而节省内存开支
image,contours,hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

#绘制独立轮廓,绘制第4个轮廓
img_a = cv2.drawContours(img, contours, -1, (0,255,0), 3)
img_4 = cv2.drawContours(img, contours, 3, (0,255,0), 3)
cv2.imshow('img_a', img_a)
cv2.imshow('img_4', img_4)

cv2.waitKey(0)
cv2.destroyAllWindows()