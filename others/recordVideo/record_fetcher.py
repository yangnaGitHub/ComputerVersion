#!/data/environments/anacoonda/envs/face/bin/python
import time
import cv2
import json
from url_fetcher import *
video_dir="/data/projects/video_collector/video/{}".format(time.strftime('%Y%m%d',time.localtime(time.time())))

def record(urlList,seconds):
    cap=cv2.VideoCapture(url)
    #fourcc = cv2.VideoWriter_fourcc(*'h264')
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fps = cap.get(cv2.CAP_PROP_FPS)
    out = cv2.VideoWriter(str(time.time())+'.avi',fourcc,fps, (int(cap.get(3)), int(cap.get(4))))
    tTime=0
    tSize=fps*seconds
    print("recording...")
    while (True):
        ret,frame=cap.read()#返回一个布尔值和一个图像矩阵
        gray = cv2.cvtColor(frame, 0)
        frame_show = cv2.resize(frame, (640, 560))
        flip=cv2.flip(gray,1)#一个标志，指定如何翻转数组; 0表示绕x轴翻转，正值（例如1）表示绕y轴翻转。负值（例如，-1）表示在两个轴周围翻转
        out.write(frame)
        #cv2.imshow("frame", flip)
        #cv2.imshow("Playing Video",frame_show)
        tTime+=1
        #print(tTime//fps)
        if tTime >= tSize:
            break
    cap.release()
    #open.release()
    cv2.destroyAllWindows()



from multiprocessing import Process
import os

# 子进程要执行的代码
def run_proc(videoIndex,seconds):
    cap=cv2.VideoCapture(urlList[videoIndex])
    fourcc = cv2.VideoWriter_fourcc(*'h264')
    #fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fps = cap.get(cv2.CAP_PROP_FPS)
    out = cv2.VideoWriter("{}/{}".format(video_dir,str(videoIndex)+'-'+str(time.time())[1:8]+'.mkv'),fourcc,fps, (int(cap.get(3)), int(cap.get(4))))
    #out = cv2.VideoWriter(str(videoIndex)+'-'+str(time.time())[5:]+'.avi',fourcc,fps, (640, 560))
    tTime=0
    tSize=fps*seconds
    print("recording...video id: "+str(videoIndex))
    while (True):
        ret,frame=cap.read()#返回一个布尔值和一个图像矩阵
        #gray = cv2.cvtColor(frame, 0)
        #frame_show = cv2.resize(frame, (1280, 720))
        if tTime%5 == 0: # one second 1/5 frame
            out.write(frame)
        tTime+=1
        if tTime >= tSize:
            break
    cap.release()
    #open.release()
    #cv2.destroyAllWindows()

if __name__=='__main__':
    if not  os.path.exists(video_dir):
        os.mkdir(video_dir)
    urlList=rtsp_getter()
    pProcess = []
    for i in range(len(urlList)):
        if not urlList[i]:
            continue
        pProcess.append(Process(target=run_proc, args=(i,720,))) #最后一个数据是记录的秒数
    for p in pProcess:
        p.start()
    for p in pProcess:
        p.join()



