import requests
import json

headers = {'content-type': 'application/json'}
URL = 'http://127.0.0.1:8001/notification_rec/receive_notification/'

data = {
    'app_key' : '123456',
    'app_secret' : 'abcdef',
    'amount' : 20,
    'from_address' : 'svsodaichdsASDSAaSCACSA213asd5SAD',
    'destination_tag' : 123456
}
params = {'sessionKey': '9ebbd0b25760557393a43064a92bae539d962103', 'format': 'xml', 'platformId': 1}
response = requests.post(URL, data=json.dumps(data),headers=headers,params=params)
print json.loads(response.text)
print(response.status_code)