# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 14:14:32 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2
import numpy as np

#变换函数
# cv2.warpAffine<=(2,3)的变换矩阵
# cv2.warpPerspective<=(3,3)的变换矩阵
#######扩展缩放
#cv2.resize()
# cv2.INTER_AREA(区域插值)<=缩放推荐
# cv2.INTER_CUBIC(三次样条插值,比较慢),cv2.INTER_LINEAR(线性插值,所的默认参数)<=扩展推荐
# cv2.INTER_NEAREST(最近邻插值),cv2.INTER_LANCZOS4(Lanczos插值)
img = cv2.imread('0002.jpg')
#res = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)#缩放因子是2
height,width = img.shape[:2]
res = cv2.resize(img, (2*width,2*height), interpolation=cv2.INTER_CUBIC)

#######平移
#你要沿(x,y)方向移动,移动的距离是(tx,ty)
# 移动矩阵M = [[1, 0, tx],[0, 1, ty]]
move_M = np.float32([[1, 0, 100],[0, 1, 50]])#沿x方向移动100,沿y方向移动50
res_m = cv2.warpAffine(img, move_M, (width,height))

#######旋转
#对一个图像旋转角度θ
# M = [[cosθ, -sinθ],[sinθ, cosθ]]
#任意地方进行旋转
# M = [[α, β, (1-α)*center*x-β*center*y],[-β, α, (1-α)*center*x+β*center*x]]
#  α=scale*cosθ, β=scale*sinθ
#  构建这个旋转矩阵,cv2.getRotationMatrix2D
#可以通过设置旋转中心,缩放因子,以及窗口大小来防止旋转后超出的边界的问题
roll_M = cv2.getRotationMatrix2D((width/2,height/2), 45, 0.6)#旋转中心(width/2,height/2), 旋转角度45, 旋转后的缩放因子0.6
res_r = cv2.warpAffine(img, roll_M, (width,height))

#######仿射变换
#是一种二维坐标到二维坐标之间的线性变化,保持了二维图形的平直性(原图中所有的平行线在结果图像中同样平行)
# 平行性(二维图形之间的相对位置关系保持不变,平行线依旧是平行线,且直线上的点的位置顺序不变)
# x` = ax + by + m
# y` = cx + dy + n
#  ==>[x`, y`].T = [[a, b, m], [c, d, n]]*[x, y, 1].T
#  可以通过一系列原子变换操作复合实现,原子操作包括:平移,缩放,旋转,翻转,错切(剪切,错位变换,产生弹性物体的变形处理)
# 不共线的三对点决定了一个唯一的仿射变换
#2D平面,仿射变换的应用较多
#仿射变换(affine transform)与透视变换(perspective transform)在图像还原,图像局部变化处理方面有重要意义
#cv2.getAffineTransform会创建一个2x3的矩阵,这个矩阵会被传给函数cv2.warpAffine
pts1 = np.float32([[50,50], [200,50], [50,200]])
pts2 = np.float32([[10,100], [200,50], [100,250]])
affine_M = cv2.getAffineTransform(pts1, pts2)
#warpAffine稠密仿射变换,Transform稀疏仿射变换
res_a = cv2.warpAffine(img, affine_M, (width,height))

#######透视变换
#将图像投影到一个新的视平面
# [x`, y`, z`] = [u, v, w]*M
# M = [[a_11, a_12, a_13], [a_21, a_22, a_23], [a_31, a_32, a_33]] = [[T_1, T_2], [T_3, a_33]]
#  T_1 = [[a_11, a_12], [a_21, a_22]]#线性变换
#  T_2 = [a_13, a_23]#透视变换
#  T_3 = [a_31, a_32]#图像平移
#  x = x`/z` = a_11*u+a_21*v+a_31/a_13*u+a_23*v+a_33
#  y = y`/z` = a_12*u+a_22*v+a_33/a_13*u+a_23*v+a_33
# 给定透视变换对应的四点像素坐标(任意三个点不能共线),可以求得透视变换的矩阵
# cv2.getPerspectiveTransform()变换矩阵构建
# cv2.warpPerspective()透视变换
pts1 = np.float32([[56,65], [368,52], [28,387], [389,390]])
pts2 = np.float32([[0,0], [300,0], [0,300], [300,300]])
perspective_M = cv2.getPerspectiveTransform(pts1, pts2)
res_p = cv2.warpPerspective(img, perspective_M, (width,height))

while True:
    cv2.imshow('res', res)
    cv2.imshow('res_m', res_m)
    cv2.imshow('res_r', res_r)
    cv2.imshow('res_a', res_a)
    cv2.imshow('res_p', res_p)
    cv2.imshow('img', img)
    if cv2.waitKey(1) & 0xFF == 27:
        break
cv2.destroyAllWindows()