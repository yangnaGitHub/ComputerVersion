# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 10:27:57 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2

#1.read
#cv2.imread()读入图像=>图片路径,应该如何读取这幅图片
# cv2.IMREAD_COLOR(1)彩色图像透明度会被忽略(默认参数)
# cv2.IMREAD_GRAYSCALE(0)灰度模式
# cv2.IMREAD_UNCHANGED(-1)包括图像的alpha通道
img = cv2.imread('0001.jpg', 0)#灰度图
#2.op

#3.show
#cv2.imshow()显示图像,窗口会自动调整为图像大小=>窗口的名字,图像
#可以创建多个窗口,但是必须给他们不同的名字
'''
#先创建一个窗口,之后再加载图像,可以决定窗口是否可以调整大小cv2.namedWindow(),初始设定函数标签是cv2.WINDOW_AUTOSIZE
#如果你把标签改成cv2.WINDOW_NORMAL就可以调整窗口大小了
cv2.namedWindow('0002', cv2.WINDOW_NORMAL)#可以调整窗口的大小
'''
cv2.imshow('0001', img)
cv2.waitKey(0)#0将无线等待下去,单位是毫秒,按下任意键返回按键的ASCII码,没有按键就返回-1
 #返回值27[ESC],64bit的系统返回值要固定在0-256之间
cv2.destroyAllWindows()#删除所有刚建立的窗口,删除特定的窗口可以使用cv2.destroyWindow()=>窗口的名字

#4.save
#cv2.imwrite()保存一个图像=>保存的文件名,保存的对象
cv2.imwrite('0001_s.png', img)

#一些说明
#彩色图像使用OpenCV加载时是BGR模式,Matplotib是RGB模式,所以彩色图像如果已经被OpenCV读取,那它将不会被Matplotib正确显示
#https://stackoverflow.com/questions/15072736/extracting-a-region-from-an-image-using-slicing-in-python-opencv/15074748#15074748
import matplotlib.pyplot as plt
img = cv2.imread('0002.jpg')
b,g,r = cv2.split(img)
img2 = cv2.merge([r,g,b])
plt.subplot(121)
plt.imshow(img)
plt.subplot(122)
plt.imshow(img2)#重新组合的rgb格式的
plt.show()
cv2.imshow('bgr image', img)
cv2.imshow('rgb image', img2)
cv2.waitKey(0)
cv2.destroyAllWindows()