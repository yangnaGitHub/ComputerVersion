#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 17:45:40 2020

@author: yangna
"""
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

Chrome_path = '/home/yangna/yangna/tool/chromedriver'
base_path = '/home/yangna/dubu'
login_path = 'http://web.duibu.cn/admin/login/?next=/admin/recognition/productmodel/%3Fp%3D0'

def initwebdriver():
    global driver
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(executable_path=Chrome_path, chrome_options=chrome_options)

def exitprocess():
    driver.quit()
    
def GetContent(mode, srcContent=driver.page_source):
    content = srcContent
    if isinstance(srcContent, str) or isinstance(srcContent, unicode):
        tr = etree.HTML(content)
    else:
        tr = srcContent
    result = tr.xpath(mode)
    return result

def GetParams(searchURL='http://www.baidu.com/'):
    driver.get(searchURL)

def loginWeb(user, password):
    driver.find_element_by_xpath('//input[@name="username"]').send_keys(user)
    driver.find_element_by_xpath('//input[@name="password"]').send_keys(password)
    driver.find_element_by_xpath('//input[@type="submit"]').click()

def generatePage(filepath='preview.html', srcCode=None):
    with open(filepath, 'w') as fd:
        fd.write(srcCode.encode('utf-8'))

list_map = {u'ID':'field-id', u'名称':'field-name', u'货号':'field-article_number',
            u'商家':'field-business', u'颜色':'field-color', u'编织方式':'field-weaving_way',
            u'克重':'field-gram_weight', u'成分':'field-ingredient', u'纱支':'field-yarn_count',
            u'缩率':'field-shrinkage', u'一级分类':'field-first_classification', u'二级分类':'field-second_classification',
            u'手机正面图片':'field-mobile_img_f', u'手机背面图片':'field-mobile_img_b', u'正面图片1':'field-img1',
            u'正面图片2':'field-img2', u'正面图片3':'field-img3', u'背面图片1':'field-img4', u'背面图片2':'field-img5', u'背面图片3':'field-img6'}
more_a = [u'ID', u'名称', u'货号', u'手机正面图片', u'手机背面图片', u'正面图片1', u'正面图片2', u'正面图片3', u'背面图片1', u'背面图片2', u'背面图片3']
pic_list = [u'手机正面图片', u'手机背面图片', u'正面图片1', u'正面图片2', u'正面图片3', u'背面图片1', u'背面图片2', u'背面图片3']
list_map_keys = list(list_map.keys())
webUrl = 'http://web.duibu.cn'
def generateFiles():
    allInfos = []
    results = GetContent('//a[@class="end"]')[0]
    end_page = int(results.text)
    for index in range(0, end_page):
        page_href = '?p=%d' % index
        if(0 != index):
            driver.find_element_by_xpath('//a[@href="%s"]' % page_href).click()
            #generatePage(filepath=str(index+1)+'.html', srcCode=driver.page_source)
        results = GetContent('//tbody/tr', srcContent=driver.page_source)
        for result in results:
            temp_dict = {}
            for list_map_key in list_map_keys:
                if list_map_key in more_a:
                    findstr = 'child::td[contains(@class,"%s")]/a' % list_map[list_map_key]
                    if list_map_key == u'ID':
                        findstr = 'child::th[contains(@class,"%s")]/a' % list_map[list_map_key]
                else:
                    findstr = 'child::td[contains(@class,"%s")]' % list_map[list_map_key]
                findresult = result.xpath(findstr)
                if(len(findresult)):
                    if findresult[0].text is not None:
                        temp_dict[list_map_key] = findresult[0].text.encode('utf-8')
                        print(findresult[0].text.encode('utf-8'))
                    if list_map_key in pic_list:
                        href = webUrl + findresult[0].attrib.get('href')
                        temp_dict[list_map_key] = href
                        print(href)
            allInfos.append(temp_dict)
    return allInfos

import xlwt
import requests
import os
def download(dUrl, savePath=base_path):
    filepath = os.path.join(savePath, os.path.basename(dUrl))
    if os.path.isfile(filepath):
        return
    r = requests.get(dUrl, stream=True)
    if r.status_code == 200:
        open(filepath, 'wb').write(r.content)
    del r

def dealInfo(allInfos):
    workbook = xlwt.Workbook(encoding = 'utf-8')
    worksheet = workbook.add_sheet('dubu')
    for index,allInfo in enumerate(allInfos):
        for inindex,list_map_key in enumerate(list_map_keys):
            if list_map_key in allInfo:
                if list_map_key in pic_list:
                    download(allInfo[list_map_key])
                worksheet.write(index+1, inindex, label=allInfo[list_map_key])
    for inindex,list_map_key in enumerate(list_map_keys):
        worksheet.write(0, inindex, label=list_map_key)
    workbook.save(os.path.join(base_path, 'dubu.xls'))

import pandas as pd
import shutil
def saveFile(temps, basePath, endPath):
    if not os.path.exists(endPath):
        os.makedirs(endPath)
    
    for index in range(temps.shape[0]):
        if pd.isnull(temps.iloc[index]):
            continue
        filename = os.path.basename(temps.iloc[index])
        before = os.path.join(basePath, filename)
        after = os.path.join(endPath, filename)
        if os.path.isfile(before):
            shutil.copyfile(before, after)
        else:
            print(filename)

combine = lambda x, code=',': reduce(lambda x, y: [i+code+j for i in x for j in y], x)
def classesPic(filename=os.path.join(base_path, 'dubu.xls'), class_list=[u'编织方式', u'成分'], basePath=base_path, savePath=os.path.join(base_path, 'result'), savePic=[0,0,1,1,1,1,1,1], saveMethod=1):
    saveCols = [pic_list[index] for index,saveflag in enumerate(savePic) if saveflag]
    df = pd.read_excel(filename)
    #df.columns
    all_values = []
    for class_l in class_list:
        all_values.append(list(df.loc[:, class_l].value_counts().index))
    all_value_strs = combine(all_values)
    infos = {}
    for index,all_value_s in enumerate(all_value_strs):
        all_value_str = all_value_s.split(',')
        temp = df
        for key,val in zip(class_list, all_value_str):
            temp = temp[temp[key]==val]
        if 0 == temp.shape[0]:
            continue
        infos[all_value_s] = [index, temp.shape[0]]
        parentPath = os.path.join(savePath, str(index))
        for saveCol in saveCols:
            if 1 == saveMethod:
                endPath = parentPath
            elif 0 == saveMethod:
                endPath = os.path.join(parentPath, saveCol)
            saveFile(temp.loc[:, saveCol], basePath, endPath)
    infos = sorted(infos.items(), key=lambda item:item[1][1], reverse=True)
    with open(os.path.join(savePath, 'infos'), 'wb') as fd:
        fd.write(u'文件夹名  实例数量  文件夹类型\n')
        for info in infos:
            fd.write(('%3d    %5d       %s\n' % (info[1][0], info[1][1], info[0])).encode('utf-8'))

if __name__ == '__main__':
    #craw infos from web
    try:
        saveFilename = os.path.join(base_path, 'dubu.xls')
        if not os.path.isfile(saveFilename):
            initwebdriver()
            GetParams(searchURL=login_path)
            loginWeb(user='bpht', password='bpht2020')
            allInfos = generateFiles()
            dealInfo(allInfos)
    except Exception, Arguments:
        print "Error:", Arguments
    finally:
        if driver:
            exitprocess()
    #classes your pic accroding you parms
    classesPic()
    classesPic(savePath=os.path.join(base_path, 'result_div'), saveMethod=0)

mymap = {}
for s_ in test:
    s_lists = s_.split('/')
    for s_list in s_lists:
        findindex = s_list.find('%')
        key = ''
        if -1 != findindex:
            key = s_list[findindex+1:]
        else:
            if -1 != s_list.find('％'):
                key = s_list[findindex+3:]
            else:
                print(s_list.encode('utf-8'))
        if key:
            if key in mymap:
                mymap[key] += 1
            else:
                mymap[key] = 1

mymap_s = sorted(mymap.items(), key=lambda item:item[1], reverse=True)
for info in mymap_s:
    print(info[0].encode('utf-8'))
    #print(info[1])