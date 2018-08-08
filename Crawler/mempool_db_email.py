import requests
import json
import time
import datetime
from mailin import Mailin
import sqlite3
import redis
import schedule
import time

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.Redis(connection_pool=pool)
PORT = 8545 # 6060
URL = 'http://localhost:' + str(PORT)
KEYS_DIR = r"/home/auxesis/Documents/Ethereum/PrivateEthr1"
headers = {'Content-type': 'application/json'}
payload = {"jsonrpc": "2.0","id": 1}
m = Mailin("https://api.sendinblue.com/v2.0", "vHmXBYOLTaMIyENj")
db_path = '/home/auxesis/PycharmProjects/cryptowallet/db.sqlite3'

def get_pending_mem_pool_data():

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # GET RPC Data
    payload['method'] = 'eth_getBlockByNumber'
    payload['params'] = ['pending',True]
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    json_data = json.loads(response.text)
    data = json_data['result']

    if 'transactions' in data:
        for tx in data['transactions']:
            txid = tx['hash']
            to_addr = tx['to']
            # Redis Check
            if not txid in r.smembers('eth_vmp_set') and to_addr in r.smembers('eth_aw_set'):
                query = "SELECT from_address,to_address,amount,txid " \
                        "FROM crypto_transaction WHERE txid = '{txid}'".format(txid=txid)
                rows = c.execute(query).fetchall()
                if not rows:
                    from_addr = tx['from']
                    amount = tx['value']
                    confirmation = 0
                    insert_query = "Insert into crypto_transaction(from_address,to_address,amount,txid,confirmation,created_at) values(?,?,?,?,?,?)"
                    insert_cursor = c.execute(insert_query,(from_addr,to_addr,amount,txid,confirmation,datetime.datetime.now()))
                    if insert_cursor.rowcount >= 1:
                        conn.commit()
                        get_name_email_query = "Select username,email from crypto_account where address = '" + str(from_addr) + "'"
                        rows = c.execute(get_name_email_query).fetchall()
                        if rows:
                            name = rows[0][0]
                            email = rows[0][1]
                            content = mail_body_reciever_mempool(name, from_addr, to_addr, str(int(amount,16)), txid)
                            send_email_mempool(email, email, content)
                            content = mail_body_sender_mempool(name, from_addr, to_addr, str(int(amount, 16)), txid)
                            send_email_mempool(email, email, content)
                            print('In Mempool : ' + str(txid))
                            r.sadd('eth_vmp_set', txid)

    conn.close()

def mail_body_reciever_mempool(name,from_addr,to_addr,amount,transaction_id):
    body = 'Dear ' + name + ',<br><br>'
    body += 'Credit is initialized from : ' + str(from_addr) + ' to your account ' + to_addr + ' for an amount(Ether) of : ' + str(amount) + ' <br> '
    body += 'Transaction ID : ' + str(transaction_id) + '<br><br>'
    body += 'Regards,<br>'
    body += 'Auxesis Group'
    return body

def mail_body_sender_mempool(name,from_addr,to_addr,amount,transaction_id):
    body = 'Dear ' + name + ',<br><br>'
    body += 'Debit is initialized from : ' + str(from_addr) + ' your account to : ' + to_addr + ' for an amount(Ether) of : ' + str(amount) + ' <br> '
    body += 'Transaction ID : ' + str(transaction_id) + '<br><br>'
    body += 'Regards,<br>'
    body += 'Auxesis Group'
    return body

def send_email_mempool(email_from,email_to,contnet):
    email_dict = {
                    "to": {email_to:email_to},
                    "from": [email_from],
                    "subject": "Notification | Mempool ",
                    "html": contnet
                }

    m.send_email(email_dict)

try:
    print 'Mempool Start at : ' + str(datetime.datetime.now())
    get_pending_mem_pool_data()
    print 'Mempool Completed at : ' + str(datetime.datetime.now())

except Exception as e:
    print e