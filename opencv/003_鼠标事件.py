# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 11:32:48 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2
import numpy as np

#使用OpenCV处理鼠标事件
#1.创建一个鼠标事件回调函数,鼠标发生动作的时候执行
 #鼠标按下,鼠标弹起,双击等等
#通过鼠标事件获得与鼠标对应的图片上的坐标
'''
events = [index for index in dir(cv2) if 'EVENT'in index]#所有的事件
#'EVENT_FLAG_ALTKEY', 'EVENT_FLAG_CTRLKEY', 'EVENT_FLAG_LBUTTON', 'EVENT_FLAG_MBUTTON'
#'EVENT_FLAG_RBUTTON', 'EVENT_FLAG_SHIFTKEY', 'EVENT_LBUTTONDBLCLK', 'EVENT_LBUTTONDOWN'
#'EVENT_LBUTTONUP', 'EVENT_MBUTTONDBLCLK', 'EVENT_MBUTTONDOWN', 'EVENT_MBUTTONUP'
#'EVENT_MOUSEHWHEEL', 'EVENT_MOUSEMOVE', 'EVENT_MOUSEWHEEL', 'EVENT_RBUTTONDBLCLK'
#'EVENT_RBUTTONDOWN', 'EVENT_RBUTTONUP'
'''
def draw_circle(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:#左边双击
        cv2.circle(img, (x,y), 100, (255,0,0), -1)

drawing = False
mode = True
ix,iy = -1,-1
def draw_circle_01(event, x, y, flags, param):
    global ix,iy,drawing,mode#使用全局变量
    if event == cv2.EVENT_LBUTTONDOWN:#左键按下,记录为起始点
        drawing = True
        ix,iy = x,y#开始的点
    elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:#左键按下并移动
        if drawing==True:
            #按下m切换画的图像
            if mode==True:
                cv2.rectangle(img, (ix,iy), (x,y), (0,255,0), -1)#画矩形
            else:
                #小圆形在一起就变成了直线
                #cv2.circle(img, (x,y), 3, (0,0,255), -1)#画圆形
                r = int(np.sqrt((x-ix)**2 + (y-iy)**2))#计算半径,这是一个连续的过程
                cv2.circle(img, (x,y) , r, (0,0,255), -1)
    elif event==cv2.EVENT_LBUTTONUP:#左键弹起就画了
        drawing==False

img = np.zeros((512,512,3), np.uint8)
cv2.namedWindow('image')
#cv2.setMouseCallback('image', draw_circle)
cv2.setMouseCallback('image', draw_circle_01)

while True:
    cv2.imshow('image', img)
    key_val = cv2.waitKey(1)&0xFF
    if key_val == 27:
        break
    elif ord('m') == key_val:
        mode = not mode

cv2.destroyAllWindows()