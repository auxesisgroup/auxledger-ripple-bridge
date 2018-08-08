import requests
import json
import time

# URL = 'https://s.altnet.rippletest.net:51234'
# URL = 'http://127.0.0.1:5005'

# proxies = {'http': 'http://root:Ripple.node@123@167.99.228.1:5005', 'https': 'http://rootRipple.node@123@167.99.228.1:5005'}
URL = 'http://167.99.228.1:5005'
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


def wallet_propose():
    payload['method'] = 'wallet_propose'
    params = {}
    payload['params'] = [params]
    print 'rpc..'
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)



def get_account_info(address):
    payload['method'] = 'account_info'
    payload['params'] = [{ "account": address }]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)

def get_account_balance(address):
    json_data = get_account_info(address)
    # Check if account is valid
    status = json_data.get('result',{}).get('status','')
    if status == 'success':
        print(json_data['result']['account_data']['Sequence'])
        return json_data.get('result',{}).get('account_data',{}).get('Balance',0)
    else:
        return -1

def submit_txs(blob):
    payload['method'] = 'submit'
    payload['params'] = [{'tx_blob':blob}]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    print('Payment Submitted')
    print(json.loads(response.text))
    return json.loads(response.text)['result']['tx_json']['hash']

def sig_xrp(from_address,secret_key,to_address,amount):
    payload['method'] = 'sign'
    params = {
        "offline": False,
        "secret": secret_key,
        "tx_json": {
            "Account": from_address,
            "Amount" : str(amount),
            "Destination": to_address,
            "DestinationTag": 123456,
            "TransactionType": "Payment"
        },
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


print(wallet_propose())

#
# acc1 = 'rEJLSVCUViUCSNhjAoamHpU4BUpXh5XZZd'
# sk1 = 'shuSyH1S7YBwNedmu4JepaH3ibDGQ'
#
# acc2 = 'rQwQkfw9PtgRZjXTNeGaJQLc1yHA6WLScF'
# sk2 = 'ssohg38haz6MuKRSgXCCVVtSpQvEX'
#
# # print(get_transaction_info('AC33D339DDDCD54F7C2F566C2B45C61E90A401025152E036AF396D873724767D'))
#
# # Success
# print(get_account_balance(acc1))
# print(get_account_balance(acc2))
# print('Signing :')
# blob = sig_xrp(acc1,sk1,acc2,30000000)
# print('Submitting :')
# hash = submit_txs(blob)
# print('Ledger :')
# time.sleep(5)
# print(get_transaction_info(hash))
# print(get_account_balance(acc1))
# print(get_account_balance(acc2))

# Insufficient Funds
# print(get_account_balance(acc1))
# print(get_account_balance(acc2))
# print('Signing :')
# blob = sig_xrp(acc1,sk1,acc2,1000000000000000)
# print('Submitting :')
# hash = submit_txs(blob)
# print('Ledger :')
# time.sleep(5)
# print(get_transaction_info(hash))
# print(get_account_balance(acc1))
# print(get_account_balance(acc2))

# Wrong Signature
# print(get_account_balance(acc1))
# print(get_account_balance(acc2))
# print('Signing :')
# blob = sig_xrp(acc1,sk2,acc2,50)
# print('Submitting :')
# hash = submit_txs(blob)
# print('Ledger :')
# time.sleep(5)
# print(get_transaction_info(hash))
# print(get_account_balance(acc1))
# print(get_account_balance(acc2))

# Sequence
# print(get_account_balance(acc1))
# print(get_account_balance(acc2))
# print('Signing :')
# blob = sig_xrp(acc1,sk1,acc2,50)
# print('Submitting :')
# hash = submit_txs(blob)
# print('Ledger :')
# time.sleep(5)
# print(get_transaction_info(hash))
# print(get_account_balance(acc1))
# print(get_account_balance(acc2))


# Destination doesnot exist
# acc2 = 'rD9JBoAM5h4o5kGDjDeMVsXpqwTXC3imU7'
# sk2 = 'sh1wxsmyv6Y1HFuGcr7irVFYBhBHs'
# print(get_account_balance(acc1))
# print(get_account_balance(acc2))
# print('Signing :')
# blob = sig_xrp(acc1,sk1,acc2,50)
# print('Submitting :')
# hash = submit_txs(blob)
# print('Ledger :')
# time.sleep(5)
# print(get_transaction_info(hash))
# print(get_account_balance(acc1))
# print(get_account_balance(acc2))


# Sending to self
# print(get_account_balance(acc1))
# print(get_account_balance(acc2))
# print('Signing :')
# blob = sig_xrp(acc1,sk1,acc1,50)
# print('Submitting :')
# hash = submit_txs(blob)
# print('Ledger :')
# time.sleep(5)
# print(get_transaction_info(hash))
# print(get_account_balance(acc1))
# print(get_account_balance(acc2))

# Format
# acc1 = 'REJLSVCUViUCSNhjAoamHpU4BUpXh5XZ24'
# print(get_account_balance(acc1))
# print(get_account_balance(acc2))
# print('Signing :')
# blob = sig_xrp(acc1,sk1,acc2,50)
# print('Submitting :')
# hash = submit_txs(blob)
# print('Ledger :')
# time.sleep(5)
# print(get_transaction_info(hash))
# print(get_account_balance(acc1))
# print(get_account_balance(acc2))
