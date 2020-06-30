#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed May 29 09:47:35 2019

@author: yangna
"""

import ctypes
from ctypes import *
import numpy as np
import six
import signal
import cv2


#加载库文件
ll = ctypes.cdll.LoadLibrary
lib = ll("./libshmop.so")

#init
init = lib.init
init.restype = c_bool
print(init(0, 1));#这儿要修改,摄像头的ID和线程的ID

get_data_size  = lib.get_data_size
get_data_size.restype = c_int

get_data  = lib.get_data
get_data.restype = c_int

send_data = lib.send_data
send_data.restype = c_int

stop = lib.stop

def sigint_handler(signum, frame):
    stop()
signal.signal(signal.SIGINT, sigint_handler)

while True:
    data_size = get_data_size()
    if 0 == data_size:
        continue

    data = '0'*data_size
    description = get_data(data)
    if 0 == description:
        #数据在data中,你的操作

        val = 2;
        send_data(six.int2byte(val), len(six.int2byte(val)), None)
    elif 1 == description:
        str_encode = ''
        npdata = np.fromstring(data, np.uint8)
        try:
            img_decode = cv2.imdecode(npdata, cv2.IMREAD_COLOR)
        except exceptions:
            print(exceptions)
        else:
            #你的操作
            cv2.putText(img_decode, 'yangna python test', (100, 100), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 255), 2)
            #cv2.imshow("img_decode", img_decode)
            #cv2.waitKey(0)
            img_encode = cv2.imencode('.jpg', img_decode)[1]
            data_encode = np.array(img_encode)
            str_encode = data_encode.tostring()
        finally:
            if str_encode:
                send_data(str_encode, len(data_encode), six.int2byte(1))
            else:
                send_data(None, 0, None)
