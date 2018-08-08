import requests
import json
import redis
import datetime
import logging

PORT = 5005
# URL = 'http://localhost:' + str(PORT)
URL = 'https://s.altnet.rippletest.net:51234'
headers = {'Content-type': 'application/json'}
payload = {"jsonrpc": "2.0","id": 1}
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.Redis(connection_pool=pool)
THRESHOLD = 6
log_path = '/home/auxesis/Documents/RIpple/Logs/log_test.log'

def my_logger(log_path):
    logging.basicConfig(filename=log_path,
                        format='%(asctime)s %(message)s',
                        filemode='w')
    handlers = [logging.FileHandler(log_path), logging.StreamHandler()]
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers = handlers
    return logger

def ledger_closed():
    payload['method'] = 'ledger_closed'
    params = {}
    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)['result']['ledger_index']

def ledger_current():
    payload['method'] = 'ledger_current'
    params = {}
    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)['result']['ledger_current_index']

def ledger_data(index):
    payload['method'] = 'ledger_data'
    params = {
        "ledger_hash": index,
    }
    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)

def ledger_entry(account,ledger_index):
    payload['method'] = 'ledger_entry'
    params = {
            "account" : account,
            "ledger_hash": ledger_index,
            "type": "account_root"
        }
    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)

def ledger(index):
    payload['method'] = 'ledger'
    params = {
        "ledger_index" : index,
    }
    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)

def get_ledger_hash(index):
    payload['method'] = 'ledger'
    params = {
        "ledger_index": index,
    }
    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    return json.loads(response.text)['result']['ledger_hash']

def get_ledger_validated_index():
    payload['method'] = 'ledger'
    params = {
                "ledger_index": "validated"
        }
    payload['params'] = [params]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    json_res = json.loads(response.text)
    try:
        index = json_res['result']['ledger']['ledger_index']
    except:
        raise Exception('validated_ledger_index not found')
    return index

def get_ledger_transactions_data(index):
    tx_data = get_ledger_transactions(index)
    for tx in tx_data:
        print("Account from : " + tx['Account'] + " to : " + tx['Destination'] + " Amount : " + tx['Amount'] + " in ledger : " +  str(index))

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

# TODO
def get_confirmation_number(transaction):
    pass

# TODO
def update_confirmation_number(transaction):
    pass

# TODO
def send_notification():
    pass

# TODO
def check_transcation_present_in_db(transaction):
    pass

# TODO
def insert_in_db(from_addr,to_addr,tx_hash,ledger_index,amount,confirmation,timestamp):
    pass

def crawler_process():
    current_validated_ledger_index = get_ledger_validated_index()

    if current_validated_ledger_index:
        if current_validated_ledger_index >= int(r.get("xrp_ledger_crawled") or 0):
            transactions_set = r.smembers("xrp_notification_set") or set()

            # Updating confirmations
            for transaction in transactions_set:
                transaction = str(transaction)
                confirmations = get_confirmation_number(transaction)

                if confirmations >= THRESHOLD:
                    send_notification()
                    r.srem('xrp_notification_set', transaction)
                else:
                    update_confirmation_number(transaction)
                    print(transaction + ' : confirmation : ' + str(confirmations) + " : Ledger Number : " + str(current_validated_ledger_index))

            # Crawling Ledgers
            for ledger_number in range(int(r.get("xrp_ledger_crawled")) + 1, current_validated_ledger_index + 1):
                print('Crawling Ledger : ' + str(ledger_number))
                transactions_list = get_ledger_transactions(ledger_number)

                for transaction_data in transactions_list:
                    to_address = transaction_data['Destination']
                    tx_hash = str(transaction_data['hash'])
                    transactions_set = r.smembers("xrp_notification_set") or set()

                    if (to_address in r.smembers('xrp_aw_set')) and (tx_hash not in transactions_set):
                        if not check_transcation_present_in_db(tx_hash):
                            from_address = transaction_data['Account']
                            amount = transaction_data['Amount']
                            timestamp = datetime.datetime.now()
                            confirmations = 0
                            insert_in_db(from_addr=from_address,to_addr=to_address,tx_hash=tx_hash,ledger_index=ledger_number,amount=amount,confirmations=confirmations,timestamp=timestamp)
                            print("Missed from mempool " + tx_hash + " : ledger Number : " + str(ledger_number))
                        else:
                            update_confirmation_number(tx_hash)
                            print(tx_hash + " : confirmations : 1 : ledger Number : " + str(ledger_number))
                        r.sadd('xrp_notification_set', tx_hash)
            r.set('xrp_ledger_crawled', int(r.get('xrp_ledger_crawled')) + 1)

try:
    crawler_process()
except Exception as e:
    print e


# ma1 = 'rBKbZSRuyyRc1L9JRReQGkmtBQ23zsP2sx'
# ms1 = 'shWZXLAe7wgPrJoCW6sHuP3BLvEVi'
# ma2 = 'raahJJ9wqREj5Ns84hzKNhugQDwLGTTwaY'
# ms2 = 'shgd31wuupZ3GMykfxVBvYPg7PwS2'
# print("ledger_current : " + str(ledger_current()))
# print("ledger_closed : " + str(ledger_closed()))
# print("ledger_validated: " + str(ledger_validated()))
# print("ledger_current : " + str(ledger_current()))
# print("ledger_closed : " + str(ledger_closed()))
# print("ledger_validated: " + str(ledger_validated()))
# print(ledger_data(index=11178310))
# print(ledger_entry(ma2,"validated"))
# get_ledger_data(11178310)
# print(ledger_data(ldgr_hash))
# print(ledger_entry(ma2,ldgr_hash))
# F1A61BC3BEF52B8C363CA5010B3A2E1EBFC5E66E08CB0979553C46821166F4C9

