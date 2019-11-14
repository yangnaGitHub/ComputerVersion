

###  video or webcam
#default is detecting person
src=../video2.mp4
#python trt_yolo3_module_1batch.py --webcam $src
## detect car
python trt_yolo3_module_1batch.py --webcam $src --class_num=2 --class_name=car


## image 
#python trt_yolo3_module_1batch_img.py --image=./images/person.jpg
