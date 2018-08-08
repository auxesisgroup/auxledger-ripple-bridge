import requests
import json


PORT = 8545
URL = 'http://localhost:' + str(PORT)
headers = {'Content-type': 'application/json'}
payload = {"jsonrpc": "2.0","id": 1}


payload['method'] = 'eth_getBlockByNumber'
payload['params'] = [hex(3693493),True]
response = requests.post(URL, data=json.dumps(payload), headers=headers)
json_data = json.loads(response.text)

print(json_data)