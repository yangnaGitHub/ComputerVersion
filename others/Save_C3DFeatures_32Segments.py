#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 13:37:12 2019

@author: yangna
"""

import numpy as np
import os
import glob
import struct

s_float = struct.calcsize('f')
s_int32 = struct.calcsize('i')

inpath = '/home/yangna/yangna/code/useful_methods/C3D/C3D-v1.0/examples/c3d_feature_extraction/output'
outpath = '/home/yangna/yangna/code/useful_methods/C3D/C3D-v1.0/examples/c3d_feature_extraction/output/convert'

if not os.path.exists(outpath):
    os.makedirs(outpath)

segmentcount = 32
for filename in os.listdir(inpath):
    filespath = os.path.join(inpath, filename)
    if os.path.isdir(filespath):
        files = glob.glob(os.path.join(filespath, '*.fc6-1'))
        files.sort()
        lenfiles = len(files)
        if lenfiles:
            features = np.zeros((lenfiles, 4096), dtype='float32')
            for f_index,featurename in enumerate(files):
                fd = open(featurename, 'rb')
                s_str = fd.read(s_int32*5)
                num,chanel,length,height,width = struct.unpack('iiiii', s_str)
                total = num*chanel*length*height*width
                data_str = fd.read(s_float*total)
                for index in range(total):
                    features[f_index][index] = struct.unpack('f', data_str[index*s_float:(index+1)*s_float])[0]
                fd.close()
            
            segments = np.zeros((segmentcount, 4096))
            repeatlist = [round(index) for index in np.linspace(0,lenfiles-1,segmentcount+1)]
            for s_num in range(segmentcount):
                ss = int(repeatlist[s_num])
                ee = int(repeatlist[s_num+1]-1)
                if ss >= ee:
                    temp = features[ss, :]
                else:
                    temp = np.mean(features[ss:ee+1, :], axis=0)
                temp = temp/np.sqrt(np.sum(temp**2))
                temp = [round(index, 6) for index in temp]
                segments[s_num] = temp
            
            outputfile = os.path.join(outpath, filename+'_C.txt')    
            with open(outputfile, 'w') as fd:
                for values in segments:
                    [fd.write('%06f '%value) for value in values]
                    fd.write('\n')