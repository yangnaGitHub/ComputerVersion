# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 11:32:46 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2
import numpy as np

#图像,颜色(BGR),粗细-1填充,线条类型
#所有的绘图函数的返回值都是None

#背景
img = np.zeros((512,512,3), np.uint8)#背景,全0,黑色
#Line
cv2.line(img, (0,0), (511,511), (255,0,0), 5)#一条直线(0,0)-(511,511)蓝色的5像素宽的直线
#矩阵
cv2.rectangle(img, (384,0), (510,128), (0,255,0), 3)#一个左上角(384,0)-右下角(510,128)的绿色的3像素宽的矩阵
#圆
cv2.circle(img, (447,63), 63, (0,0,255), -1)#中心坐标点(447,63)和半径=63的红色全填充
#椭圆
#中心点的位置坐标(256,256),长轴和短轴的长度(100,50),逆时针方向旋转的角度0,顺时针方向起始的角度0和结束角度180(若是0-360就是整个椭圆)
cv2.ellipse(img, (256,256), (100,50), 0, 0, 180, (255,255,0), -1)
#多边形,需要指点每个顶点的坐标,行数就是点的数目,数组的数据类型必须为int32
pts=np.array([[10,5], [20,30], [70,20], [50,10]], np.int32)#4个定点
pts=pts.reshape((-1, 1, 2))
cv2.polylines(img, [pts], True, (0,255,255))
#cv2.polylines(img, [pts], False, (0,255,255))#多边形是不闭合的,首尾不相连
#图片上添加文字
 #绘制的文字,绘制的位置,字体类型通过cv2.putText()可查看,大小,一般属性颜色粗细线条cv2.LINE_AA等
font=cv2.FONT_HERSHEY_SIMPLEX
cv2.putText(img, 'yangna', (10,500), font, 4, (255,255,255), 2, cv2.LINE_AA)

winname = '002'
cv2.namedWindow(winname)
cv2.imshow(winname, img)
cv2.waitKey(0)
cv2.destroyWindow(winname)