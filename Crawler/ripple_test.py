import requests
import json

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

def server_info():
    payload['method'] = 'server_info'
    payload['params'] = []
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)

def get_account_info(address):
    payload['method'] = 'account_info'
    payload['params'] = [{ "account": address }]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)

def account_currencies(address):
    payload['method'] = 'account_currencies'
    payload['params'] = [{ "account": address }]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)

def sig_xrp(from_address,secret_key,to_address,amount,currency):
    payload['method'] = 'sign'
    params = {
        "offline": False,
        "secret": secret_key,
        "tx_json": {
            "Account": from_address,
            "Amount" : str(amount),
            "Destination": to_address,
            "TransactionType": "Payment"
        },
        "fee_mult_max": 1000
    }

    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    print('Payment Init')
    data = json.loads(response.text)
    print(data)
    return data['result']['tx_blob']

def sign_payments(from_address,secret_key,to_address,amount,currency):

    payload['method'] = 'sign'
    params = {
        "offline": False,
        "secret": secret_key,
        "tx_json": {
            "Account": from_address,
            "Amount": {
                "currency": currency,
                "issuer": from_address,
                "value": str(amount)
            },
            "Destination": to_address,
            "TransactionType": "Payment"
        },
        "fee_mult_max": 1000,
        "Paths" : []
    }

    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    print('Payment Init')
    return json.loads(response.text)['result']['tx_blob']

def get_account_balance(address):
    json_data = get_account_info(address)
    # Check if account is valid
    status = json_data.get('result',{}).get('status','')
    if status == 'success':
        return json_data.get('result',{}).get('account_data',{}).get('Balance',0)
    else:
        return -1


def get_transaction_info(hash):
    payload['method'] = 'tx'
    payload['params'] = [{"transaction": hash}]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)

def create_new_account():
    payload['method'] = 'wallet_propose'
    payload['params'] = []
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)

def submit_txs(blob):
    payload['method'] = 'submit'
    payload['params'] = [{'tx_blob':blob}]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    print('Payment Submitted')
    return json.loads(response.text)

def account_currencies(address):
    payload['method'] = 'account_currencies'
    params = {
            "account": address,
            "account_index": 0,
            "ledger_index": "validated",
            "strict": True
        }
    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)

def get_fee():
    payload['method'] = 'fee'
    payload['params'] = []
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)

def enable_master_key():
    payload['method'] = 'submit'
    params = {
        "secret": "snoPBrXtMeMyMHUVTgbuqAfg1SUTb",
        "tx_json": {
            "TransactionType": "AccountSet",
            "Account": "rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh",
            "ClearFlag": 4
        }
    }
    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)

# TODO
def get_paths(from_addr,to_addr,value,dest_currency):
    payload['method'] = 'ripple_path_find'
    params = {
            "destination_account": to_addr,
            "destination_amount": {
                "currency": dest_currency,
                "issuer": from_addr,
                "value": str(value)
            },
            "source_account": to_addr,
            "source_currencies": [
                {
                    "currency": "XRP"
                },
                {
                    "currency": "USD"
                }
            ]
        }

    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)

def create_multi_sign_account(ms_acc_id,sk,quoram,signer_entries):
    payload['method'] = 'submit'
    signer_ent = []
    for se in signer_entries:
        signer_ent.append(
            {
                "SignerEntry":{
                    "Account" : se[0],
                    "SignerWeight" : se[1]

                }
            }
        )

    params = {
        "secret" : sk,
        'tx_json':{
            "Flags": 0,
            "TransactionType": "SignerListSet",
            "Account": ms_acc_id,
            "Fee": "12",
            "SignerQuorum": quoram,
            "SignerEntries": signer_ent
        }
    }
    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)

def account_objects(account):
    payload['method'] = 'account_objects'
    params = {
            "account": account,
            "ledger_index": "validated",
        }
    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)

def multi_sign_init(account,sk,multi_sign_acc,to_acct,amount,sequence,signers = []):
    payload['method'] = 'sign_for'
    # params = {
    #     "offline" : False,
    #     "account": account,
    #     "secret": sk,
    #     "tx_json":{
    #         "TransactionType": "Payment",
    #         "Account": multi_sign_acc,
    #         "Destination" : to_acct,
    #         "Flags": 262144,
    #         "Amount" : str(amount),
    #         # "LimitAmount": {
    #         #     "currency": "USD",
    #         #     "issuer" :to_acct,
    #         #     "value":str(amount)
    #         # },
    #         "Sequence": sequence,
    #         "Signers" : signers,
    #         "SigningPubKey": "",
    #         "Fee": "30000"
    #     }
    # }

    params = {
        "offline": False,
        "account": account,
        "secret": sk,
        "tx_json": {
            "Account": multi_sign_acc,
            "Flags": 2147483648,
            "Sequence": sequence,
            "Fee": "30000",
            "TransactionType": "Payment",
            "Destination": to_acct,
            "Amount": str(amount),
            "SigningPubKey": "",
            "Signers": signers,
        },
    }

    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    data = json.loads(response.text)
    print(data)
    return data['result']['tx_json']['Signers'],data['result']['tx_json'],data['result']['tx_blob']

def submit_multi_signed(tx_json):
    payload['method'] = 'submit_multisigned'
    params = {
        "tx_json" : tx_json
    }
    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    data = json.loads(response.text)
    return data,data['result']['tx_json']['hash']

def get_fee():
    payload['method'] = 'fee'
    payload['params'] = []
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    data_json = json.loads(response.text)
    if response.status_code == 200 :
        result = json.loads(response.text)['result']
        return result['drops']['base_fee']
    else:
        raise Exception('Unable to get fee')

def get_ledger_transactions(index):
    payload['method'] = 'ledger'
    params = {
        "ledger_index": index,
        "transactions": True,
        "expand": True
    }
    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    try:
        transactions_data = json.loads(response.text)['result']['ledger']['transactions']
    except:
        raise Exception('Transaction Data not found')
    return transactions_data



# print(get_ledger_transactions(11326014))

# print get_fee()

# print(get_transaction_info('F1D781A173C57FDEC6AB7B6A0BC810EDE89D67A9364A8F7A8AA2678C36D1F047'))
# print(get_account_info('rBKbZSRuyyRc1L9JRReQGkmtBQ23zsP2sx'))
# print(get_account_balance('rDUoc5LePtDy1RGfvJDYZrQfLjQigvzaiy'))
# print(get_account_balance('rBKbZSRuyyRc1L9JRReQGkmtBQ23zsP2sx'))
# print('-'*100)
# blob = sig_xrp(
#     from_address='rBKbZSRuyyRc1L9JRReQGkmtBQ23zsP2sx',
#     secret_key='shWZXLAe7wgPrJoCW6sHuP3BLvEVi',
#     to_address='raahJJ9wqREj5Ns84hzKNhugQDwLGTTwaY',
#     amount=10,
#     currency='XRP')
# print('-'*100)
# print(get_account_balance('rBKbZSRuyyRc1L9JRReQGkmtBQ23zsP2sx'))
# print('-'*100)
# print(submit_txs(blob))
# print('-'*100)
# print(get_account_balance('rBKbZSRuyyRc1L9JRReQGkmtBQ23zsP2sx'))

# Multi Sign key
# ma1 = 'rBKbZSRuyyRc1L9JRReQGkmtBQ23zsP2sx'
# ms1 = 'shWZXLAe7wgPrJoCW6sHuP3BLvEVi'
# ma2 = 'raahJJ9wqREj5Ns84hzKNhugQDwLGTTwaY'
# ms2 = 'shgd31wuupZ3GMykfxVBvYPg7PwS2'
# ma3 = 'rpN5MV56k2TZkccTorgp8ybZChyLGTFrSB'
# ms3 = 'spx5U1mfqQJMbiB4pZRxhdzovdrrX'
# ms_acc_id = 'rEGqxJWNU1YtSmrNjZn7JUxmXFiRhz2ffB'
# ms_acc_sk = 'ssnN6nfb1DKHMS9ADvydHxKxm4nJ5'
# ms_rec_add = 'rUAfaEymfQKjYSTvCV7vJSwft9htKRqDaL'
# ms_rec_key = 'sh2CG2N4WCyN1bZeQ6wk5hmCniHLv'
# amount = 10
#
# js_acc = 'rGQtiaRAMMEZQpyeUg6bYHF4tSMqE4sBAk'
# js_sk = 'shNGcN8HX38UBWij9HP9XkFj7sjyu'
#
# print(get_account_balance(js_acc))
# print(get_account_balance(ma1))
# print('-'*100)
# blob = sig_xrp(
#     from_address=js_acc,
#     secret_key=js_sk,
#     to_address=ma1,
#     amount=90,
#     currency='XRP')
# print(submit_txs(blob))
# print('-'*100)
# print(get_account_balance(js_acc))
# print(get_account_balance(ma1))



### Multisig
# tx_data = get_account_transcations(account=ma2)['result']['transactions']
# for tx in tx_data:
#     print(get_transaction_info(hash=tx['tx']['hash']))
# print(get_transaction_info(hash='1178ABF2AE71F3E497ECCB4D808AAEBAFFA52928299CC67F01814B81BB3E4371'))
# acc_data = get_account_info(ms_acc_id)
# print(acc_data)
# sequence = acc_data['result']['account_data']['Sequence']
# print(sequence)
# print(get_account_balance(ms_acc_id))
# print(get_account_balance(ms_rec_add))
# print('-'*100)
# sign1,tx_json1,blob1 = multi_sign_init(account=ma1,sk=ms1,multi_sign_acc=ms_acc_id,to_acct=ms_rec_add,amount=amount,sequence=sequence)
# # print(sign1)
# print(tx_json1)
# print('-'*100)
# sign2,tx_json2,blob2 = multi_sign_init(account=ma2,sk=ms2,multi_sign_acc=ms_acc_id,to_acct=ms_rec_add,amount=amount,signers=sign1,sequence=sequence)
# # print(sign2)
# print(tx_json2)
# print('-'*100)
# sign3,tx_json3,blob3 = multi_sign_init(account=ma3,sk=ms3,multi_sign_acc=ms_acc_id,to_acct=ms_rec_add,amount=amount,signers=sign2,sequence=sequence)
# # print(sign3)
# print(tx_json3)
# print(blob3)
# print('-'*100)
# # tx_json,hash = submit_multi_signed(tx_json=tx_json3)
# print(submit_txs(blob=blob3))
# # print(tx_json)
# # print(hash)
# print('-'*100)
# print(get_account_balance(ms_acc_id))
# print(get_account_balance(ms_rec_add))
# print('-'*100)
# print(get_transaction_info(hash=hash))
# acc_data = get_account_info(ms_acc_id)
# print(acc_data)
# sequence = acc_data['result']['account_data']['Sequence']
# print(sequence)

# print(account_objects(ms_acc_id))
# print(create_multi_sign_account(ms_acc_id = ms_acc_id,sk=ms_acc_sk,quoram = 3,signer_entries = [[ma1,2],[ma2,1],[ma3,1]]))
# print(account_objects(ms_acc_id))
# acc1 = 'rHhruopyBrznqe6RuUywCCTQXWgVZMQRJS'
# acc2 = 'rBi4xANDhY9yAaLz676n9YEcg4S5FVZQH3'
# p_acc = 'aB4AUpwFPbTZDDHetMBAc2vnXLZFqy5SACatw4mFGcjw96auRit8'
# acc_id = 'rnnjcb4QtUFDwrTFU96j419tduTsngsVt2'
# seed='snbQAqeRozcE4NCYDHkK1GBAucnmw'
#
# master_acc = 'rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh'
# master_acc = 'rBmVUQNF6tJy4cLvoKdPXb4BNqKBk5JY1Y'
# master_seed = 'snoPBrXtMeMyMHUVTgbuqAfg1SUTb'
#
# print(get_account_info(master_acc))
#
# # print(create_new_account())
#
# # p_acc1 = 'aBRky9fh43ArFNkMee2BattymrZG798HjFr4eaeYkb6UGAPi5qWp'
# blob = sig_xrp(
#     from_address=acc1,
#     secret_key='sneGWXGHi8h3jD3VukRhJ5Gxqxk1H',
#     to_address=ms_acc_id,
#     amount=1000000,
#     currency='XRP')
# print(submit_txs(blob))
# #
# # blob = sign_payments(
# #     from_address=acc1,
# #     secret_key='sneGWXGHi8h3jD3VukRhJ5Gxqxk1H',
# #     to_address=acc2,
# #     amount=100,
# #     currency='USD')
# # print(submit_txs(blob))
# #
# # print('Balance')
# # print(get_account_balance(acc1))
# # print(get_account_balance(acc2))
#
# # XRP TO XRP required no path
# # blob = sig_xrp(
# #     from_address=acc1,
# #     secret_key='sneGWXGHi8h3jD3VukRhJ5Gxqxk1H',
# #     to_address=acc2,
# #     amount=58,
# #     currency='XRP')
# # print(submit_txs(blob))
