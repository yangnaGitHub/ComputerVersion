#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 15:05:26 2019

@author: yangna
"""

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
    {}
    <segmented>0</segmented>
    {}
</annotation>'''

allfiles = []
def generate_voc(path):
    files = glob.iglob(os.path.join(path, '*.jpg'))
    for index,filepath in enumerate(files):
        #oldbasename = os.path.splitext(os.path.basename(filepath))[0]
        #xmlfilepath = os.path.join(path, oldbasename+'.xml')
        basename = os.path.splitext(os.path.basename(filepath))[0]
        xmlfilepath = os.path.join(path, basename+'.xml')
        if not os.path.exists(xmlfilepath):
            continue
#        basename = '2%06d' % index
#        os.rename(filepath, os.path.join(path, basename+'.jpg'))
        
        with open(xmlfilepath, 'r') as fd:
            contents = ''.join(fd.readlines())
        size_str = ''
        all_object_str = ''
        if (-1 != contents.find('<size>')) and (-1 != contents.find('</size>')):
            size_str = contents[contents.find('<size>'):contents.find('</size>')+7]
        if (-1 != contents.find('<object>')) and (-1 != contents.rfind('</object>')):
            all_object_str = contents[contents.find('<object>'):contents.rfind('</object>')+9]
        if size_str and all_object_str:    
            with open(os.path.join(Annotations, '{}.xml'.format(basename)), 'w') as fd:
                fd.write(total_str.format(basename, basename, size_str, all_object_str))
            sourceDir = os.path.join(path, '{}.jpg'.format(basename))
            targetDir = os.path.join(JPEGImages, '{}.jpg'.format(basename))
            shutil.copy(sourceDir, targetDir)
            allfiles.append(basename)

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
    
    generate_voc(rootpath)
    
    
    files = glob.glob('/home/yangna/yangna/code/object_detection/darknet_origin/scripts/VOCdevkit/VOC2013/Annotations/*.xml')
    allfiles = [os.path.splitext(os.path.basename(filename))[0] for filename in files]
    
    random.shuffle(allfiles)
    train_txt = os.path.join(Main, 'train.txt')
    test_txt = os.path.join(Main, 'val.txt')
    f_len = int(len(allfiles)*0.8)
    with open(train_txt, 'w') as fd:
        fd.write('\n'.join(allfiles[:f_len]))
    with open(test_txt, 'w') as fd:
        fd.write('\n'.join(allfiles[f_len:]))