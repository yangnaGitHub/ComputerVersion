# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 13:47:35 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2

#不知道目标在图像中的尺寸大小,我们需要创建一组图像,这些图像具有不同的分辨率的原始图像
#同一图像的不同分辨率的子图集合:图像金字塔
# 最大图像放在底部,最小图像放在顶部
#高斯金字塔和拉普拉斯金字塔
#高斯金字塔的顶部是通过将底部图像中连续的行和列去除得到的
# 顶部图像中的每个像素值都等于下一层图像中5个像素的高斯加权平均值
# 操作一次一个m*n的图像就变成了一个m/2*n/2的图像,这幅图像的面积就变成了原来图像面积的1/4=>Octave
# 连续操作可以得到一个一个分辨率不断下降的图像金字塔
# cv2.pyrDown()从一个高分辨大尺寸的图像上构建一个金字塔(尺寸变小,分辨率降低)
#  分辨率降低,信息会被丢失
#img = cv2.imread('0001.jpg')
#lower_reso = cv2.pyrDown(img)
#cv2.imshow('lower_reso', lower_reso)
# cv2.pyrUp()一个低分辨率小尺寸的图像向下构建一个金字塔(尺寸变大,分辨率不会增加)
#higher_reso2 = cv2.pyrUp(lower_reso)#结果会比原图模糊很多
#cv2.imshow('higher_reso2', higher_reso2)

#拉普拉斯金字塔图像看起来像边界图,其中很多像素都是0,经常被用在图像压缩中
#图像金字塔的一个应用是图像融合,图像缝合中需要将两幅图叠在一起,但是由于连接区域图像像素的不连续性,使得效果开起来很差
# 图像金字塔可以实现无缝连接
# 1.读入两幅图像
img_a = cv2.imread('0001.jpg')
img_b = cv2.imread('0002.jpg')
# 2.构建两幅图像的高斯金字塔
temp_a = img_a.copy()
gp_a = [temp_a]#若原图是1024*1024
temp_b = img_b.copy()
gp_b = [temp_b]
for index in range(6):
    temp_a = cv2.pyrDown(temp_a)
    gp_a.append(temp_a)
    temp_b = cv2.pyrDown(temp_b)
    gp_b.append(temp_b)
#1024*1024, 512*512, 256*256, 128*128, 64*64, 32*32, 16*16
# 3.根据高斯金字塔计算拉普拉斯金字塔
lp_a = [gp_a[5]]
lp_b = [gp_b[5]]#32*32
for index in range(5, 0, -1):
    temp = cv2.pyrUp(gp_a[index])#index=5[64*64]要和index=4的做subtract
    diff = cv2.subtract(gp_a[index-1], temp)#图像gp_a[index-1]与temp相减
    lp_a.append(diff)#32*32, 64*64, 128*128, 256*256, 512*512, 1024*1024
    temp = cv2.pyrUp(gp_b[index])
    diff = cv2.subtract(gp_b[index-1], temp)
    lp_b.append(diff)#32*32, 64*64, 128*128, 256*256, 512*512, 1024*1024
# 4.拉普拉斯的每一层进行图像融合
import numpy as np
l_a = []
for la,lb in zip(lp_a, lp_b):
    rows,cols,dpt = la.shape
    la = np.hstack((la[:,0:cols//2], lb[:, cols//2:]))
    l_a.append(la)
# 5.根据融合后的图像金字塔重新构建原始图像
la_ = l_a[0]#32*32
for index in range(1,6):
    la_ = cv2.pyrUp(la_)#64*64, 128*128, 256*256, 512*512, 1024*1024
    la_ = cv2.add(la_, l_a[index])
real = np.hstack((img_a[:,:cols//2], img_b[:,cols//2:]))

cv2.imshow('la_', la_)
cv2.imshow('real', real)

cv2.waitKey(0)
cv2.destroyAllWindows()