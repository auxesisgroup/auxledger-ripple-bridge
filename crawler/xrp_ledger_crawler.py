import requests
import json
import redis
from apscheduler.schedulers.blocking import BlockingScheduler
import MySQLdb
import datetime
import logging

# Testing
URL = 'http://167.99.228.1:5005'
headers = {'Content-type': 'application/json'}
payload = {"jsonrpc": "2.0","id": 1}
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.Redis(connection_pool=pool)
logger, db = None, None


def init_logger():
    global logger
    log_path = '/var/log/xrp_logs/crawler_logs/ledger_%s.log' % (str(datetime.date.today()).replace('-', '_'))
    handlers = [logging.FileHandler(log_path), logging.StreamHandler()]
    logging.basicConfig(filename=log_path, format='%(asctime)s %(message)s', filemode='a')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers = handlers


def get_db_connect():
    try:
        db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                         user="root",         # your username
                         passwd="Ripple.test#123",  # your password
                         db="test_xrp_auxpay")
        return db
    except Exception as e:
        logger.info("Error get_db_connect : " + str(e))
        raise Exception(str(e))


def get_account_info(address):
    try:
        payload['method'] = 'account_info'
        payload['params'] = [{ "account": address }]
        response = requests.post(URL, data=json.dumps(payload), headers=headers)
        return json.loads(response.text)
    except Exception as e:
        logger.info("Error get_account_info : " + str(e))


def get_account_balance(address):
    json_data = get_account_info(address)
    # Check if account is valid
    status = json_data.get('result',{}).get('status','')
    if status == 'success':
        return json_data.get('result',{}).get('account_data',{}).get('Balance',0)
    else:
        return 0


def get_ledger_validated_index():
    try:
        payload['method'] = 'ledger'
        params = {
                    "ledger_index": "validated"
            }
        payload['params'] = [params]
        response = requests.post(URL, data=json.dumps(payload), headers=headers)
        json_res = json.loads(response.text)
        index = int(json_res.get('result',{}).get('ledger',{}).get('ledger_index',0))
        return index
    except Exception as e:
        logger.info("Error get_ledger_validated_index : " + str(e))


def get_ledger_transactions(index):
    try:
        payload['method'] = 'ledger'
        params = {
            "ledger_index": index,
            "transactions": True,
            "expand": True
        }
        payload['params'] = [params]
        response = requests.post(URL, data=json.dumps(payload), headers=headers)
        transactions_data = json.loads(response.text).get('result',{}).get('ledger',{}).get('transactions',[])
        return transactions_data
    except Exception as e:
        logger.info("Error get_ledger_transactions : " + str(e))


def get_notification_url(address):
    try :
        cursor = db.cursor()
        query = "Select notification_url,app_key,app_secret" \
                " from aux_ripp_address_master a INNER JOIN aux_ripp_user_master u" \
                " ON a.user_name = u.user_name"\
                " where a.address = '" + str(address) + "'"
        cursor.execute(query)
        rows = cursor.fetchall()
        if len(rows) == 1:
            return True,rows[0][0],rows[0][1],rows[0][2]
        else:
            return False,None,None,None

    except Exception as e:
        logger.info('Error get_notification_url : ' + str(e))


def send_notification(to_address,from_address,destination_tag,amount,ledger_number,transaction_hash, status):
    try:
        result,notification_url,app_key,app_secret = get_notification_url(to_address)
        if result:
            data = {
                'app_key': app_key,
                'app_secret': app_secret,
                'from_address': from_address,
                'to_address' : to_address,
                'destination_tag': destination_tag,
                'amount': amount,
                'ledger_number' : ledger_number,
                'transaction_hash' : transaction_hash,
                'status' : status
            }
            response = requests.post(notification_url, data=json.dumps(data), headers=headers)
            logger.info(json.loads(response.text))
    except Exception as e:
        logger.info('Error send_success_notification : ' + str(e))


def validate_transaction(tx_result):
    return tx_result == 'tesSUCCESS'


def update_active_status(address,status = True):
    try:
        cursor = db.cursor()
        update_query = "Update aux_ripp_address_master set is_active = " + str(status) + \
                       " where address = '" + address + "'"

        cursor.execute(update_query)
        db.commit()
    except Exception as e:
        logger.info('Error update_active_status :' + str(e))


def insert_transaction(from_address, to_address, amount, txid, sequence, ledger, created, destination_tag, status):
    try:
        cursor = db.cursor()
        insert_query = 'Insert into aux_ripp_transaction_master' \
                       ' (from_address,to_address,amount,txid,sequence,ledger_index,created_at,bid_id,status)' \
                       ' values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'

        cursor.execute(insert_query, (from_address, to_address, amount, txid, sequence, ledger, created, destination_tag, status))
        db.commit()
    except Exception as e:
        logger.info('Error insert_transaction : ' + str(e))


def reciver_crawler():
    try :
        global db

        init_logger()

        # Redis
        job_id = str(r.get("xrp_job_id") or 0)
        logger.info(' Job ID : ' + job_id)
        r.set('xrp_job_id', int(r.get('xrp_job_id') or 0) + 1)

        db = get_db_connect()
        current_validated_ledger_index = get_ledger_validated_index()

        if current_validated_ledger_index:
            if current_validated_ledger_index >= int(r.get("xrp_ledger_crawled") or 0):
                # Crawling Ledgers
                for ledger_number in range(int(r.get("xrp_ledger_crawled") or 0) + 1, current_validated_ledger_index + 1):
                    logger.info('-' * 100)
                    transactions_list = get_ledger_transactions(ledger_number)
                    logger.info('Crawling Ledger : ' + str(ledger_number) + " , Validated : " + str(current_validated_ledger_index))
                    for transaction_data in transactions_list:
                        to_address = transaction_data.get('Destination','')
                        if (to_address in r.smembers('xrp_aw_set')):
                            tx_hash = str(transaction_data['hash'])
                            if (tx_hash not in r.smembers("xrp_notification_set") or set()):

                                # Destination_Tag
                                logger.info('Found : ' + str(to_address) + ' hash : ' + str(tx_hash))

                                # Check if valid
                                tx_result = transaction_data.get('metaData',{}).get('TransactionResult','')

                                balance = get_account_balance(to_address)
                                if balance:
                                    update_active_status(to_address)

                                if validate_transaction(tx_result):
                                    status = 'Success'
                                else:
                                    status = 'Failure'

                                from_address = transaction_data.get('Account','')
                                amount = transaction_data.get('Amount','')
                                destination_tag = transaction_data.get('DestinationTag','')
                                sequence = transaction_data.get('Sequence','')
                                created = datetime.datetime.now()

                                insert_transaction(from_address, to_address, amount, tx_hash, sequence, ledger_number,created, destination_tag,status)
                                send_notification(to_address, from_address, destination_tag, amount,ledger_number, tx_hash, status)
                                r.sadd('xrp_notification_set', tx_hash)

                    logger.info('-'*100)
                    r.set('xrp_ledger_crawled', int(r.get('xrp_ledger_crawled') or 0) + 1)
    except Exception as e:
        logger.info('Error in job : ' + str(job_id) + ' : ' + str(e))
    finally:
        if db :
            db.close()


try:
    sched = BlockingScheduler(timezone='Asia/Kolkata')
    sched.add_job(reciver_crawler, 'interval', id='my_job_id', seconds=10)
    sched.start()
except Exception as e:
    logger.info('Error : ' + str(e))
