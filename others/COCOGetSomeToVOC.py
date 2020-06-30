# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 11:10:09 2019

@author: yangna

@mail:ityangna0402@163.com

"""

import os
import json
import shutil

path = 'D:\\work_study\\data\\compress\\coco\\'
year = '2014'
process = 'train'
class_name = []
class_id = []
annotations = os.path.join(path, 'annotations_trainval'+year, 'annotations')

def get_annotations(filename):
    ob_d = os.path.join(annotations, filename)#instances_train2014.json instances_val2014.json
    with open(ob_d, 'r') as fd:
        data = json.load(fd)
    return data

def print_info(data):
    data.keys()
    print(type(data['info']))
    print(type(data['images']))#40504
    print(type(data['licenses']))
    print(type(data['annotations']))#291875
    print(type(data['categories']))#80

def construct_data(data):
    image_d = {}
    for image in data['images']:
        if image['id'] not in image_d:
            image_d[image['id']] = [image['file_name'], image['height'], image['width']]
        else:
            print(image['id'])

    categorie_d = {}
    for categorie in data['categories']:
        if categorie['id'] not in categorie_d:
            categorie_d[categorie['id']] = [categorie['name'], categorie['supercategory']]
        else:
            print(categorie['id'])
        
    annotation_d = {}
    for annotation in data['annotations']:
        if annotation['id'] not in annotation_d:
            annotation_d[annotation['id']] = image_d[annotation['image_id']] + [annotation['bbox'], annotation['category_id']]
        else:
            print(annotation['id'])
    return categorie_d, annotation_d

string_1 = '''<annotation>
    <folder>natasha</folder>
    <filename>{}</filename>
    <path>{}</path>
    <source>
        <database>Unknown</database>
    </source>
    <size>
        <width>{}</width>
        <height>{}</height>
    </size>
    <segmented>0</segmented>'''

string_2 = '''
    <object>
        <name>{}</name>
        <pose>Unspecified</pose>
        <truncated>1</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>{}</xmin><ymin>{}</ymin><xmax>{}</xmax><ymax>{}</ymax>
        </bndbox>
    </object>'''

def get_by_ids(annotation_d, class_ids, categorie_d, key_p = 'train'):
    filelist = []
    saveDict = {}
    for key,value in annotation_d.items():
        if value[-1] in class_ids:
            filepath = os.path.join(path, 'voc', 'Annotations', value[0][:-4]+'.xml')
            if filepath not in saveDict:
                filelist.append(value[0][:-4])
                object_string = string_2.format(categorie_d[value[-1]], value[3][0], value[3][1], value[3][0]+value[3][2], value[3][1]+value[3][3])
                saveDict[filepath] = [string_1.format(value[0], value[0], value[2], value[1]), object_string]
            else:
                saveDict[filepath][1] += string_2.format(categorie_d[value[-1]], value[3][0], value[3][1], value[3][0]+value[3][2], value[3][1]+value[3][3])
            shutil.copy(os.path.join(path, key_p+year, value[0]), os.path.join(path, 'voc', 'JPEGImages', value[0]))
    for key,value in saveDict.items():
        with open(key, 'w') as fd:
            fd.write(''.join(value)+'</annotation>')
    return filelist

def createDirs():
    voc_path = os.path.join(path, 'voc')
    Annotations = os.path.join(voc_path, 'Annotations')
    if not os.path.exists(Annotations):
        os.makedirs(Annotations)
    Annotations = os.path.join(voc_path, 'Annotations')
    if not os.path.exists(Annotations):
        os.makedirs(Annotations)
    Main = os.path.join(voc_path, 'ImageSets', 'Main')
    if not os.path.exists(Main):
        os.makedirs(Main)
    JPEGImages = os.path.join(voc_path, 'JPEGImages')
    if not os.path.exists(JPEGImages):
        os.makedirs(JPEGImages)

if __name__ == '__main__':
    data = get_annotations('instances_%s%s.json'%(process, year))
    c_d, a_d = construct_data(data)
    if len(class_name):
        for name in class_name:
            for key,value in c_d.items():
                if name == value[0]:
                    if key not in class_id:
                        class_id.append(key)
                    break
    
    if len(class_id):
        createDirs()
        r_lists = get_by_ids(a_d, class_id, c_d, process)
        Main = os.path.join(path, 'voc', 'ImageSets', 'Main')
        with open(os.path.join(Main, process+'.txt')) as fd:
            for r in r_lists:
                fd.write(r+'\n')