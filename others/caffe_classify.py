#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 11:29:04 2019

@author: yangna
"""

import os
import re
import cv2
import glob
import shutil
import numpy as np
from sklearn.model_selection import train_test_split
import random
import Augmentor

rootpath = '/home/yangna/yangna/project/grocery/data/body'
datamap = {'other':0,
           'cleaner':1,
           'detecter':2,
           'manager':3,
           'apron':4}
SORT_DATA = False

def prepare_data(dirpath, prefix):
    for dirname,dirnames,files in os.walk(dirpath):
#        for refile in files:
#            srcfile = os.path.join(dirpath, refile)
#            renamefile = os.path.join(dirpath, '%02d'%(prefix)+refile[2:])
#            if srcfile != renamefile:    
#                image = cv2.imread(srcfile)
#                cv2.imwrite(renamefile, image)
#                os.remove(srcfile)
        length = len(files)
        print(prefix, length)
        re_files = []
        for refile in files:
            if SORT_DATA:
                re_find = re.findall('\d{10}.jpg', refile)
                if re_find:
                    pass
                else:
                    re_files.append(refile)
            else:
                re_find = re.findall('original', refile)
                if re_find:
                    re_files.append(refile)
                else:
                    pass
        
        if re_files:
            startname = length - len(re_files)
            for index,refile in enumerate(re_files):
                srcfile = os.path.join(dirpath, refile)
                renamefile = os.path.join(dirpath, '%02d%08d.jpg'%(prefix, startname+index))
                os.rename(srcfile, renamefile)
                #image = cv2.imread(srcfile)
                #cv2.imwrite(renamefile, image)
                #os.remove(srcfile)

def copyfile(src, des, filename=''):
    if not os.path.exists(des):
        os.makedirs(des)
    if filename:
        srcfile = os.path.join(src, filename)
        if not os.path.isfile(srcfile):
            print('{} is not file'.format(srcfile))
            return
        else:
            shutil.copyfile(srcfile, os.path.join(des, filename))
    else:
        for dirname,dirnames,files in os.walk(dirpath):
            for removefile in files:
                shutil.copyfile(os.path.join(src, removefile), os.path.join(des, removefile))

#augment_data->prepare_data->prepare_datas->generate_file->generate_data_file
#resize_pic->generate_train_test->generate_lmdb->generate_mean

processing = 'prepare_data'
datafilepath = os.path.join(rootpath, 'data.txt')
trainfilepath = os.path.join(rootpath, 'train.txt')
testfilepath = os.path.join(rootpath, 'test.txt')
datarfilepath = os.path.join(rootpath, 'datar.txt')
dataspath = os.path.join(rootpath, 'datas')
datarpath = os.path.join(rootpath, 'datar')
trainpath = os.path.join(rootpath, 'train')
testpath = os.path.join(rootpath, 'test')
caffepath = '/home/yangna/下载/caffe'
caffebuildpath = os.path.join(caffepath, 'build/tools')
trainlmdbpath = os.path.join(rootpath, 'train_lmdb')
testlmdbpath = os.path.join(rootpath, 'test_lmdb')
datalmdbpath = os.path.join(rootpath, 'data_lmdb')
trainmeanpath = os.path.join(rootpath, 'train.binaryproto')
testmeanpath = os.path.join(rootpath, 'test.binaryproto')
datameanpath = os.path.join(rootpath, 'data.binaryproto')
datasets = None

data_count = 2500
if processing in ["augment_data", "prepare_data", "prepare_datas", "generate_file", "generate_data_file"]:
    for key,val in datamap.items():
        dirpath = os.path.join(rootpath, key)
        if 'augment_data' == processing:
            print(dirpath)
            temp = Augmentor.Pipeline(dirpath, output_directory=dirpath+'AUG')
            temp.flip_left_right(0.4)
            temp.random_brightness(1, 0.78, 1.45)
            temp.sample(data_count)
        elif 'prepare_data' == processing:#1
            if not SORT_DATA:
                dirpath += 'AUG'
            prepare_data(dirpath, val)
        elif 'prepare_datas' == processing:#2
            dirpath += 'AUG'
            copyfile(dirpath, dataspath)
        elif 'generate_file' == processing:#3
            dirpath += 'AUG'
            filepath = os.path.join(rootpath, key+'.txt')
            files = glob.glob(dirpath+'/*.jpg')
            random.shuffle(files)
            lenfiles = len(files)
            #recursive = data_count if data_count > lenfiles else len(files)
            with open(filepath, 'w') as fd:
                for filename in files:
                    fd.write(filename[filename.rfind('/')+1:] + ' ' + str(val)+'\n')
                #for index in range(recursive):
                    #tempindex = index%lenfiles
                    #if 0 == tempindex:    
                        #random.shuffle(files)
                    #filename = files[tempindex]
                    #fd.write(filename[filename.rfind('/')+1:] + ' ' + str(val)+'\n')
        elif 'generate_data_file' == processing:#4
            filepath = os.path.join(rootpath, key+'.txt')
            with open(datafilepath, 'a') as fd:
                with open(filepath, 'r') as fd_s:
                    [fd.write(lines) for lines in fd_s.readlines()]
            
if 'resize_pic' == processing:#6
    if not os.path.exists(datarpath):
        os.makedirs(datarpath)
    for dirname,dirnames,files in os.walk(dataspath):
        for filename in files:
            srcfilename = os.path.join(dataspath, filename)
            image = cv2.imread(srcfilename)
            image = cv2.resize(image, (256, 256), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(os.path.join(datarpath, filename), image)

elif 'generate_train_test' == processing:#5
    with open(datafilepath, 'r') as fd:
        contents = fd.readlines()
        random.shuffle(contents)
        datasets = np.array([lines.split(' ') for lines in contents])    
    if datasets is not None:
        trainx,testx,trainy,testy = train_test_split(datasets[:, 0], datasets[:, 1], test_size=0.3)
        with open(datarfilepath, 'w') as fd:
            [fd.write('datar/{} {}'.format(name, label)) for name,label in zip(trainx, trainy)]
            [fd.write('datar/{} {}'.format(name, label)) for name,label in zip(testx, testy)]
        with open(trainfilepath, 'w') as fd:
            [fd.write('train/{} {}'.format(name, label)) for name,label in zip(trainx, trainy)]
        with open(testfilepath, 'w') as fd:
            [fd.write('test/{} {}'.format(name, label)) for name,label in zip(testx, testy)]
        [copyfile(datarpath, trainpath, name) for name in trainx]
        [copyfile(datarpath, testpath, name) for name in testx]
elif 'generate_lmdb' == processing:#7
    os.system(os.path.join(caffebuildpath, 'convert_imageset') + ' --shuffle --resize_height=256 --resize_width=256 ' + rootpath + '/ ' + trainfilepath + ' ' + trainlmdbpath)
    os.system(os.path.join(caffebuildpath, 'convert_imageset') + ' -shuffle --resize_height=256 --resize_width=256 ' + rootpath + '/ ' + testfilepath + ' ' + testlmdbpath)
    os.system(os.path.join(caffebuildpath, 'convert_imageset') + ' -shuffle --resize_height=256 --resize_width=256 ' + rootpath + '/ ' + datarfilepath + ' ' + datalmdbpath)
elif 'generate_mean' == processing:#8
    os.system(os.path.join(caffebuildpath, 'compute_image_mean') + ' ' + trainlmdbpath + ' ' + trainmeanpath)
    os.system(os.path.join(caffebuildpath, 'compute_image_mean') + ' ' + testlmdbpath + ' ' + testmeanpath)
    os.system(os.path.join(caffebuildpath, 'compute_image_mean') + ' ' + datalmdbpath + ' ' + datameanpath)