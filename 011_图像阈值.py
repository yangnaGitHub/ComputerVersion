# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 18:01:15 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2

#像素值高于阈值时,给这个像素赋予一个新值cv2.threshhold()
img = cv2.imread('0001.jpg', 0)
#大于127的设置成阈值255(白),小于127为0(黑)
ret,thresh1 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)#高于127的全部成255
#大于127为0(黑),小于127的设置成阈值255(白)
ret,thresh2 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
#大于127为阈值255(白),小于127的不变
ret,thresh3 = cv2.threshold(img, 127, 255, cv2.THRESH_TRUNC)
#大于127的不变,小于127的是0(黑)
ret,thresh4 = cv2.threshold(img, 127, 255, cv2.THRESH_TOZERO)
#大于127的是0(黑色),大于127的不变
ret,thresh5 = cv2.threshold(img, 127, 255, cv2.THRESH_TOZERO_INV)

#from matplotlib import pyplot as plt
titles = ['Original Image', 'BINARY', 'BINARY_INV', 'TRUNC', 'TOZERO', 'TOZERO_INV']
images = [img, thresh1, thresh2, thresh3, thresh4, thresh5]
for index,title in enumerate(titles):
    cv2.imshow(title, images[index])
cv2.waitKey(0)
cv2.destroyAllWindows()
#    plt.subplot(2, 3, index+1),
#    plt.imshow(images[index],'gray')
#    plt.title(title)
#    plt.xticks([])
#    plt.yticks([])
#plt.show()

##########自适应阈值
#阈值是根据图像上的每一个小区域计算与其对应的阈值
#在同一幅图像上的不同区域采用的是不同的阈值
#指定计算阈值的方法,邻域大小,C是一个常数(阈值就等于的平均值或者加权平均值减去这个常数)
# cv2.ADPTIVE_THRESH_MEAN_C阈值取自相邻区域的平均值
# cv2.ADPTIVE_THRESH_GAUSSIAN_C阈值取值相邻区域的加权和,权重为一个高斯窗口
img = cv2.medianBlur(img, 5)#中值滤波
#邻域大小=11,C=2
th2 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
th3 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
cv2.imshow('th2', th2)
cv2.imshow('th3', th3)
cv2.waitKey(0)
cv2.destroyAllWindows()

##########Otsu’s二值化
#怎么知道选取的阈值的好坏<=不停的尝试
#双峰图像是指图像直方图中存在两个峰,对一副双峰图像自动根据其直方图计算出一个阈值
# 找到一个阈值,使得同一类加权方差最小,两个峰之间找到一个阈值t,将这两个峰分开,使每一个峰内的方差最小
'''
import numpy as np
blur = cv2.GaussianBlur(img, (5,5), 0)
#计算归一化直方图
hist = cv2.calcHist([blur], [0], None, [256], [0,256])#(256, 1)
hist_norm = hist.ravel()/hist.max()#(256,)
Q = hist_norm.cumsum()#[1,2,3]=>[1,3,6]累加
bins = np.arange(256)
fn_min = np.inf
thresh = -1
for index in range(1,256):
    p1,p2 = np.hsplit(hist_norm, [index])#分离出来
    q1,q2 = Q[index],Q[255]-Q[index]#
    b1,b2 = np.hsplit(bins, [index])
    m1,m2 = np.sum(p1*b1)/q1, np.sum(p2*b2)/q2
    v1,v2 = np.sum(((b1-m1)**2)*p1)/q1,np.sum(((b2-m2)**2)*p2)/q2
    fn = v1*q1 + v2*q2
    if fn < fn_min:
        fn_min = fn
        thresh = index
ret, otsu = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
'''
# cv2.THRESH_OTSU,阈值设为0,算法会找到最优阈值,最优阈值就是返回值retVal
ret4,th4 = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
#高斯核大小是(5,5), 0是标准差
blur = cv2.GaussianBlur(img, (5,5), 0)#高斯核除去噪音
ret5,th5 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
cv2.imshow('th4', th4)
cv2.imshow('blur', blur)
cv2.imshow('th5', th5)
cv2.waitKey(0)
cv2.destroyAllWindows()