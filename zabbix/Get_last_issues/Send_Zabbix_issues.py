#!/usr/bin/python
import urllib3
import json
import time
import requests
## Init
Zabbix_Cusor = urllib3.PoolManager()
Zabbix_url = "http://zabbix_URL/api_jsonrpc.php"
Zabbix_username = 'username'
Zabbix_pass = 'password'
Zabbix_header = {"Content-Type":"application/json"}

def Get_hostname(triggerid,*args):
    Get_host = json.dumps({
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
        "output": ["host","hostid"],
        "triggerids": triggerid,
        },
        "auth": Session,
        "id": 1
    })
    Host_list = Get_value(Get_host).data
    return Process(Host_list)

def Convert_time(value):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(value)))

def Get_value(Request_body):
    Value = Zabbix_Cusor.request('POST',
                                Zabbix_url,
                                body=Request_body,
                                headers=Zabbix_header
                                )
    return Value

def Process(value):
    '''

    :param value:
    :return: a list

    '''
    try:
        value1 = value.decode('utf-8')
        User_Data = json.loads(value1)['result']
        return User_Data
    except TypeError:
        print("No respone")
        raise KeyError

def Change_triggerid_to_Hostname(triggerid):
    '''
    :param triggerid:
    :return: 'hostname'

    '''

    body1 = Get_hostname(triggerid,*["hostid","host"])
    try:
        return body1[0]['host']
    except KeyError:
        print('Change triggerid to Hostname error.')
        exit(1)

def Combine_Hostname_trigger_value():
    Trig_dict = {}
    Trig_list = Get_Problem_trigger()
    for index,One_trig in enumerate(Trig_list):
        # print(index,"----",One_trig)
        Name_test = 'a'+str(index)
        Trig_dict[Name_test] = {}
        temp = One_trig['triggerid']
        Trig_dict[Name_test]['Des'] = One_trig['description']
        Trig_dict[Name_test]['hostname'] = Change_triggerid_to_Hostname(temp)
        Trig_dict[Name_test]['date'] = Convert_time(One_trig['lastchange'])
    return Trig_dict

def Get_Problem_trigger():
    '''

    :return: a list that incluing some dicts。
    字典有的key为
                triggerid,
                description,
                lastchange,

    '''
    Get_Trig = json.dumps({
        "jsonrpc": "2.0",
        "method": "trigger.get",
        "params": {
            # "templateids" : "10190",
            # "output" : "extend",
            "output":
                [
                    "triggerid",
                    "description",
                    "lastchange"
                ],
            "filter": {
                "value": 1
                # "templateids": 10190,
            },
            "sortfield": "lastchange",
            "sortorder": "DESC"
        },
        "auth": Session,
        "id": 1
    })
    Trig_mid_value = Get_value(Get_Trig)
    Trig_last_value = Process(Trig_mid_value.data)
    return Trig_last_value
def Send_Mess_Chat(message):
    payload = {
        "text": '今天仍未解决的问题',
        "attachments": [{
            "text": message
        }],
        "fallback": 'test2' + "\n" + 'test3',
        "parseUrls": False
    }
    requests.post("https://chat_API", data=json.dumps(payload), headers={"Content-Type": "application/json"})

if __name__ == '__main__':
    login_data = json.dumps(
        {"jsonrpc": "2.0",
         "method": "user.login",
         "params":
             {
                 "user": Zabbix_username,
                 "password": Zabbix_pass,
                 "userData": "false",
             },
         "id": 0
         }).encode('utf-8')
    a = Zabbix_Cusor.request('POST',
                             Zabbix_url,
                             body=login_data,
                             headers=Zabbix_header
                             )
    mmm = a.data.decode('utf-8')
    Session = json.loads(mmm)['result']['sessionid']
    Last_issue = {}
    Last_issue = Combine_Hostname_trigger_value()
    if len(Last_issue) == 0:
        Send_Mess_Chat("没有未解决的问题")
    else:
        The_mess = "今天仍旧没有解决的问题有：\n"
        for i,g in enumerate(Last_issue):
            The_mess = The_mess +"主机：%s\t问题：%s\t问题起始时间：%s\t"%(Last_issue[g]['hostname'],
                                                          Last_issue[g]['Des'],
                                                          Last_issue[g]['date']) + "\n"
        Send_Mess_Chat(The_mess)
