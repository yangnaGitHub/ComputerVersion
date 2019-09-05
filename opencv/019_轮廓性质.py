# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 13:50:10 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2

#提取一些经常使用的对象特征
img = cv2.imread('0001.jpg', 0)
ret,thresh = cv2.threshold(img, 127, 255, 0)
image,contours,hierarchy = cv2.findContours(thresh, 1, 2)
cnt = contours[0]
#1.长宽比
# 边界矩形的宽高比
x,y,w,h = cv2.boundingRect(cnt)
aspect_ratio = float(w)/h
print(aspect_ratio)

#2.Extent:轮廓面积与边界矩形的比
area = cv2.contourArea(cnt)
x,y,w,h = cv2.boundingRect(cnt)
rect_area = w*h
extent = float(area)/rect_area
print(extent)

#3.Solidity:轮廓面积与凸包面积的比
hull = cv2.convexHull(cnt)
hull_area = cv2.contourArea(hull)
solidity = float(area)/hull_area
print(solidity)

#4.Equivalent Diameter:与轮廓面积相等的圆形的直径
import numpy as np
equi_diameter = np.sqrt(4*area/np.pi)
print(equi_diameter)

#5.方向:对象的方向
(x,y),(MA,ma),angle = cv2.fitEllipse(cnt)#返回长轴和短轴的长度

#6.掩模和像素点<=需要构成对象的所有像素点
imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
mask = np.zeros(imgray.shape, np.uint8)
cv2.drawContours(mask, [cnt] , 0, 255, -1)#一定要使用参数-1绘制填充的的轮廓
pixelpoints = np.transpose(np.nonzero(mask))

#7.最大值和最小值及它们的位置<=可以使用掩模图像得到这些参数
min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(imgray, mask = mask)

#8.平均颜色及平均灰度
# 可以使用相同的掩模求一个对象的平均颜色或平均灰度
mean_val = cv2.mean(img, mask = mask)

#9.极点
# 对象最上面,最下面,最左边,最右边的点
leftmost = tuple(cnt[cnt[:,:,0].argmin()][0])
rightmost = tuple(cnt[cnt[:,:,0].argmax()][0])
topmost = tuple(cnt[cnt[:,:,1].argmin()][0])
bottommost = tuple(cnt[cnt[:,:,1].argmax()][0])

#10.凸缺陷<=对象上的任何凹陷都被成为凸缺陷
# cv.convexityDefect()找到凸缺陷
#返回一个数组,每一行包含的值是[起点,终点,最远的点,到最远点的近似距离]
hull = cv2.convexHull(cnt, returnPoints = False)#查找凸缺陷returnPoints要设置成False
defects = cv2.convexityDefects(cnt, hull)
for index in range(defects.shape[0]):
    s,e,f,d = defects[index, 0]
    start = tuple(cnt[s][0])
    end = tuple(cnt[e][0])
    far = tuple(cnt[f][0])
    cv2.line(img, start, end, [0,255,0], 2)
    cv2.circle(img, far, 5, [0,0,255], -1)
cv2.imshow('img', img)

#11.Point Polygon Test<=图像中的一个点到一个对象轮廓的最短距离
# 点在轮廓的外部,返回值为负
# 在轮廓上,返回值为0
# 在轮廓内部,返回值为正
dist = cv2.pointPolygonTest(cnt, (50,50), True)#measureDist=True会计算最短距离,False只判断这个点换个轮廓的位置关系(返回值是+/-1和0)

#12.形状匹配
# cv2.matchShape()比较两个形状或轮廓的相似度,返回值越小,匹配越好,是根据Hu矩来计算的
# Hu矩是归一化中心矩的线性组合,能够获取代表图像的某个特征的矩函数
# 矩函数对某些变化如缩放,旋转,镜像映射(除了h1)具有不变形
img2 = cv2.imread('0002.jpg', 0)
ret,thresh2 = cv2.threshold(img2, 127, 255, 0)
contours,hierarchy = cv2.findContours(thresh2, 2, 1)
cnt2 = contours[0]
ret = cv2.matchShapes(cnt, cnt2, 1, 0.0)
print(ret)

#学习轮廓的层次结构
# 一个形状在另外一个形状的内部,称外部的形状为父,内部的形状为子,所有轮廓之间就建立父子关系,确定一个轮廓与其他轮廓是怎样连接的
# 一个含有四个元素的数组表示[Next,Previous,First_Child,Parent]
#  Next表示同一级组织结构中的下一个轮廓,同一级没有Next的时候=-1
#  Previous表示同一级结构中的前一个轮廓,同一级没有Previous的时候=-1
#  First_Child表示它的第一个子轮廓,没有子=-1
#  Parent表示它的父轮廓,没有父=-1
# 轮廓检索模式
#  RETR_LIST提取所有的轮廓,不去创建任何父子关系(人人平等First_Child=-1,Parent=-1)<=不关心轮廓之间的关系
#  RETR_EXTERNAL返回最外边的的轮廓,所有的子轮廓都会被忽略掉<=只会返回最外边的轮廓(第0级)
#  RETR_CCOMP所有的轮廓并将轮廓分为两级组织结构
#  RETR_TREE返回所有轮廓,创建一个完整的组织结构列表

cv2.waitKey(0)
cv2.destroyAllWindows()