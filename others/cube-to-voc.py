#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 14:30:14 2019

@author: yangna
"""

import os
import shutil
import glob
import random

total_str = '''<annotation>
    <folder>natasha</folder>
    <filename>{}.jpg</filename>
    <path>{}.jpg</path>
    <source>
        <database>Unknown</database>
    </source>
    <size>
        <width>{}</width>
        <height>{}</height>
    </size>
    <segmented>0</segmented>{}
</annotation>'''
object_str = '''
    <object>
        <name>{}</name>
        <pose>Unspecified</pose>
        <truncated>1</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>{}</xmin><ymin>{}</ymin><xmax>{}</xmax><ymax>{}</ymax>
        </bndbox>
    </object>'''

allfiles = []
def generate_voc(path):
    files = glob.iglob(os.path.join(path, '*.txt'))
    for filepath in files:
        basename = os.path.splitext(os.path.basename(filepath))[0]
        allfiles.append(basename)
        with open(filepath, 'r') as fd:
            contents = fd.readlines()
        weigth = int(contents[1].split('\r\n')[0].split(',')[0])
        height = int(contents[1].split('\r\n')[0].split(',')[1])
        all_object_str = ''
        for content in contents[2:]:
            content = content.split(',')
            try:
                c_range = map(lambda x: int(x), [content[2], content[8], content[3], content[9]])
            except IndexError:
                print(filepath, content)
                continue
            x_min = min(c_range[:2])
            x_max = max(c_range[:2])
            y_min = min(c_range[2:])
            y_max = max(c_range[2:])
            if (0 == x_max - x_min) or (0 == y_max - y_min):
                print(filepath, content)
                continue
            all_object_str += object_str.format(content[1], str(x_min), str(y_min), str(x_max), str(y_max))
        with open(os.path.join(Annotations, '{}.xml'.format(basename)), 'w') as fd:
            fd.write(total_str.format(basename, basename, weigth, height, all_object_str))
        sourceDir = os.path.join(path, '{}.jpg'.format(basename))
        targetDir = os.path.join(JPEGImages, '{}.jpg'.format(basename))
        shutil.copy(sourceDir, targetDir)

def del_file(path):
    files = os.listdir(path)
    for filename in files:
        c_path = os.path.join(path, filename)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)
    shutil.rmtree(path, True)

rootpath = '/home/yangna/part'
Annotations = os.path.join(rootpath, 'Annotations')
JPEGImages = os.path.join(rootpath, 'JPEGImages')
Main = os.path.join(rootpath, 'Main')

def remove():
    if os.path.exists(Annotations):
        del_file(Annotations)
    if os.path.exists(JPEGImages):
        del_file(JPEGImages)
    if os.path.exists(Main):
        del_file(Main)

def create():
    os.makedirs(Annotations)
    os.makedirs(JPEGImages)
    os.makedirs(Main)

if __name__ == '__main__':
    remove()
    create()

    for files in os.listdir(rootpath):
        if os.path.isdir(os.path.join(rootpath, files)):
            generate_voc(os.path.join(rootpath, files))
    
    random.shuffle(allfiles)
    train_txt = os.path.join(Main, 'train.txt')
    test_txt = os.path.join(Main, 'val.txt')
    f_len = int(len(allfiles)*0.8)
    with open(train_txt, 'w') as fd:
        fd.write('\n'.join(allfiles[:f_len]))
    with open(test_txt, 'w') as fd:
        fd.write('\n'.join(allfiles[f_len:]))