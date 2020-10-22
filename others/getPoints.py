#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 16:07:52 2019

@author: yangna
"""

import cv2
import numpy as np
import os
import glob

class FILE_OP:
    def __init__(self, rootPath='/home/yangna/12345', savePath='/home/yangna/12345/save', new_name=False):
        self.Records = []
        self.types = ['.jpg', '.png', '.bmp']
        self.setDir(rootPath)
        self.savePath = savePath
        self.new_name = new_name
        if not os.path.exists(savePath):
            os.makedirs(savePath)
    
    def getFrame(self):
        self.fileindex += 1
        if self.fileindex == len(self.filelists):
            self.imgname = ''
            return ;
        filepath = self.filelists[self.fileindex]
        self.img = cv2.imread(filepath)
        self.imgname = os.path.basename(filepath)
    
    def setDir(self, dir_path):
        self.dir_path = dir_path
        self.filelists = []
        if self.types:
            for fType in self.types:
                self.filelists += glob.glob(os.path.join(dir_path, '*'+fType))
        else:
            self.filelists += glob.glob(os.path.join(dir_path, '*'))
        self.fileindex = -1
        self.getFrame()

    def setTypes(self, types, method=1):
        if 0 == method:
            self.types = []
            if isinstance(types, list):
                self.types = types
            elif isinstance(types, str):
                self.types = [types]
        elif 1 == method:
            if isinstance(types, list):
                self.types.extend(types)
            elif isinstance(types, str):
                self.types.append(types)
    
    def renames(self):
        length = len(self.filelists)
        if length < 1000000:
            for index, filepath in enumerate(self.filelists):
                self.img = cv2.imread(filepath)
                cv2.imwrite(os.path.join(self.savePath, '%06d.jpg' % index), self.img)
        elif length < 1000000000:
            for index, filepath in enumerate(self.filelists):
                self.img = cv2.imread(filepath)
                cv2.imwrite(os.path.join(self.savePath, '%09d.jpg' % index), self.img)
        
    def addMouseEvent(self, function):
        cv2.namedWindow('image', cv2.WINDOW_FREERATIO)
        #cv2.resizeWindow("image", 1920, 1080);
        cv2.setMouseCallback('image', function)
        cv2.imshow('image', self.img)
        while True:
            if cv2.waitKey(20)&0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
    
    def quit_op(self):
        cv2.destroyAllWindows()
    
    def clipRect(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.Records.append((x, y))
        elif event == cv2.EVENT_LBUTTONUP:
            save_frame = self.img[self.Records[0][1]:y, self.Records[0][0]:x] 
            self.Records = []
            if self.imgname and self.savePath:
                if self.new_name:
                    cv2.imwrite(os.path.join(self.savePath, '%06d.jpg' % self.fileindex), save_frame)
                else:
                    cv2.imwrite(os.path.join(self.savePath, self.imgname), save_frame)
            if not self.imgname:
                self.quit_op()
            self.getFrame()
            cv2.imshow('image', self.img)
        elif (event == cv2.EVENT_MOUSEMOVE) and (flags == cv2.EVENT_FLAG_LBUTTON):
            frame = self.img.copy()
            cv2.line(frame, (x, self.Records[0][1]), self.Records[0], (0, 0, 255), thickness=1)
            cv2.line(frame, (self.Records[0][0], y), self.Records[0], (0, 0, 255), thickness=1)
            cv2.line(frame, (x, self.Records[0][1]), (x, y), (0, 0, 255), thickness=1)
            cv2.line(frame, (self.Records[0][0], y), (x, y), (0, 0, 255), thickness=1)
            cv2.imshow('image', frame)
    
    def paintArea(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONUP:
            self.findRect()
        elif event == cv2.EVENT_RBUTTONDBLCLK:
            self.quit_op()
        elif (event == cv2.EVENT_MOUSEMOVE) and (flags == cv2.EVENT_FLAG_LBUTTON):
            cv2.circle(self.img, (x, y), 10, (255, 0, 0), thickness=-1)
            cv2.imshow('image', self.img)

    def findRect(self):
        mask = cv2.inRange(self.img, lowerb=np.array([255,0,0]), upperb=np.array([255,0,0]))
        dst = cv2.bitwise_and(self.img, self.img, mask=mask)
        diff_gray = cv2.cvtColor(dst, cv2.COLOR_RGB2GRAY)
        if cv2.__version__[-5] == '4':
            contours, _ = cv2.findContours(diff_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        else:
            _, contours, _ = cv2.findContours(diff_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cnt_area = [cv2.contourArea(cnt) for cnt in contours]
        for index,contour in enumerate(contours):
            if cnt_area[index] > 100:# and cnt_area[index] < 2000:
                polygon = contour.reshape(-1, 2)
                prbox = cv2.boxPoints(cv2.minAreaRect(polygon))
                x,y,w,h = cv2.boundingRect(contour)
                cv2.rectangle(self.img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                rbox_in_img = np.int0(prbox.flatten()).reshape((-1, 1, 2))
                cv2.polylines(self.img, [rbox_in_img], True, (255, 255, 0), 3)
        cv2.imshow('image', self.img)
    
    def choosePoints(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.Records.append((x, y))
        elif event == cv2.EVENT_LBUTTONUP:
            frame = self.img.copy()
            for index,point in enumerate(self.Records):
                cv2.circle(frame, point, 4, (0, 0, 255), thickness=4)
                if 0 <= (index - 1):
                    cv2.line(frame, self.Records[index-1], point, (0, 0, 255), thickness=2)
            if len(self.Records) > 1:
                cv2.line(frame, self.Records[-1], self.Records[0], (0, 0, 255), thickness=2)
            cv2.imshow('image', frame)
            print(self.Records)
    
m_op = FILE_OP(new_name=True)
m_op.renames()

#save pic start####################
def savePic(srcPath, count=1, skipnumber=1):
    dirname = os.path.dirname(srcPath)
    cap = cv2.VideoCapture(srcPath)
    index = 0
    indexsum = 0
    while True:
        ret,img = cap.read()
        if not ret:
            continue
        if 0 == (indexsum % skipnumber):
            filepath = os.path.join(dirname, '%d.jpg' % index)
            cv2.imwrite(filepath, img)
            index += 1
            if index == count:
                break
        indexsum += 1
    cap.release()
savePic('/home/yangna/行为AI分析/人员聚集.avi', count=2)
#choose mulit points start####################

#select roi start###################
def selectROI(srcPath):
    afterfix = os.path.splitext(srcPath)[1]
    iscap = False
    if afterfix in ['.jpg', '.png', '.bmp']:
        img = cv2.imread(srcPath)
    elif afterfix in ['.mp4', '.mkv', '.avi']:
        cap = cv2.VideoCapture(srcPath)
        iscap = True
        ret,img = cap.read()
    while(True):
        r = cv2.selectROI(img)
        print(r)    
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break
    if iscap:
        cap.release()
    cv2.destroyAllWindows()
#select roi end###################

#generateAlpha start###################
def generateAlpha(frame, b, g, r, a):
    e_frame = np.zeros_like(frame)
    b_channel, g_channel, r_channel = cv2.split(e_frame)
    b_channel[:, :] = b
    g_channel[:, :] = g
    r_channel[:, :] = r
    alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255
    alpha_channel[:, :] = a
    img_BGRA = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))
    return img_BGRA
#generateAlpha end###################