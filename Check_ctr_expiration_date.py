#/usr/bin/env python
# -*- coding: utf-8 -*-
import os,commands
import json
import datetime
from dateutil import tz
import time
import requests
import re

def Send_Mess_Chat(message):
    pass
def Check_expire_time(**kwargs):
    Msg = u"将要到期的证书有:\n"
    for i in kwargs:
        Time_left = abs(Get_current_timestamp() - kwargs[i][1])
        if Time_left < 2592000:
            all_time = datetime.timedelta(seconds=Time_left)
            Day_left = all_time.days
            all_time = re.findall('(\d+):(\d+):(\d+)',str(all_time))
            print all_time[0]
            Msg = Msg + u"证书名：%s 到期时间：%s 距今日还有：%s天 %s时 %s分 %s秒\n"%(i,kwargs[i][0],Day_left,all_time[0][0],all_time[0][1],all_time[0][2])
    print Msg

def Deal_timezone(data):
    '''
    return a time that tz is Asia/Shanghai and timestamp
    '''
    tz_here = tz.gettz("Asia/Shanghai")
    tz_gmt = tz.gettz("GMT")
    Time_src = time.mktime(time.strptime(data, "%b %d %H:%M:%S %Y %Z"))
    Time_cst = datetime.datetime.fromtimestamp(
        Time_src).replace(tzinfo=tz_gmt).astimezone(tz_here)
    Time_stamp = time.mktime(Time_cst.timetuple())
    Time_cst = Time_cst.strftime("%Y-%m-%d %H:%M:%S ")
    return [Time_cst, int(Time_stamp)]

def Get_current_timestamp():
    return int(time.mktime(datetime.datetime.now().utctimetuple()))

def Init(data):
    Name_time = {}
    time_value = []  # 作为每一证书的value,里面放两项。[0]上海时间,[1]时间戳
    all = commands.getoutput(
        'find /home/ubuntu/pki/output -type f|grep -E "(server|client)".pem').split('\n')
    f = open("/Script/file_record", 'w')  # 建立目录列表
    for i in all:
        time_src = commands.getoutput("openssl x509 -enddate -noout -in %s|awk -F'=' '{print $2}'" % i)
        time_value = Deal_timezone(time_src)
        Name_time[i] = time_value
    json.dump(Name_time, f)
    f.close()
    f = open("/Script/time_record", 'w')  # 建立时间标识
    f.write(data)
    f.close()
    return Name_time

Modify_time = os.popen("stat /Script/|awk 'NR==6 {print}'").next().strip().split(': ')[1]
if not os.path.exists('/Script/time_record'):  # 文件不存在，程序初始化，建立  文件列表及 创建时间标识
    os.system("touch /Script/time_record /Script/file_record")
    Init(Modify_time)
    Create = Modify_time
else:  # 文件存在，读取文件内容 开始进行判断
    f = open("/Script/time_record", 'r')
    Create = f.read()
    f.close()
if Create == Modify_time:  # 通过时间戳 判断文件没有更改，比较每个证书的过期时间
    Name_time = {}
    f = open('/Script/file_record', 'r')
    Name_time = json.load(f)
    f.close()
    Check_expire_time(**Name_time)

else:  # 通过时间标识，判断文件更改，使用当前信息初始化
    Check_expire_time(**Init(Modify_time))

