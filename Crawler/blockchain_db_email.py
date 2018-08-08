import requests
import json
import datetime
from mailin import Mailin
import sqlite3
import redis
import schedule
import time
import traceback

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.Redis(connection_pool=pool)
PORT = 8545 # 6060
URL = 'http://localhost:' + str(PORT)
KEYS_DIR = r"/home/auxesis/Documents/Ethereum/PrivateEthr1"
headers = {'Content-type': 'application/json'}
payload = {"jsonrpc": "2.0","id": 1}
m = Mailin("https://api.sendinblue.com/v2.0", "vHmXBYOLTaMIyENj")
db_path = '/home/auxesis/PycharmProjects/cryptowallet/db.sqlite3'
THRESHOLD = 6

def get_pending_mem_pool_data():

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Get Block Number
    payload['method'] = 'eth_blockNumber'
    payload['params'] = []
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    json_data = json.loads(response.text)

    if 'result' in json_data:
        current_block = int(json_data['result'],16)
        if current_block >= int(r.get("eth_blocks_crawled") or 0):

            # Notification for confirm email
            transactions = r.smembers("eth_notification_set") or set()
            for txs in transactions:
                txs = str(txs)
                get_query = "Select confirmation from crypto_transaction where txid = '" + txs + "'"
                data = c.execute(get_query).fetchall()
                if data:
                    confirmations = data[0][0]
                    if confirmations < THRESHOLD:
                        update_query = "Update crypto_transaction set confirmation = confirmation + 1 where txid = '" + txs + "'"
                        c.execute(update_query)
                        conn.commit()
                        print txs + ' : confirmation : ' + str(confirmations) + " : Block Number : " + str(current_block)
                    else:
                        # Send Notification
                        # TODO - get values from db
                        print txs + ' : confirmation : ' + str(confirmations) + " : Block Number : " + str(current_block)
                        name = 'Jitender'
                        email = 'Akash@auxesisgroup.com'
                        content = mail_body_reciever(name, txs,confirmations)
                        send_email_block(email, email, content)
                        r.srem('eth_notification_set', txs)

            end_block = current_block + 1
            for block_number in range(int(r.get("eth_blocks_crawled"))+1,end_block):
                print('Crawling block : ' + str(block_number))
                payload['method'] = 'eth_getBlockByNumber'
                payload['params'] = [hex(block_number),True]
                response = requests.post(URL, data=json.dumps(payload), headers=headers)
                data = json.loads(response.text)

                # TODO - Exception handling
                data = data['result']

                if 'transactions' in data:
                    data = data['transactions']
                    # for to_addr,info in data['transactions'].items():
                    for txs in data:
                        # Check if the transactions is in Redis
                        to_addr = txs['to']
                        tx_id = str(txs['hash'])
                        try :
                            if (to_addr in r.smembers('eth_aw_set')) and (tx_id not in r.smembers('eth_notification_set')):
                                txid = txs['hash']
                                from_addr = txs['from']
                                amount = txs['value']
                                check_query = "select from_address from crypto_transaction WHERE txid = '{txid}'".format(txid=txid)
                                rows = c.execute(check_query).fetchall()
                                # If not in db but in eth_aw_set then it means that it misses the 0th confirmation from mempool script, now we have to send confirmation 0 message
                                if not rows:
                                    insert_query = "Insert into crypto_transaction(from_address,to_address,amount,txid,confirmation,created_at) values(?,?,?,?,?,?)"
                                    insert_cursor = c.execute(insert_query, (
                                    from_addr, to_addr, amount, txid, 0, datetime.datetime.now()))
                                    conn.commit()
                                    print "Missed from mempool " + tx_id + " : Block Number : " + str(block_number)
                                else:
                                    update_query = "Update crypto_transaction set confirmation = confirmation + 1 where txid = '" + tx_id + "'"
                                    c.execute(update_query)
                                    conn.commit()
                                    print tx_id + " : confirmationss : 1 : Block Number : " + str(block_number)
                                r.sadd('eth_notification_set', tx_id)
                                #r.srem('eth_aw_set', to_addr)
                        except Exception as e:
                            print e


                r.set('eth_blocks_crawled', int(r.get('eth_blocks_crawled')) + 1)


    else :
        raise Exception("Some Error Occured : " + json_data['error']['message'])


    conn.close()

def mail_body_reciever(name,transaction_id,confirmations):
    body = 'Dear ' + name + ',<br><br>'
    body += 'You transaction is Completed <br>'
    body += 'Transaction ID : ' + str(transaction_id) + ', with confirmations : ' + str(confirmations) + '<br><br>'
    body += 'Regards,<br>'
    body += 'Auxesis Group'
    return body


def send_email_block(email_from,email_to,contnet):
    email_dict = {
                    "to": {email_to:email_to},
                    "from": [email_from],
                    "subject": "Notification | Blockchain ",
                    "html": contnet
                }

    m.send_email(email_dict)

try:
    print 'Block Start at : ' + str(datetime.datetime.now())
    get_pending_mem_pool_data()
    print 'Block Completed at : ' + str(datetime.datetime.now())

except Exception as e:
    traceback.print_exc()
    print e