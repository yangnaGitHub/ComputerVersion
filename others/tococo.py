#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 18:00:06 2019

@author: yangna
"""

import os
import glob
import random
import json
import numpy as np
import cv2
import time
import shutil

def renameFiles(rootpath, startIndex=0):
    images = glob.glob(os.path.join(rootpath, '*.jpg'))
    for image in images:
        os.rename(image, os.path.join(rootpath, '%06d.jpg'%startIndex))
        startIndex += 1
renameFiles('/home/yangna/cropVideo', startIndex=2220)

def loadJson(filepath):
    with open(filepath, 'r') as fd:
        contents = fd.readlines()
        
    #print(contents, len(contents))
    if 1 != len(contents):
        t_str = ''
        for content in contents:
            t_str += content.strip()
        contents = t_str
    else:
        contents = contents[0]
    imagePathIndex = contents.find('imagePath')+13
    imagePathoffset = imagePathIndex+contents[imagePathIndex:].find('"')
    w_tag = contents[imagePathIndex:imagePathoffset].rfind("\\")
    if -1 != w_tag:
        newIndex = imagePathIndex + w_tag
        newcontents = contents[:imagePathIndex]
        newcontents += contents[newIndex+1:imagePathoffset]
        newcontents += contents[imagePathoffset:]
        contents = newcontents
    filedict = json.loads(contents)
    return filedict

######labelme to coco start################
#labelme generate coco json
def LabelmeGCJ(rootpath, images, categorieslist, after=3, wtype='instances', phase='train', idstart=0):
    finallydict = {}
    imageslist = []
    annotationslist = []
    index = 0
    categoriesdict = {}
    categoriesname = []
    for categories in categorieslist:
        categoriesdict[categories['name']] = [categories['id']]
        if 'keypoints' in categories:
            categoriesdict[categories['name']].append(len(categories['keypoints']))
        categoriesname.append(categories['name'])
    for filepath in images:#one json
        j_filepath = filepath[:-after]+'json'
        print(j_filepath)
        filedict = loadJson(j_filepath)
        imageslist.append({'file_name':filedict['imagePath'],
                           'height':filedict['imageHeight'],
                           'width':filedict['imageWidth'],
                           'id':idstart})
        annotationsdicts = {}
        for shapes in filedict['shapes']:
            print(shapes['label'])
            typenames = shapes['label'].split('_')
            typename = typenames[0]
            if len(typenames) < 2:
                typeids = '0'
            else:
                typeids = typenames[1]
            if  typename not in categoriesname:#pick some type
                continue
            if typeids not in annotationsdicts:
                annotationsdicts[typeids] = {}
            if 'polygon' == shapes['shape_type']:
                points = np.array(shapes['points'])
                bbox = [points[:, 0].min(), points[:, 1].min(), points[:, 0].max(), points[:, 1].max()]
                bbox[2] -= bbox[0]
                bbox[3] -= bbox[1]
                #print(points)
                #bbox = list(cv2.boundingRect(points))
                annotationsdicts[typeids]['image_id'] = idstart
                annotationsdicts[typeids]['id'] = index
                annotationsdicts[typeids]['iscrowd'] = 0
                annotationsdicts[typeids]['segmentation'] = points.reshape((1, -1)).tolist()
                annotationsdicts[typeids]['category_id'] = categoriesdict[typename][0]
                annotationsdicts[typeids]['bbox'] = bbox
                annotationsdicts[typeids]['area'] = bbox[2]*bbox[3]#cv2.contourArea(points)
                index += 1
            elif 'point' == shapes['shape_type']:
                if 'keypoints' != wtype:
                    continue
                if 'num_keypoints' not in annotationsdicts[typeids]:
                    annotationsdicts[typeids]['num_keypoints'] = 0
                    annotationsdicts[typeids]['keypoints'] = [0]*3*categoriesdict[typename][1]
                annotationsdicts[typeids]['num_keypoints'] += 1
                k_index = 3 * (int(typenames[2]) - 1)
                annotationsdicts[typeids]['keypoints'][k_index] = shapes['points'][0][0]
                annotationsdicts[typeids]['keypoints'][k_index+1] = shapes['points'][0][1]
                annotationsdicts[typeids]['keypoints'][k_index+2] = 2
        annotationslist.extend([value for value in annotationsdicts.values()])
        idstart += 1
    
    #write to json
    finallypath = os.path.join(rootpath, '%s_%s.json' % (wtype, phase))
    finallydict['info'] = {'contributor':'deepblue', 'date_created':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) ,
               'description':'pig datasets', 'url':'http://deepblueai.com',
               'version':'0.1', 'year': 2019}
    finallydict['licenses'] = [{'id':1, 'name':'yangna', 'url':'http://yangna'}]
    #finallydict['type'] = wtype
    finallydict['categories'] = categorieslist
    finallydict['images'] = imageslist
    finallydict['annotations'] = annotationslist
    finallystr = json.dumps(finallydict)
    with open(finallypath, 'w') as fd:
        fd.write(finallystr)
    
    return idstart

def GetLists(allpic, pos, totalinps, dealinps, otherinps, inp_allpic):
    if 0 == otherinps:
        return pos, None
    dealinps += otherinps
    if totalinps == dealinps:
        return -1, allpic[pos:]
    else:
        return pos+int(inp_allpic*otherinps), allpic[pos:pos+int(inp_allpic*otherinps)]

def copyFiles(rootpath, images, phase='train'):
    s_path = os.path.join(rootpath, phase)
    if not os.path.exists(s_path):
        os.makedirs(s_path)
    for filepath in images:
        shutil.copyfile(filepath, os.path.join(s_path, os.path.split(filepath)[1]))

def LabelmeToCoco(rootpath, pformat='jpg', categorieslist=[], train_val_test=[7, 2, 1], idstart=0, wtype='instances'):
    if 0 == len(categorieslist):
        return
    allpic = glob.glob(os.path.join(rootpath, '*.'+pformat))
    random.shuffle(allpic)

    pos = 0
    dealinps = 0
    idstart = 0
    phaseDict = {0:'train', 1:'val', 2:'test'}
    totalinps = sum(train_val_test)
    inp_allpic = float(len(allpic))/totalinps
    for index,val in enumerate(train_val_test):
        pos, pic_lists = GetLists(allpic, pos, totalinps, dealinps, val, inp_allpic)
        if pic_lists:
            copyFiles(rootpath, pic_lists, phase=phaseDict[index])
            idstart = LabelmeGCJ(rootpath, pic_lists, categorieslist, after=len(pformat), wtype=wtype, phase=phaseDict[index], idstart=idstart)

#run instances
#categorieslist = [{'supercategory': 'animal', 'id': 1, 'name': 'pig'}]
def generateFiles(root_path='/home/yangna/pics', categorieslist=None, GEN_TYPE = 'instances'):
    if 'instances' == GEN_TYPE:
        if categorieslist is None:
            categorieslist = [{'supercategory': 'person', 'id': 1, 'name': 'person'},
                              {'supercategory': 'person', "id": 19, 'name': "pig"}]
        LabelmeToCoco(root_path, pformat='jpg', categorieslist=categorieslist, train_val_test=[8, 2, 0], wtype=GEN_TYPE)
    elif 'keypoints' == GEN_TYPE:
        if categorieslist is None:
            categorieslist = [{'supercategory': 'person', 'id': 1, 'name': 'person',
                               'keypoints': ['nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear', 'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow', 'left_wrist', 'right_wrist', 'left_hip', 'right_hip', 'left_knee', 'right_knee', 'left_ankle', 'right_ankle'],
                               'skeleton': [[16, 14], [14, 12], [17, 15], [15, 13], [12, 13], [6, 12], [7, 13], [6, 7], [6, 8], [7, 9], [8, 10], [9, 11], [2, 3], [1, 2], [1, 3], [2, 4], [3, 5], [4, 6], [5, 7]]},
                              {'supercategory': 'animal', 'id': 19, 'name': 'pig',
                               'keypoints': ['nose', 'left_shoulder', 'right_shoulder', 'left_wrist', 'right_wrist', 'left_hip', 'right_hip', 'left_ankle', 'right_ankle'],
                               'skeleton': [[8, 6], [9, 7], [2, 6], [3, 7], [2, 4], [3, 5], [1, 2], [1, 3]]}]
        LabelmeToCoco(root_path, pformat='jpg', categorieslist=categorieslist, train_val_test=[8, 2, 0], wtype=GEN_TYPE)
gen_categories = [{'supercategory': 'carbody', 'id': 1, 'name': 'gap'}]
generateFiles(root_path='/home/yangna/12345', categorieslist=gen_categories)
######labelme to coco end################

######coco pick one type to coco start################
def pickTypeFromCoco(rootpath, outpath='/home/yangna/outcoco', types=[], wtype='instances', year=2017, pic_start=0, pic_size=1000):
    if 0 == len(types):
        return
    #train_path = os.path.join(rootpath, 'train%d' % year)
    #test_path = os.path.join(rootpath, 'test%d' % year)
    #val_path = os.path.join(rootpath, 'val%d' % year)
    finallydict = {}
    annotation_path = os.path.join(rootpath, 'annotations')
    imagesPath = ''
    targetPath = ''
    v_jsons = glob.glob(os.path.join(annotation_path, '%s*.json'%wtype))
    skip_pic_index = -1
    for v_json in v_jsons:
        if -1 != os.path.basename(v_json).find('val%s'%year):
            imagesPath = os.path.join(rootpath, 'val%s'%year)
            targetPath = os.path.join(outpath, 'val%s'%year)
        elif -1 != os.path.basename(v_json).find('train%s'%year):
            imagesPath = os.path.join(rootpath, 'train%s'%year)
            targetPath = os.path.join(outpath, 'train%s'%year)
        if not os.path.exists(targetPath):
            os.makedirs(targetPath)
        filedict = loadJson(v_json)
        whichtypes = []
        whichimages = []
        annotationslist = []
        categorieslist = []
        imageslist = []
        for categorie in filedict['categories']:
            if categorie['name'] in types:
                whichtypes.append(categorie['id'])
                categorieslist.append(categorie)
        for annotation in filedict['annotations']:
            if annotation['category_id'] in whichtypes:
                if annotation['image_id'] not in whichimages:
                    skip_pic_index += 1
                    if skip_pic_index < pic_start:
                        continue
                    whichimages.append(annotation['image_id'])
                    #if pic_size == len(whichimages):
                    #    break
        for image in filedict['images']:
            if image['id'] in whichimages:
                imageslist.append(image)
                shutil.copyfile(os.path.join(imagesPath, image['file_name']), os.path.join(targetPath, image['file_name']))
        for annotation in filedict['annotations']:
            if (annotation['category_id'] in whichtypes) and (annotation['image_id'] in whichimages):
                annotationslist.append(annotation)
        writefile = os.path.join(outpath, os.path.basename(v_json))
        #writefile = v_json[:-5]+'-'+'_'.join([str(s_type) for s_type in whichtypes])+'.json'
        #print(writefile)
        finallydict['info'] = filedict['info']
        finallydict['licenses'] = filedict['licenses']
        #finallydict['type'] = filedict['type']
        finallydict['categories'] = categorieslist
        finallydict['images'] = imageslist
        finallydict['annotations'] = annotationslist
        finallystr = json.dumps(finallydict)
        with open(writefile, 'w') as fd:
            fd.write(finallystr)

#run instances
#['person', 'bicycle', 'car', 'motorcycle', 'bus', 'train', 'truck']
#[{u'id': 1, u'name': u'person', u'supercategory': u'person'},
# {u'id': 2, u'name': u'bicycle', u'supercategory': u'vehicle'},
# {u'id': 3, u'name': u'car', u'supercategory': u'vehicle'},
# {u'id': 4, u'name': u'motorcycle', u'supercategory': u'vehicle'},
# {u'id': 6, u'name': u'bus', u'supercategory': u'vehicle'},
# {u'id': 7, u'name': u'train', u'supercategory': u'vehicle'},
# {u'id': 8, u'name': u'truck', u'supercategory': u'vehicle'}]
pickTypeFromCoco('/yang_data/coco/2017', outpath='/home/yangna/out', types=['person', 'bicycle', 'car', 'motorcycle', 'bus', 'train', 'truck'], pic_start=0, pic_size=2000)
######coco pick one type to coco end################

######mix coco json file start################
def getNewId(ids, maxIndex=100):
    while True:
        newId = random.randint(0, maxIndex)
        if newId not in ids:
            return newId

def mixJsonFile(s_f_1, s_f_2, outfile):
    filedict_1 = loadJson(s_f_1)
    filedict_2 = loadJson(s_f_2)
    finallydict = {}
    finallydict['info'] = filedict_1['info']
    finallydict['licenses'] = filedict_1['licenses']
    
    #categories not repeat
    categorieslist = []
    categoriesdict = {}
    changeCds = {}
    for categorie in filedict_1['categories']:
        categoriesdict[categorie['id']] = categorie['name']
    categorieslist.extend(filedict_1['categories'])
    for categorie in filedict_2['categories']:
        if categorie['id'] not in categoriesdict.keys():
            categoriesdict[categorie['id']] = categorie['name']
            categorieslist.append(categorie)
        else:
            if categorie['name'] != categoriesdict[categorie['id']]:
                newId = getNewId(categoriesdict.keys())
                changeCds[categorie['id']] = newId
                categorie['id'] = newId
                categoriesdict[categorie['id']] = categorie['name']
                categorieslist.append(categorie)
#    print(categoriesdict)
#    print(filedict_1['categories'])
#    print(filedict_2['categories'])
    #image
    ids = []
    changeIds = {}
    ids.extend([images['id'] for images in filedict_1['images']])
    for images in filedict_2['images']:
        if images['id'] in ids:
            newId = getNewId(ids, maxIndex=10000000)
            changeIds[images['id']] = newId
            images['id'] = newId
        ids.append(images['id'])
    
    #annotations
    ids = []
    ids.extend([annotations['id'] for annotations in filedict_1['annotations']])
    for annotations in filedict_2['annotations']:
        if annotations['id'] in ids:
            newId = getNewId(ids, maxIndex=100000000)
            annotations['id'] = newId
        ids.append(annotations['id'])
        if annotations['image_id'] in changeIds.keys():
            annotations['image_id'] = changeIds[annotations['image_id']]
        if annotations['category_id'] in changeCds.keys():
            annotations['category_id'] = changeCds[annotations['category_id']]
    
    #mix
    #finallydict['type'] = filedict['type']
    print(categorieslist)
    finallydict['categories'] = categorieslist
    finallydict['images'] = filedict_1['images']+filedict_2['images']
    finallydict['annotations'] = filedict_1['annotations']+filedict_2['annotations']
    finallystr = json.dumps(finallydict)
    with open(outfile, 'w') as fd:
        fd.write(finallystr)
#run instances
#mixJsonFile('/home/yangna/outcoco/instances_train2014-1.json', '/home/yangna/yangna/code/object_segmentation/maskscoring_rcnn/datasets/pig/annotations/instances_train_old.json', '/home/yangna/outcoco/instances_train.json')
mixJsonFile('/home/yangna/out/instances_train2014.json', '/home/yangna/yangna/project/pigmall/data/all/mixData-end/instances_train.json', '/home/yangna/instances_train.json')
mixJsonFile('/home/yangna/out/instances_val2014.json', '/home/yangna/yangna/project/pigmall/data/all/mixData-end/instances_val.json', '/home/yangna/instances_val.json')
######mix coco json file end################

######show dataset start###################
colors = [(0,0,255), (255,255,0), (0,255,255), (0,255,0), (255,0,0), (255,0,255), (128,128,128), (0,128,128), (128,128,0), (128,0,128), (255,255,255)]
len_colors = len(colors)
def showDateset(rootpath, files='instances', types='val'):
    imagespath = ''
    for afiles in os.listdir(rootpath):
        if os.path.isdir(os.path.join(rootpath, afiles)) and afiles.startswith(types):
            imagespath = os.path.join(rootpath, afiles)
    if not imagespath:
        return
    annotations = os.path.join(rootpath, 'annotations')
    f_annotations = os.listdir(annotations)
    fileType = files+'_'+types
    filename = os.path.join(annotations, [f_annotation for f_annotation in f_annotations if -1 != f_annotation.find(fileType)][0])
    filedict = loadJson(filename)
    categories = {}
    for categorie in filedict['categories']:
        categories[categorie['id']] = categorie['name']
    
    infos = {}
    for annotation in filedict['annotations']:
        if annotation['image_id'] in infos:
            infos[annotation['image_id']]['annotations'].append(annotation)
        else:
            infos[annotation['image_id']] = {}
            infos[annotation['image_id']]['annotations'] = [annotation]
    for image in filedict['images']:
        #print(image['file_name'])
        if -1 == image['file_name'].find('101338'):
            continue
        print(infos[image['id']])
        imagepath = os.path.join(imagespath, image['file_name'])
        frame = cv2.imread(imagepath)
        if image['id'] in infos:
            color_maps = {}
            color_map = (0,0,0)
            color_index = 0
            for annotation in infos[image['id']]['annotations']:
                if annotation['category_id'] not in color_maps:
                    if color_index < len_colors:
                        color_maps[annotation['category_id']] = colors[color_index]
                        color_index += 1
                    else:
                        color_maps[annotation['category_id']] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                color_map =  color_maps[annotation['category_id']]
                bbox = map(lambda x:int(x+0.5), annotation['bbox'])
                cv2.rectangle(frame, (bbox[0],bbox[1]), (bbox[0]+bbox[2],bbox[1]+bbox[3]), color_map, 2)
                cv2.putText(frame, str(annotation['category_id'])+'_'+str(categories[annotation['category_id']]), (bbox[0]+bbox[2]//2,bbox[1]+bbox[3]//2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_map, 2)
        cv2.imshow('images', frame)
        keyvalue = cv2.waitKey(0)&0xFF
        if ord('n') == keyvalue:
            continue
        elif ord('q') == keyvalue:
            cv2.destroyAllWindows()
            break
        else:
            pass
showDateset(rootpath='/home/yangna/deepfashion', types='train')
######show dataset end###################

######coco to darknet start#################
def convert(w, h, box):
    dw = 1./w
    dh = 1./h
    x = box[0] + box[2]/2.0 - 1
    y = box[1] + box[3]/2.0 - 1
    x = x*dw
    w = box[2]*dw
    y = y*dh
    h = box[3]*dh
    return x,y,w,h

def getInfo(imagesinfo, annotationsinfo, reids, annotation, filespath, pfilepath):
    filedict = loadJson(annotation)
    categories = {}
    for index, categorie in enumerate(filedict['categories']):
        categories[categorie['id']] = index
    for images in filedict['images']:
        if images['id'] not in imagesinfo:
            imagesinfo[images['id']] = [os.path.join(pfilepath, images['file_name']), images['width'], images['height']]
    for annotations in filedict['annotations']:
        w,h = imagesinfo[annotations['image_id']][1],imagesinfo[annotations['image_id']][2]
        x,y,w,h = convert(w,h,annotations['bbox'])
#        if annotations['category_id'] not in reids:
#            reids[annotations['category_id']] = len(reids);
#        if annotations['image_id'] not in annotationsinfo:
#            annotationsinfo[annotations['image_id']] = [[reids[annotations['category_id']],x,y,w,h]]
#        else:
#            annotationsinfo[annotations['image_id']].append([reids[annotations['category_id']],x,y,w,h])
        if annotations['image_id'] not in annotationsinfo:
            annotationsinfo[annotations['image_id']] = [[categories[annotations['category_id']],x,y,w,h]]
        else:
            annotationsinfo[annotations['image_id']].append([categories[annotations['category_id']],x,y,w,h])

def cocoToDarknet(rootpath='/home/yangna/out', savePath='', iprefix='images', lprefix='labels', split=8):
    annotations = glob.glob(os.path.join(rootpath, 'annotations', '*.json'))
#    annotations = ['/home/yangna/out/instances_val2017.json']
    imagesinfo = {}
    annotationsinfo = {}
    reids = {}
    for annotation in annotations:
        filepath = annotation.split('/')[-1].split('_')[-1][:-5]
        saveldir = os.path.join(savePath, lprefix, filepath)
        saveidir = os.path.join(savePath, iprefix, filepath)
        if not os.path.exists(saveldir):
            os.makedirs(saveldir)
        if not os.path.exists(saveidir):
            os.makedirs(saveidir)
        filespath = os.path.join(rootpath, filepath)
        getInfo(imagesinfo, annotationsinfo, reids, annotation, filespath, filepath)
    imageslist = list(imagesinfo.keys())
    random.shuffle(imageslist)
    maxIndex = len(imageslist)
    centerIndex = int(maxIndex/10*split+0.5)
    saveldir = os.path.join(savePath, lprefix)
    saveidir = os.path.join(savePath, iprefix)
    with open(os.path.join(savePath, 'train.txt'), 'w') as fd:
        [fd.write(os.path.join(saveidir, imagesinfo[image_id][0])+'\n') for image_id in imageslist[:centerIndex]]
    with open(os.path.join(savePath, 'val.txt'), 'w') as fd:
        [fd.write(os.path.join(saveidir, imagesinfo[image_id][0])+'\n') for image_id in imageslist[centerIndex:]]
    for index in range(maxIndex):
        image_id = imageslist[index]
        string = ''
        for content in annotationsinfo[image_id]:
            string += ' '.join(list(map(str, content)))+'\n'
#        print(string)
        with open(os.path.join(saveldir, imagesinfo[image_id][0][:-3]+'txt'), 'w') as fd:
            fd.write(string)
        shutil.copyfile(os.path.join(rootpath, imagesinfo[image_id][0]), os.path.join(saveidir, imagesinfo[image_id][0]))

cocoToDarknet(rootpath='/home/yangna/deepfashion', savePath='/home/yangna/yangna/code/detection/yolov5/deepfashion')


def correctFiles(root_path):
    filelists = glob.glob(os.path.join(root_path, '*.txt'))
    for filepath in filelists:
        #filepath = '/home/yangna/yangna/code/detection/yolov5/deepfashion/labels/train2017/101338.txt'
        with open(filepath, 'r') as fd:
            contents = fd.readlines()
        ifchange = False
        string = ''
        for content in contents:
            rowValue = list(map(lambda x: 0.0 if float(x) < 0.0 else float(x), content[:-1].split(' ')[1:]))
            if 4 == rowValue.count(0.0):
                ifchange = True
                continue
            #print(content, rowValue, rowValue.count(0.0))
            string += content
        if ifchange:
            print(filepath)
            with open(filepath, 'w') as fd:
                fd.write(string)
correctFiles('/home/yangna/yangna/code/detection/yolov5/deepfashion/labels/val2017')
######coco to darknet end###################
#[u'info', u'images', u'licenses', u'type', u'annotations', u'categories']
'''
info dict
{u'contributor': u'Microsoft COCO group',
 u'date_created': u'2015-01-27 09:11:52.357475',
 u'description': u'This is stable 1.0 version of the 2014 MS COCO dataset.',
 u'url': u'http://mscoco.org',
 u'version': u'1.0',
 u'year': 2014}

licenses list
[0]
{u'id': 1,
 u'name': u'Attribution-NonCommercial-ShareAlike License',
 u'url': u'http://creativecommons.org/licenses/by-nc-sa/2.0/'}

type unicode(either exist)
u'instances'

images list
[0]
{u'date_captured': u'2013-11-14 17:02:52',
 u'file_name': u'COCO_val2014_000000397133.jpg',
 u'height': 427,
 u'id': 397133,
 u'license': 4,
 u'url': u'http://farm7.staticflickr.com/6116/6255196340_da26cf2c9e_z.jpg',
 u'width': 640}

categories list
[0]
{u'id': 1, u'name': u'person', u'supercategory': u'person'}

annotations list
[0]
{u'area': 702.10575,
 u'bbox': [473.07, 395.93, 38.65, 28.67],
 u'category_id': 18,
 u'id': 1768,
 u'image_id': 289343,
 u'iscrowd': 0,
 u'segmentation': [[510.66,
   423.01,
   511.72,
   420.03,
   510.45,
   416,
   510.34,
   413.02,
   510.77,
   410.26,
   510.77,
   407.5,
   510.34,
   405.16,
   511.51,
   402.83,
   511.41,
   400.49,
   510.24,
   398.16,
   509.39,
   397.31,
   504.61,
   399.22,
   502.17,
   399.64,
   500.89,
   401.66,
   500.47,
   402.08,
   499.09,
   401.87,
   495.79,
   401.98,
   490.59,
   401.77,
   488.79,
   401.77,
   485.39,
   398.58,
   483.9,
   397.31,
   481.56,
   396.35,
   478.48,
   395.93,
   476.68,
   396.03,
   475.4,
   396.77,
   473.92,
   398.79,
   473.28,
   399.96,
   473.49,
   401.87,
   474.56,
   403.47,
   473.07,
   405.59,
   473.39,
   407.71,
   476.68,
   409.41,
   479.23,
   409.73,
   481.56,
   410.69,
   480.4,
   411.85,
   481.35,
   414.93,
   479.86,
   418.65,
   477.32,
   420.03,
   476.04,
   422.58,
   479.02,
   422.58,
   480.29,
   423.01,
   483.79,
   419.93,
   486.66,
   416.21,
   490.06,
   415.57,
   492.18,
   416.85,
   491.65,
   420.24,
   492.82,
   422.9,
   493.56,
   424.39,
   496.43,
   424.6,
   498.02,
   423.01,
   498.13,
   421.31,
   497.07,
   420.03,
   497.07,
   415.15,
   496.33,
   414.51,
   501.1,
   411.96,
   502.06,
   411.32,
   503.02,
   415.04,
   503.33,
   418.12,
   501.1,
   420.24,
   498.98,
   421.63,
   500.47,
   424.39,
   505.03,
   423.32,
   506.2,
   421.31,
   507.69,
   419.5,
   506.31,
   423.32,
   510.03,
   423.01,
   510.45,
   423.01]]}
'''