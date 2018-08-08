import requests
import json

PORT = 5005
# URL = 'http://localhost:' + str(PORT)
URL = 'https://s.altnet.rippletest.net:51234'
headers = {'Content-type': 'application/json'}
payload = {"jsonrpc": "2.0","id": 1}

def get_account_transcations(account):
    payload['method'] = 'account_tx'
    params = {
        "account": account,
        }
    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)

def sig_xrp(from_address,secret_key,to_address,amount):
    payload['method'] = 'sign'
    params = {
        "offline": False,
        "secret": secret_key,
        "tx_json": {
            "Account": from_address,
            "Amount" : str(amount),
            "Destination": to_address,
            "TransactionType": "Payment",
            "Memos": [
                {
                    "Memo": {
                        "MemoType": "687474703a2f2f6578616d706c652e636f6d2f6d656d6f2f67656e65726963",
                        "MemoData": "1234567"
                    }
                }
            ],
        },
        "fee_mult_max": 1000
    }

    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    print('Payment Init')
    data = json.loads(response.text)
    print(data)
    return data['result']['tx_blob']

def get_transaction_info(hash):
    payload['method'] = 'tx'
    payload['params'] = [{"transaction": hash}]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)

def submit_txs(blob):
    payload['method'] = 'submit'
    payload['params'] = [{'tx_blob':blob}]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    print('Payment Submitted')
    return json.loads(response.text)

def get_account_info(address):
    payload['method'] = 'account_info'
    payload['params'] = [
        {
            "account": address,
            # "ledger_index": "current",
            "strict":True,
            # "queue":True
        }
    ]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)

def get_account_balance(address):
    json_data = get_account_info(address)
    return address + ' : ' + json_data['result']['account_data']['Balance']

def get_transactional_data(account):
    tx_data = get_account_transcations(account=account)['result']['transactions']
    for tx in tx_data:
        tx_info = get_transaction_info(hash=tx['tx']['hash'])
        tx_info_data = tx_info['result']
        result = 'From : ' + tx_info_data['Account'] + ' With Destination Tag : '
        if 'Memos' in tx_info_data:
            result += tx_info_data['Memos'][0]['Memo']['MemoData']
        else:
            result += ' NA'
        print(result)

def cancel_transaction(account,sk,seq_no):
    payload['method'] = 'submit'
    params = {
        "secret": sk,
        "tx_json": {
            "TransactionType": "AccountSet",
            "Account": account,
            "Sequence": seq_no
        }
    }
    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)


ma1 = 'rBKbZSRuyyRc1L9JRReQGkmtBQ23zsP2sx'
ms1 = 'shWZXLAe7wgPrJoCW6sHuP3BLvEVi'
ma2 = 'raahJJ9wqREj5Ns84hzKNhugQDwLGTTwaY'
ms2 = 'shgd31wuupZ3GMykfxVBvYPg7PwS2'


# print get_account_balance(ma1)
# print get_account_balance(ma2)
# print('-'*100)
# blob = sig_xrp(ma1,ms1,ma2,10)
# # print(blob)
# print(get_account_info(ma1))
# print(get_account_info(ma2))
# print(submit_txs(blob))
# print(get_account_info(ma1))
# print(get_account_info(ma2))
# print('-'*100)
# print get_account_balance(ma1)
# print get_account_balance(ma2)
# print('-'*100)
hash = 'F1A61BC3BEF52B8C363CA5010B3A2E1EBFC5E66E08CB0979553C46821166F4C9'
print(get_transaction_info(hash=hash))
