#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 16:07:52 2019

@author: yangna
"""

import cv2
import numpy as np

srcPath = '/home/yangna/yangna/project/mclz/video_bk/pic/yangna_1.jpg'
img = cv2.imread(srcPath)

pts1 = np.float32([[0,0],[0,12],[376,20],[376,32]])
pts2 = np.float32([[0,0],[0,12],[376,0],[376,12]])

M = cv2.getPerspectiveTransform(pts1, pts2)
dst = cv2.warpPerspective(img[224:256, 802:1178], M, (376,32))
cv2.imshow('ori_img', img[224:256, 802:1178])
cv2.imshow('dst_img', dst[:12, :])
cv2.waitKey(0)
cv2.destroyAllWindows()

srcPath = '/home/yangna/yangna/code/object_detection/darknet_origin/temp.jpg'
img = cv2.imread(srcPath)

pts1 = np.float32([[0,0],[300,488],[587,0],[586,483]])
pts2 = np.float32([[0,450],[587,450],[0,0],[587,0]])

M = cv2.getPerspectiveTransform(pts1, pts2)
dst = cv2.warpPerspective(img[234:727, 1267:1854], M, (587,493))
cv2.imshow('ori_img', img[234:727, 1267:1854])
cv2.imshow('dst_img', dst)
cv2.waitKey(0)
cv2.destroyAllWindows()

import math
def rotate_about_center(src, angle, scale=1.):
    w = src.shape[1]
    h = src.shape[0]
    rangle = np.deg2rad(angle)  # angle in radians
    # now calculate new image width and height
    nw = (abs(np.sin(rangle)*h) + abs(np.cos(rangle)*w))*scale
    nh = (abs(np.cos(rangle)*h) + abs(np.sin(rangle)*w))*scale
    # ask OpenCV for the rotation matrix
    rot_mat = cv2.getRotationMatrix2D((nw*0.5, nh*0.5), angle, scale)
    # calculate the move from the old center to the new center combined
    # with the rotation
    rot_move = np.dot(rot_mat, np.array([(nw-w)*0.5, (nh-h)*0.5,0]))
    # the move only affects the translation, so update the translation
    # part of the transform
    rot_mat[0,2] += rot_move[0]
    rot_mat[1,2] += rot_move[1]
    return cv2.warpAffine(src, rot_mat, (int(math.ceil(nw)), int(math.ceil(nh))), flags=cv2.INTER_LANCZOS4)

c_img = rotate_about_center(img, 90)
cv2.imshow('c_img', c_img)
cv2.waitKey(0)
cv2.destroyAllWindows()



