import requests
import json

address = 'http://127.0.0.1:'
port = 8080
URL =  address + str(port)

method = URL + '/get_account_data'
get = requests.get(method)  # GET request
data = get.json()
print(data)
# # process this JSON data and do something with it
# print(data)


# seed_data = {'seed' : '123456'}
# response = requests.post('http://127.0.0.1:8080/get_keys', data=json.dumps(seed_data))
# print json.loads(response.text)