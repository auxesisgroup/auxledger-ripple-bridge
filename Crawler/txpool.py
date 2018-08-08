# -*- coding: utf-8 -*-
import requests
import json
import time


PORT = 8544 # 6060
URL = 'http://localhost:' + str(PORT)
KEYS_DIR = r"/home/auxesis/Documents/Ethereum/PrivateEthr1"
headers = {'Content-type': 'application/json'}
payload = {"jsonrpc": "2.0","id": 1}


def get_pending_mem_pool_data(type):

    pending_data = set()

    payload['method'] = 'txpool_content'
    payload['params'] = []

    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    json_data = json.loads(response.text)

    data = json_data['result']
    pending_transaction = data[type]

    if pending_transaction:
        for key,value in pending_transaction.items():
            from_addr = key
            for tx_num,tx_data in value.items():
                to_addr = tx_data['to']
                pending_data.add((from_addr,to_addr))

    return pending_data


def send_email_pending_transactions(pending_data):
    pass


def send_email(addr,msg):
    pass


pending_data = get_pending_mem_pool_data('pending')
for d in pending_data:
    print d
