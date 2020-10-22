#!/data/environments/anacoonda/envs/face/bin/python
import cv2 as cv
from url_fetcher import *
import time
import os
from multiprocessing import Process
from multiprocessing import Pool
def record(video_path,rtsp,hour=1):

    cap = cv.VideoCapture(rtsp)
    ret,frame=cap.read()
    if not ret:
        return 
    frame_cout=0
    frameSize=frame.shape[:2]
    codec=cv.VideoWriter_fourcc(*'h264')
    fps=25.0
    recorder=cv.VideoWriter(video_path,codec,fps,frameSize)
    while cap.isOpened():
        _,frame=cap.read()
        if _:
            recorder.write(frame)
        else:
            continue
        frame_cout+=1
        if frame_count > 25*3600*hour:
            break
    print("[recorder]: video {} saved!".format(rtsp))
    cap.release()
    recorder.release()

rtsps=rtsp_getter()
p=Pool()
video_dir="video/{}/".format(time.strftime('%Y%m%d',time.localtime(time.time())))
if not  os.path.exists(video_dir):
    os.mkdir(video_dir)

for i,r in enumerate(rtsps):
    if r:
        video_name="{}_{}".format(i,int(time.time()*1000))
        video_path=video_dir+video_name
        #record(video_path,r)
        p.apply_async(record,(video_path,r,0.25)) 
p.close()
p.join()

