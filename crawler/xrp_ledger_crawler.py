import requests
import json
import redis
from apscheduler.schedulers.blocking import BlockingScheduler
import MySQLdb
import datetime
import logging
import ConfigParser

# Init Parser
parser = ConfigParser.RawConfigParser()

# Node Connection
xrp_node_conf_path = r'/var/xrp_config/xrp_node.ini'
parser.read(xrp_node_conf_path)
URL = parser.get('ripple_node', 'url')

# Redis Connection
xrp_redis_conf_path = r'/var/xrp_config/xrp_redis.ini'
parser.read(xrp_redis_conf_path)
pool = redis.ConnectionPool(host=parser.get('redis', 'host'), port=int(parser.get('redis', 'port')), db=int(parser.get('redis', 'db')))
r = redis.Redis(connection_pool=pool)

# Reference
headers = {'Content-type': 'application/json'}
payload = {"jsonrpc": "2.0","id": 1}
logger, db = None, None


def init_logger():
    """
    Initialization of log object
    :return:
    """
    try:
        global logger
        log_path = '/var/log/xrp_logs/crawler_logs/ledger_%s.log' % (str(datetime.date.today()).replace('-', '_'))
        handlers = [logging.FileHandler(log_path), logging.StreamHandler()]
        logging.basicConfig(filename=log_path, format='%(asctime)s %(message)s', filemode='a')
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.handlers = handlers
        return True
    except:
        return False


def get_db_connect():
    """
    MySQL Connection
    :return:
    """
    try:
        xrp_auxpay_conf_path = r'/var/xrp_config/xrp_auxpay_db.ini'
        parser.read(xrp_auxpay_conf_path)
        db = MySQLdb.connect(host=parser.get('db', 'host'),
                         user=parser.get('db', 'user'),
                         passwd=parser.get('db', 'password'),
                         db=parser.get('db', 'db_name'))
        return db
    except Exception as e:
        logger.info("Error get_db_connect : " + str(e))
        raise Exception(str(e))


def get_account_info(address):
    """
    RPC for getting account info
    :param address:
    :return:
    """
    try:
        payload['method'] = 'account_info'
        payload['params'] = [{ "account": address }]
        response = requests.post(URL, data=json.dumps(payload), headers=headers)
        return json.loads(response.text)
    except Exception as e:
        logger.info("Error get_account_info : " + str(e))


def get_account_balance(address):
    """
    Get account balance from get_account_info
    :param address:
    :return:
    """
    json_data = get_account_info(address)
    # Check if account is valid
    status = json_data.get('result',{}).get('status','')
    if status == 'success':
        return json_data.get('result',{}).get('account_data',{}).get('Balance',0)
    else:
        return 0


def get_ledger_validated_index():
    """
    RPC for getting the latest validated ledger
    :return:
    """
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
    """
    RPC for reading ledger data
    :param index:
    :return:
    """
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
    """
    Get Notification url from DB
    :param address:
    :return:
    """
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
    """
    Send notification to the user.
    :return:
    """
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
    """
    Check if the transaction is success or not
    :param tx_result:
    :return:
    """
    return tx_result == 'tesSUCCESS'


def update_active_status(address,status = True):
    """
    Update active status of the user.
    :param address:
    :param status:
    :return:
    """
    try:
        cursor = db.cursor()
        update_query = "Update aux_ripp_address_master set is_active = " + str(status) + \
                       " where address = '" + address + "'"

        cursor.execute(update_query)
        db.commit()
    except Exception as e:
        logger.info('Error update_active_status :' + str(e))


def insert_transaction(from_address, to_address, amount, txid, sequence, ledger, created, destination_tag, status):
    """
    Insert Transaction in Database
    """
    try:
        cursor = db.cursor()
        insert_query = 'Insert into aux_ripp_transaction_master' \
                       ' (from_address,to_address,amount,txid,sequence,ledger_index,created_at,bid_id,status)' \
                       ' values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'

        cursor.execute(insert_query, (from_address, to_address, amount, txid, sequence, ledger, created, destination_tag, status))
        db.commit()
    except Exception as e:
        logger.info('Error insert_transaction : ' + str(e))


def address_active(transaction_data):
    """
    Checks if the address is newly generated
    :return:
    """
    for node in transaction_data.get('metaData', {}).get('AffectedNodes', {}):
        if 'CreatedNode' in node:
            return True
    return False


def reciver_crawler():
    """
    Main Process
    :return:
    """
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

                                # Data
                                from_address = transaction_data.get('Account', '')
                                amount = transaction_data.get('Amount', '')
                                destination_tag = transaction_data.get('DestinationTag', '')
                                sequence = transaction_data.get('Sequence', '')
                                created = datetime.datetime.now()

                                if validate_transaction(tx_result):
                                    status = 'Success'
                                    if address_active(transaction_data):
                                        balance = get_account_balance(to_address)
                                        if balance:
                                            update_active_status(to_address)
                                else:
                                    status = 'Failure'

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
