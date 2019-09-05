# -*- coding: utf-8 -*-
"""
Created on Sun Mar 18 17:55:30 2018

@author: natasha1_Yang
"""
计算机视觉
 1>语义感知
  分类
  检测
  识别
  分隔
  检索
  语言
 2>几何属性
  3D建模
  双目视觉
  增强实现
解决像素值和语义之间的GAP
图像数据处理
 1>空域分析及变换
  Sobel,拉普拉斯,高斯,中值
 2>频域分析及变换
  FFT,小波
 3>模板匹配,金字塔,filter
 4>特征数据操作
  PCA,SVD,Cluster
图像特征及描述
 1>颜色特征
  RGB,HSV,Lab,直方图
 2>几何特征
  Edge,Corner,Blob
 3>纹理特征
  HOG,LBP,Gabor
 4>局部特征
  SIFT,SURF,FAST
CNN:AlexNet->VGG->GoogleNet->ResNet->ResNeXt
R-CNN:R-CNN->SPP-Net->Fast/Faster R-CNN->YOLO->SSD->R-FCN(智能监控,辅助驾驶)
FCN->SegNet/DeconvNet->DeepLab(全卷积神经网络)
RNN递归神经网络,循环神经网络->Vanilla RNN->LSTM->GRU(文本/区域/视频序列)
GAN生成对抗网络
 生成器网络
 判别器网络
 无监督:GAN->DCGAN->wGAN
 有监督:SRGAN->SalGAN->RLA
RGB=>3通道(B,G,R),加法混色
CMY(K)=>四通道(c,m,y,k),减法混色
HSV/HSL(I)=>3通道,色调,饱和度,明度/亮度
CLE-XYZ颜色空间,CLE-Lab对色空间(非线性3通道)
单通道灰度图:R*0.3+G*0.59+B*0.11
均值平滑/中值平滑(有效去除椒盐噪声)/高斯平滑(模拟人眼,关注中心区域,级联高斯)
 级联高斯[[1, 2, 1], [2, 4, 2], [1, 2, 1]] ==> [1, 2, 1].T * [1, 2, 1]==>降低计算次数
 Prewitt梯度滤波:[[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]] = [-1, 0, 1](水平梯度) * [1, 1, 1].T(均值平滑)
                [[-1, -1, -1], [0, 0, 0], [1, 1, 1]] = [1, 1, 1](均值平滑) * [-1, 0, 1].T(垂直梯度)
 Sobel梯度:[-1, 0, 1] * [1, 2, 1](高斯平滑) + [1, 2, 1] * [-1, 0, 1].T
 Laplacian梯度:团块检测/边缘检测
边缘提取:先高斯去噪声(对噪声敏感),在使用一阶导数获取极值

