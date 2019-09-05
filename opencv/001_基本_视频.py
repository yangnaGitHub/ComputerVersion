# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 10:53:41 2019

@author: yangna

@e-mail: ityangna0402@163.com
"""

import cv2

#1.创建一个VideoCapture对象=>设备索引号0代表内置,其他代表其他的摄像头/视频文件
cap = cv2.VideoCapture(0)

#2.读取操作存储等操作
#可以使用函数cap.get(propId)来获得视频的一些参数信息,propId<=[0-18],每一个数字代表视频的一个属性
 #cap.get(3)和cap.get(4)来查看每一帧的宽和高
#可以使用cap.set(propId,value)来修改,value就是你想要设置成的新值
 #ret=cap.set(3,320)和ret=cap.set(4,240)来把宽和高改成 320X240
'''
#2.11保存视频文件
#定义Codec和写对象创建一个VideoWriter的对象
#cv2.cv.FOURCC('M','J','P','G') or cv2.cv.FOURCC(*'MJPG')
fourcc = cv2.VideoWriter_fourcc(*'DIVX')#指定FourCC编码,4字节码确定视频的编码格式<=fourcc.org上可以查到
out = cv2.VideoWriter('001_基本_视频_01.avi', fourcc, 20.0, (640,480))#文件名字,指定编码,播放频率,帧的大小,是否是彩色图
'''

'''
#cap可能不能成功的初始化摄像头设备,可使用cap.isOpened()来检查是否成功初始化了,返回值是True打开成功
#返回值是False,使用函数cap.open()打开
while(cap.isOpened()):
'''
while True:
    
    ret, frame = cap.read()#一帧一帧的读取数据
    
    '''
    2.12写操作
    #返回一个布尔值,帧读取的是正确就是True
    #可以通过检查他的返回值ret=False来查看视频文件是否已经到了结尾
    if ret==True:
        frame = cv2.flip(frame, 0)
        out.write(frame)#写文件
        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break
    '''
    
    #显示操作
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)#BGR的彩图转成灰度图
    cv2.imshow('frame', gray)#显示
    if cv2.waitKey(1) & 0xFF == ord('q'):#按键q退出,使用cv2.waiKey()设置适当的持续时间,可控制播放速度
        break

#3.清理工作,放弃控制权,释放对象,delete
cap.release()
'''
out.release()
'''

cv2.destroyAllWindows()