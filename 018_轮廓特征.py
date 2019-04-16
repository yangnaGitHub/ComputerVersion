# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 13:48:51 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2

#查找轮廓的不同特征
#1.矩,图像的各类几何特征,包含了很多轮廓的特征信息
# 图像的矩可以帮助计算图像的质心,面积等(Image Moments)
#  cv2.moments()会计算得到的矩以一个字典的形式返回
img = cv2.imread('0001.jpg', 0)
ret,thresh = cv2.threshold(img, 127, 255, 0)
#cv2.RETR_CCOMP建立两个等级的轮廓上面的一层为外边界里面的一层为内孔的边界信息,cv2.CHAIN_APPROX_SIMPLE
image,contours,hierarchy = cv2.findContours(thresh, 1, 2)
cnt = contours[0]#第1个轮廓为例子
M = cv2.moments(cnt)
print(M)
# 根据矩的值,计算对象的重心Cx=M['m10']/M['m00'],Cy=M['m01']/M['m00']
cx = 0 if 0 == M['m00'] else int(M['m10']/M['m00'])
cy = 0 if 0 == M['m00'] else int(M['m01']/M['m00'])

#2.轮廓面积
# cv2.contourArea()或者是使用矩(0阶矩)M['m00']
area = cv2.contourArea(cnt)
print(area)

#3.轮廓周长(弧长)
# cv2.arcLength()<=第二参数可以用来指定对象的形状是闭合的(True)还是打开的(一条曲线)
perimeter = cv2.arcLength(cnt, True)
print(perimeter)

#4.轮廓近似
# 将轮廓形状近似到另外一种由更少点组成的轮廓形状,新轮廓的点的数目由设定的准确度来决定(Douglas-Peucker)
epsilon = 0.1*cv2.arcLength(cnt, True)#从原始轮廓到近似轮廓的最大距离,准确度参数,好的epsilon对于得到满意结果非常重要
approx = cv2.approxPolyDP(cnt, epsilon, True)#True设定弧线是否闭合
cv2.imshow('approx', approx)

#5.凸包
# cv2.convexHull()用来检测一个曲线是否具有凸性缺陷,并能纠正缺陷
# 凸性曲线总是凸出来的,如果有地方凹进去了就被叫做凸性缺陷
# hull = cv2.convexHull(points[, hull[, clockwise[, returnPoints]]
# points:传入的轮廓
# hull:输出,通常不需要
# clockwise:方向标志,True输出的凸包是顺时针方向的,False逆时针方向
# returnPoints:默认值为True(返回凸包上点的坐标,查找凸包),False(返回与凸包点对应的轮廓上的点,获得凸性缺陷设置成False)
hull = cv2.convexHull(cnt)

#6.凸性检测
# cv2.isContourConvex()用来检测一个曲线是不是凸的
# 只能返回True或False
k = cv2.isContourConvex(cnt)
print(k)

#7.边界矩形
# 直边界矩形:一个直矩形(没有旋转),不会考虑对象是否旋转,所以边界矩阵的面积不是最小的
#  cv2.boundingRect()
x,y,w,h = cv2.boundingRect(cnt)
Rect_M = cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)#画出这个框
# 旋转的边界矩形:边界矩形是面积最小的,考虑了对象的旋转
#  cv2.minAreaRect()<=Box2D结构,包含左上角角点的坐标(x,y),矩形的宽和高(w,h),以及旋转角度
#  绘制这个矩形需要矩形的4个角点<=cv2.boxPoints()获得
rect = cv2.minAreaRect(cnt)#得到最小外接矩形的
box = cv2.boxPoints(rect)
import numpy as np
box = np.int0(box)
Rect = cv2.drawContours(img ,[box], 0, (0,0,255), 2)
cv2.imshow('Rect', Rect)

#8.最小外接圆
# cv2.minEnclosingCircle()找到一个对象的外切圆,是所有能够包括对象的圆中面积最小的一个
(x,y),radius = cv2.minEnclosingCircle(cnt)
center = (int(x),int(y))
radius = int(radius)
circle = cv2.circle(img, center, radius, (0,255,0), 2)
cv2.imshow('circle', circle)

#9.椭圆拟合
# cv2.ellipse()返回值其实就是旋转边界矩形的内切圆
ellipse = cv2.fitEllipse(cnt)
ellipse = cv2.ellipse(img, ellipse, (0,255,0), 2)
cv2.imshow('ellipse', ellipse)

#10.直线拟合
# 根据一组点拟合出一条直线
rows,cols = img.shape[:2]
[vx,vy,x,y] = cv2.fitLine(cnt, cv2.DIST_L2, 0, 0.01, 0.01)
lefty = int((-x*vy/vx) + y)
righty = int(((cols-x)*vy/vx) + y)
img = cv2.line(img, (cols-1,righty), (0,lefty), (0,255,0), 2)

cv2.waitKey(0)
cv2.destroyAllWindows()