#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 17:08:32 2019

@author: yangna
"""

import cv2
import numpy as np
import math

img_p = cv2.imread('/home/yangna/yangna/project/mclz/video_bk/yangna.jpg')
img_c = cv2.imread('/home/yangna/yangna/project/mclz/video_bk/yangna_1.jpg')
img_p_hsl = cv2.cvtColor(img_p, cv2.COLOR_BGR2YCrCb)#COLOR_BGR2HLS,COLOR_BGR2HSV,COLOR_BGR2YCrCb
img_c_hsl = cv2.cvtColor(img_c, cv2.COLOR_BGR2YCrCb)
norm(img_p_hsl)
norm(img_c_hsl)
img_p = cv2.cvtColor(img_p_hsl, cv2.COLOR_YCrCb2BGR)#COLOR_HLS2BGR,COLOR_HSV2BGR,COLOR_YCrCb2BGR
img_c = cv2.cvtColor(img_c_hsl, cv2.COLOR_YCrCb2BGR)
cv2.imshow('img_c_o', img_c)
cv2.imshow('img_p_o', img_p)
cv2.waitKey(0)
cv2.destroyAllWindows()

diff = cv2.absdiff(cv2.imread('/home/yangna/yangna/project/mclz/video_bk/yangna_a.jpg'), cv2.imread('/home/yangna/yangna/project/mclz/video_bk/yangna_3_a.jpg'))
cv2.imshow('diff', diff)
cv2.waitKey(0)
cv2.destroyAllWindows()

hidden(img_c, img_p)

def norm(frame):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    frame[:, :, 0] = clahe.apply(frame[:, :, 0])
    #frame[:, :, 1] = clahe.apply(frame[:, :, 1])
    #frame[:, :, 2] = clahe.apply(frame[:, :, 2])

def hidden(img_c, img_p):
    pts = np.array([[626, 59], [594, 143], [436, 146], [177, 451], [0, 432], [0, 719], [1279, 719], [1279, 322], [808, 315], [722, 64]], np.int32)
    pts = pts.reshape((-1,1,2))
    img_c_hsv = cv2.cvtColor(img_c, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 0, 70])
    upper_red = np.array([180, 30, 95])
    mask = ~cv2.inRange(img_c_hsv, lower_red, upper_red)
    img_c = cv2.bitwise_and(img_c, img_c, mask = mask)
    img_p = cv2.bitwise_and(img_p, img_p, mask = mask)
    mask = cv2.fillPoly(img_p.copy(), [pts], (255, 255, 255))
    mask = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)
    ret, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
    diff = cv2.absdiff(img_p, img_c)
    diff = cv2.bitwise_and(diff, diff, mask = mask)
    cv2.imshow('diff', diff)
    diff_gray = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
    cv2.imshow('diff_gray', diff_gray)
    ret,thresh = cv2.threshold(diff_gray, 60, 255, 0)
    cv2.imshow('thresh', thresh)
    if cv2.__version__[-5] == '4':
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    else:
        _, contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnt_area = [cv2.contourArea(cnt) for cnt in contours]
    
    for index,contour in enumerate(contours):
        if cnt_area[index] > 100:# and cnt_area[index] < 2000:
            polygon = contour.reshape(-1, 2)
            prbox = cv2.boxPoints(cv2.minAreaRect(polygon))
            x,y,w,h = cv2.boundingRect(contour)
            rbox_in_img = np.int0(prbox.flatten()).reshape((-1, 1, 2))
            ratio = math.sqrt((rbox_in_img[0][0][0]-rbox_in_img[1][0][0])**2+(rbox_in_img[0][0][1]-rbox_in_img[1][0][1])**2)
            ratio = ratio/math.sqrt((rbox_in_img[1][0][0]-rbox_in_img[2][0][0])**2+(rbox_in_img[1][0][1]-rbox_in_img[2][0][1])**2)
            if (ratio < 0.2) or (ratio > 5):
                continue
            cv2.rectangle(diff, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.polylines(diff, [rbox_in_img], True, (255, 255, 0), 3)
    
    cv2.imshow('diff_m', diff)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def unevenLightCompensate(gray, blockSize):
    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    average = np.mean(gray)

    rows_new = int(np.ceil(gray.shape[0] / blockSize))
    cols_new = int(np.ceil(gray.shape[1] / blockSize))

    blockImage = np.zeros((rows_new, cols_new), dtype=np.float32)
    for r in range(rows_new):
        for c in range(cols_new):
            rowmin = r * blockSize
            rowmax = (r + 1) * blockSize
            if (rowmax > gray.shape[0]):
                rowmax = gray.shape[0]
            colmin = c * blockSize
            colmax = (c + 1) * blockSize
            if (colmax > gray.shape[1]):
                colmax = gray.shape[1]

            imageROI = gray[rowmin:rowmax, colmin:colmax]
            temaver = np.mean(imageROI)
            blockImage[r, c] = temaver

    blockImage = blockImage - average
    blockImage2 = cv2.resize(blockImage, (gray.shape[1], gray.shape[0]), interpolation=cv2.INTER_CUBIC)
    gray2 = gray.astype(np.float32)
    dst = gray2 - blockImage2
    dst = dst.astype(np.uint8)
    dst = cv2.GaussianBlur(dst, (3, 3), 0)
    #dst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)

    return dst

def allLC(img):
    blockSize = 16
    dst = np.zeros_like(img)
    print(dst.shape)
    img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    #dst[:, :, 0] = unevenLightCompensate(img_hsv[:, :, 0], blockSize)
    #dst[:, :, 1] = unevenLightCompensate(img_hsv[:, :, 1], blockSize)
    dst[:, :, 0] = img_hsv[:, :, 0]
    dst[:, :, 1] = img_hsv[:, :, 1]
    dst[:, :, 2] = unevenLightCompensate(img_hsv[:, :, 2], blockSize)
    
    return cv2.cvtColor(dst, cv2.COLOR_HSV2BGR)

if __name__ == '__main__':
    files = '/home/yangna/yangna/project/mclz/video_bk/yangna_3.jpg'
    blockSize = 16
    img = cv2.imread(files)
    dst = np.zeros_like(img)
    print(dst.shape)
    dst[:, :, 0] = unevenLightCompensate(img[:, :, 0], blockSize)
    dst[:, :, 1] = unevenLightCompensate(img[:, :, 1], blockSize)
    dst[:, :, 2] = unevenLightCompensate(img[:, :, 2], blockSize)

    result = np.concatenate([img, dst], axis=1)

    cv2.imshow('result', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

##########################
def uniform_pattern_LBP(img, radius=3, neighbors=8):
    h,w=img.shape
    dst = np.zeros((h-2*radius, w-2*radius),dtype=img.dtype)
    # LBP特征值对应图像灰度编码表，直接默认采样点为8位
    temp = 1
    table =np.zeros((256),dtype=img.dtype)
    for i in range(256):
        if getHopTimes(i)<3:
            table[i] = temp
            temp+=1
    # 是否进行UniformPattern编码的标志
    flag = False
    # 计算LBP特征图
    for k in range(neighbors):
        if k==neighbors-1:
            flag = True
      
        # 计算采样点对于中心点坐标的偏移量rx，ry
        rx = radius * np.cos(2.0 * np.pi * k / neighbors)
        ry = -(radius * np.sin(2.0 * np.pi * k / neighbors))
        # 为双线性插值做准备
        # 对采样点偏移量分别进行上下取整
        x1 = int(np.floor(rx))
        x2 = int(np.ceil(rx))
        y1 = int(np.floor(ry))
        y2 = int(np.ceil(ry))
        # 将坐标偏移量映射到0-1之间
        tx = rx - x1
        ty = ry - y1
        # 根据0-1之间的x，y的权重计算公式计算权重，权重与坐标具体位置无关，与坐标间的差值有关
        w1 = (1-tx) * (1-ty)
        w2 =    tx  * (1-ty)
        w3 = (1-tx) *    ty
        w4 =    tx  *    ty
        # 循环处理每个像素
        for i in range(radius,h-radius):
            for j in range(radius,w-radius):
                # 获得中心像素点的灰度值
                center = img[i,j]
                # 根据双线性插值公式计算第k个采样点的灰度值
                neighbor = img[i+y1,j+x1] * w1 + img[i+y2,j+x1] *w2 + img[i+y1,j+x2] *  w3 +img[i+y2,j+x2] *w4
                # LBP特征图像的每个邻居的LBP值累加，累加通过与操作完成，对应的LBP值通过移位取得
                dst[i-radius,j-radius] |= (neighbor>center)  <<  (np.uint8)(neighbors-k-1)
                # 进行LBP特征的UniformPattern编码
                if flag:
                    dst[i-radius,j-radius] = table[dst[i-radius,j-radius]]
    return dst
             
def getHopTimes(data):
    '''
    计算跳变次数
    '''
    count = 0;
    binaryCode = "{0:0>8b}".format(data)
     
    for i in range(1,len(binaryCode)):
        if binaryCode[i] != binaryCode[(i-1)]:
            count+=1
    return count

def getLBPH(img_lbp,numPatterns,grid_x,grid_y,normed):
    '''
    计算LBP特征图像的直方图LBPH
    '''
    h,w=img_lbp.shape
    width = int(w / grid_x)
    height = int(h / grid_y)
    # 定义LBPH的行和列，grid_x*grid_y表示将图像分割的块数，numPatterns表示LBP值的模式种类
    result = np.zeros((grid_x * grid_y,numPatterns),dtype=float)
    resultRowIndex = 0
    # 对图像进行分割，分割成grid_x*grid_y块，grid_x，grid_y默认为8
    for i in range(grid_x):
        for j in range(grid_y):
            # 图像分块
            src_cell = img_lbp[i*height:(i+1)*height,j*width:(j+1)*width]
            # 计算直方图
            hist_cell = getLocalRegionLBPH(src_cell,0,(numPatterns-1),True)
            #将直方图放到result中
            result[resultRowIndex]=hist_cell
            resultRowIndex+=1
    return np.reshape(result,(-1))

def getLocalRegionLBPH(src,minValue,maxValue,normed):
    '''
    计算一个LBP特征图像块的直方图
    '''
    data = np.reshape(src,(-1))
    # 计算得到直方图bin的数目，直方图数组的大小
    bins = maxValue - minValue + 1;
    # 定义直方图每一维的bin的变化范围
    ranges = (float(minValue),float(maxValue + 1))
    hist, bin_edges = np.histogram(src, bins=bins, range=ranges, normed=normed)
    return hist

gray = cv2.imread('/home/yangna/yangna/project/mclz/video_bk/yangna.jpg', cv2.IMREAD_GRAYSCALE)[350:, :]
gray_1 = cv2.imread('/home/yangna/yangna/project/mclz/video_bk/yangna_1.jpg', cv2.IMREAD_GRAYSCALE)[350:, :]
gray_2 = cv2.imread('/home/yangna/yangna/project/mclz/video_bk/yangna_2.jpg', cv2.IMREAD_GRAYSCALE)[350:, :]
gray_3 = cv2.imread('/home/yangna/yangna/project/mclz/video_bk/yangna_3.jpg', cv2.IMREAD_GRAYSCALE)[350:, :]
uniform_pattern = uniform_pattern_LBP(gray,3,8)
uniform_pattern_1 = uniform_pattern_LBP(gray_1,3,8)
uniform_pattern_2 = uniform_pattern_LBP(gray_2,3,8)
uniform_pattern_3 = uniform_pattern_LBP(gray_3,3,8)
cv2.imwrite('/home/yangna/yangna/project/mclz/video_bk/yangna_a.jpg', uniform_pattern)
cv2.imwrite('/home/yangna/yangna/project/mclz/video_bk/yangna_1_a.jpg', uniform_pattern_1)
cv2.imwrite('/home/yangna/yangna/project/mclz/video_bk/yangna_2_a.jpg', uniform_pattern_2)
cv2.imwrite('/home/yangna/yangna/project/mclz/video_bk/yangna_3_a.jpg', uniform_pattern_3)
lbph = getLBPH(uniform_pattern,59,8,8,True)
lbph_1 = getLBPH(uniform_pattern_1,59,8,8,True)
lbph_2 = getLBPH(uniform_pattern_2,59,8,8,True)
lbph_3 = getLBPH(uniform_pattern_3,59,8,8,True)
print(sum(abs(lbph-lbph_1)))
print(sum(abs(lbph_1-lbph_2)))
print(sum(abs(lbph-lbph_3)))
cv2.waitKey(0)
cv2.destroyAllWindows()

##########################
result = cv2.matchTemplate(cv2.imread('/home/yangna/yangna/project/mclz/video_bk/yangna.jpg')[480:, :], cv2.imread('/home/yangna/yangna/project/mclz/video_bk/yangna_3.jpg')[480:, :], cv2.TM_SQDIFF_NORMED)
result = cv2.matchTemplate(cv2.imread('/home/yangna/yangna/project/mclz/video_bk/yangna.jpg')[480:, :], cv2.imread('/home/yangna/yangna/project/mclz/video_bk/yangna_1.jpg')[480:, :], cv2.TM_SQDIFF_NORMED)
result = cv2.matchTemplate(cv2.imread('/home/yangna/yangna/project/mclz/video_bk/yangna_1.jpg')[480:, :], cv2.imread('/home/yangna/yangna/project/mclz/video_bk/yangna_2.jpg')[480:, :], cv2.TM_SQDIFF_NORMED)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
print(min_val)