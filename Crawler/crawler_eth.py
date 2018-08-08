import requests
import json
import time


PORT = 8548 # 6060
URL = 'http://localhost:' + str(PORT)
KEYS_DIR = r"/home/auxesis/Documents/Ethereum/PrivateEthr1"
headers = {'Content-type': 'application/json'}
payload = {"jsonrpc": "2.0","id": 1}

def get_pending_mem_pool_data():

    pending_data = set()

    payload['method'] = 'eth_getBlockByNumber'
    payload['params'] = ['pending',True]

    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    json_data = json.loads(response.text)

    data = json_data['result']

    if 'transactions' in data:
        for tx in data['transactions']:
            pending_data.add((tx['from'],tx['to']))

    return pending_data

print get_pending_mem_pool_data()