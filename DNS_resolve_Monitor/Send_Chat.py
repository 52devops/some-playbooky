import requests, json
def Send_Mess_Chat(message, text):
    payload = {
        "text": text,
        "attachments": [{
            "text": message
        }],
        "fallback": 'test2' + "\n" + 'test3',
        "parseUrls": False
    }
    requests.post("xxxxxxxxxxx", data=json.dumps(payload), headers={"Content-Type": "application/json"})
