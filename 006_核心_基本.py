# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 18:24:28 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2
import numpy as np

img = cv2.imread('0001.jpg')

#####修改像素值
#修改像素值方法1
print(img[100, 100])
img[100,100] = [255,255,255]
print(img[100, 100])
#修改像素值方法2
print(img.item(10,10,2))
img.itemset((10,10,2), 100)
print(img.item(10,10,2))

#####get图像的属性
#图像的属性包括:行,列,通道,图像数据类型,像素数目
#img.shape可以获取图像的形状,返回值是一个包含行数,列数,通道数的元组
print(img.shape)#灰度图,返回值仅有行数和列数,通过检查这个返回值就可以知道加载的是灰度图还是彩色图
#img.size可以返回图像的像素数目
print(img.size)
#img.dtype返回的是图像的数据类型
print(img.dtype)#非常重要,经常出现数据类型的不一致

#####选择一个区域
#图像ROI,要对一幅图像的特定区域进行操作
 #检测一副图像中眼睛的位置,首先应该在图像中找到脸,再在脸的区域中找眼睛<=逐步缩小范围,提高准确性和性能
rot_section = img[280:340,330:390]
img[500:560,100:160] = rot_section

#####拆分及合并图像通道
#比较耗时的操作,最好用索引操作img[:,:,0]
b,g,r = cv2.split(img)#b = img[:,:,0],g = img[:,:,1],r = img[:,:,2]
#img[:,:,2] = 0所有像素的红色通道值都为0
img = cv2.merge([g,r,b])

cv2.imshow('image', img)
if cv2.waitKey(0) & 0xFF == ord('q'):
    cv2.destroyAllWindows()

#####图像扩边填充
#图像周围创建一个边像相框一样<=cv2.copyMakeBorder()
#卷积运算或0填充时被用到
#输入图像,(top,bottom,left,right对应边界的像素数目),borderType要添加那种类型的边界,value边界颜色(cv2.BORDER_CONSTANT)
 #borderType:cv2.BORDER_CONSTANT<=有颜色的常数值边界<=value
  #cv2.BORDER_REFLECT边界元素的镜像<=cv2.BORDER_REFLECT_101
  #cv2.BORDER_REPLICATE重复最后一个元素
  #cv2.BORDER_WRAP
from matplotlib import pyplot as plt
BLUE = [255,0,0]#plt显示是红色
replicate = cv2.copyMakeBorder(img, 10, 10, 10, 10, cv2.BORDER_REPLICATE)
reflect = cv2.copyMakeBorder(img, 10, 10, 10, 10, cv2.BORDER_REFLECT)
reflect101 = cv2.copyMakeBorder(img, 10, 10, 10, 10, cv2.BORDER_REFLECT_101)
wrap = cv2.copyMakeBorder(img, 10, 10, 10, 10, cv2.BORDER_WRAP)
constant= cv2.copyMakeBorder(img, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=BLUE)
plt.subplot(231), plt.imshow(img, 'gray'), plt.title('ORIGINAL')
plt.subplot(232), plt.imshow(replicate, 'gray'), plt.title('REPLICATE')
plt.subplot(233), plt.imshow(reflect, 'gray'), plt.title('REFLECT')
plt.subplot(234), plt.imshow(reflect101, 'gray'), plt.title('REFLECT_101')
plt.subplot(235), plt.imshow(wrap, 'gray'), plt.title('WRAP')
plt.subplot(236), plt.imshow(constant, 'gray'), plt.title('CONSTANT')#plt显示是红色
plt.show()