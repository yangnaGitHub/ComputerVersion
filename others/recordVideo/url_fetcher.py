#!/data/environments/anacoonda/envs/face/bin/python
import requests
import json
url = "http://10.149.0.180:8080/maskDetection/temp/getByCode"

DATA=[{"gb_CODE": "44031158001320002328"},{"gb_CODE": "44031158001320002463"},{"gb_CODE": "44031158001320029205"},{"gb_CODE": "44031158001320002362"},{"gb_CODE": "44031158001320029272"},{"gb_CODE": "44031158001320029237"},{"gb_CODE": "44031158001320002327"},
    {"gb_CODE": "44031158001320029263"},{"gb_CODE": "44031158001320029263"},{"gb_CODE": "44031158001320029237"},{"gb_CODE": "44031158001320029223"},{"gb_CODE": "44031158001320029259"},{"gb_CODE": "44031158001320002330"},{"gb_CODE": "44031158001320002230"}]
def rtsp_getter():
    RTSP=[]
    for d in DATA:
        res = requests.post(url=url,json=d)
        print("--"*10)
        #print(res.text)
        if res.text:
            pass
        else:
            continue
        rtsp=eval(res.text)['data']
        msg=eval(res.text)["msg"]
        retcode=eval(res.text)["retcode"]
        #print("rtsp:{}".format(rtsp))
        if rtsp:
            #RTSP.append(rtsp)
            #continue
            print("gb_CODE:{},\nrtsp:{}".format(d["gb_CODE"],rtsp))
        else:
            #print("url fetch faild!")
            print("gb_CODE:{}".format(d["gb_CODE"]))
            print("error massage: {}, {}".format(msg, retcode))
        RTSP.append(rtsp)
        print("--"*10)
    return RTSP

if __name__ == '__main__':
    rtsp_getter()
