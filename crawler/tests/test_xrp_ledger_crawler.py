import xrp_ledger_crawler
import MySQLdb
import datetime

user_name = 'test_user_name'
token = 'test_token'
url = 'http://localhost'
app_key = 'test_app_key'
app_secret = 'test_app_secret'
address = 'test_address'
public_key = 'test_public_key'
enc_master_seed = 'test_enc_master_seed'
enc_master_key = 'test_enc_master_key'
from_address = address
to_address = address
amount = 1000000
txid = 12345678
sequence = 1242424
ledger = 1021312
created = datetime.datetime.now()
destination_tag = 123456
amount = 'test_amount'
transaction_hash = 'test_transaction_hash'
status ='test_status'
db_auxpay = None
redis_xrp_ledger_crawled = None
log_path = '/var/log/xrp_logs/crawler_logs/ledger_%s.log' % (str(datetime.date.today()).replace('-', '_'))

def insert_sample_data(db_auxpay):

    # Init
    cur = db_auxpay.cursor()

    # Generate User
    insert_address = "Insert into aux_ripp_user_master(user_name,token,notification_url,app_key,app_secret) values (%s,%s,%s,%s,%s)"
    cur.execute(insert_address, (user_name, token, url, app_key, app_secret))
    db_auxpay.commit()

    # Generate Address
    insert_address = "Insert into aux_ripp_address_master(user_name,address,public_key,enc_master_seed,enc_master_key,is_active,is_multi_sig) values (%s,%s,%s,%s,%s,%s,%s)"
    cur.execute(insert_address, (user_name, address, public_key, enc_master_seed, enc_master_key, False, False))
    db_auxpay.commit()
    cur.close()

def delete_sample_data(db_auxpay):
    cur = db_auxpay.cursor()

    # Delete User Master
    delete_user_query = "Delete from aux_ripp_user_master where user_name = '%s'" % (user_name)
    cur.execute(delete_user_query)
    db_auxpay.commit()

    # Delete Address Master
    delete_address_query = "Delete from aux_ripp_address_master where user_name = '%s'" % (user_name)
    cur.execute(delete_address_query)
    db_auxpay.commit()

    cur.close()
    db_auxpay.close()

def delete_transaction(db_auxpay, address):
    cur = db_auxpay.cursor()

    # Delete Transaction
    delete_tx_query = "Delete from aux_ripp_transaction_master where from_address = '%s' or to_address = '%s'" % (address, address)
    cur.execute(delete_tx_query)
    db_auxpay.commit()
    cur.close

def setup_module(module):
    global db_auxpay

    db_auxpay = xrp_ledger_crawler.get_db_connect(
        host = xrp_ledger_crawler.host,
        user = xrp_ledger_crawler.user,
        password = xrp_ledger_crawler.password,
        db_name = xrp_ledger_crawler.db_name
    )
    assert isinstance(db_auxpay, MySQLdb.connections.Connection)

    global redis_xrp_ledger_crawled
    redis_xrp_ledger_crawled = int(xrp_ledger_crawler.r.get("xrp_ledger_crawled") or 0)

    insert_sample_data(db_auxpay)

def teardown_module(module):
    assert isinstance(db_auxpay, MySQLdb.connections.Connection)
    delete_sample_data(db_auxpay)

    xrp_ledger_crawler.r.set("xrp_ledger_crawled", redis_xrp_ledger_crawled)
    assert int(xrp_ledger_crawler.r.get("xrp_ledger_crawled") or 0) == redis_xrp_ledger_crawled

# ++++++ Init Logger
def test_init_logger():
    assert xrp_ledger_crawler.init_logger(log_path) == True

# ------ Init Logger - Wrong Path
def test_init_logger_wrong_path():
    log_path = '/wrong_path/'
    assert xrp_ledger_crawler.init_logger(log_path) == False

# ++++++ RPC - Account Info
def test_get_account_info():
    res_json = xrp_ledger_crawler.get_account_info(address)
    assert isinstance(res_json, dict)

# ------ RPC - Account Info - Wrong URL
def test_get_account_info_wrong_url():
    correct_url = xrp_ledger_crawler.URL
    xrp_ledger_crawler.URL = 'wrong_url'
    res_json = xrp_ledger_crawler.get_account_info(address)
    xrp_ledger_crawler.URL = correct_url
    assert res_json == {}

# ------ RPC - Account Balance
def test_get_account_balance():
    balance = xrp_ledger_crawler.get_account_balance(address)
    assert isinstance(balance, int)

# ++++++ RPC - Validated Ledger Index
def test_get_ledger_validated_index():
    index = xrp_ledger_crawler.get_ledger_validated_index()
    assert isinstance(index, int)

# ------ RPC - Validated Ledger Index - Wrong URL
def test_get_ledger_validated_index_wrong_url():
    correct_url = xrp_ledger_crawler.URL
    xrp_ledger_crawler.URL = 'wrong_url'
    index = xrp_ledger_crawler.get_ledger_validated_index()
    xrp_ledger_crawler.URL = correct_url
    assert index == 0

# ++++++ RPC - Get Ledger Index
def test_get_ledger_transactions():
    transactions = xrp_ledger_crawler.get_ledger_transactions(ledger)
    assert isinstance(transactions, list)

# ------ RPC - Get Ledger Index - Wrong URL
def test_get_ledger_transactions_wrong_url():
    correct_url = xrp_ledger_crawler.URL
    xrp_ledger_crawler.URL = 'wrong_url'
    transactions = xrp_ledger_crawler.get_ledger_transactions(ledger)
    xrp_ledger_crawler.URL = correct_url
    assert isinstance(transactions, list)

# +++++++ Validate Transaction
def test_validate_transaction():
    tx_result = 'tesSUCCESS'
    assert xrp_ledger_crawler.validate_transaction(tx_result) == True

# +++++++ Address Active
def test_is_new_address():
    transaction_data = {
        'metaData': {
            'AffectedNodes': [{
                'CreatedNode': {
                    'NewFields': {
                        'Account': 'rP5cH8jEhHeiEyv3sn88iKAkCHLJXm4HVT',
                        'Balance': '30000000',
                        'Sequence': 1
                    },
                    'LedgerEntryType': 'AccountRoot',
                    'LedgerIndex': 'C4467CBDCBBF8BAC6273632418C0142A54EFD76AE8E5A4A1805695C2002B0E5B'
                }
            },
                {
                    'ModifiedNode': {
                        'LedgerEntryType': 'AccountRoot',
                        'PreviousTxnID': '0382F9A13A800C123B85601AE02F8486E1F2D75055B0542906F06F4E82B219B8',
                        'FinalFields': {
                            'OwnerCount': 0,
                            'Account': 'r35KqtkbBbHNXnsSEUxqnrprvMD8tnHM5q',
                            'Balance': '9879999820',
                            'Flags': 0,
                            'Sequence': 8
                        },
                        'LedgerIndex': 'F5739F44C81DD7FC4A0671F1FCB50C5547B7C49BC09997CB7148ED2E39C8071C',
                        'PreviousTxnLgrSeq': 11725585,
                        'PreviousFields': {
                            'Balance': '9909999830',
                            'Sequence': 7
                        }
                    }
                }
            ]
        }
    }
    assert xrp_ledger_crawler.is_new_address(transaction_data) == True

# ------- Address Active
def test_is_new_address_false():
    transaction_data = {
        'metaData': {
            'AffectedNodes': [{
                'ModifiedNode': {
                    'NewFields': {
                        'Account': 'rP5cH8jEhHeiEyv3sn88iKAkCHLJXm4HVT',
                        'Balance': '30000000',
                        'Sequence': 1
                    },
                    'LedgerEntryType': 'AccountRoot',
                    'LedgerIndex': 'C4467CBDCBBF8BAC6273632418C0142A54EFD76AE8E5A4A1805695C2002B0E5B'
                }
            },
                {
                    'ModifiedNode': {
                        'LedgerEntryType': 'AccountRoot',
                        'PreviousTxnID': '0382F9A13A800C123B85601AE02F8486E1F2D75055B0542906F06F4E82B219B8',
                        'FinalFields': {
                            'OwnerCount': 0,
                            'Account': 'r35KqtkbBbHNXnsSEUxqnrprvMD8tnHM5q',
                            'Balance': '9879999820',
                            'Flags': 0,
                            'Sequence': 8
                        },
                        'LedgerIndex': 'F5739F44C81DD7FC4A0671F1FCB50C5547B7C49BC09997CB7148ED2E39C8071C',
                        'PreviousTxnLgrSeq': 11725585,
                        'PreviousFields': {
                            'Balance': '9909999830',
                            'Sequence': 7
                        }
                    }
                }
            ]
        }
    }
    assert xrp_ledger_crawler.is_new_address(transaction_data) == False

# ++++++ DB Connection
def test_get_db_connect():
    db = xrp_ledger_crawler.get_db_connect(
        host=xrp_ledger_crawler.host,
        user=xrp_ledger_crawler.user,
        password=xrp_ledger_crawler.password,
        db_name=xrp_ledger_crawler.db_name
    )
    assert isinstance(db, MySQLdb.connections.Connection)

# ------ DB Connection - Wrong Password
def test_get_db_connect():
    db = xrp_ledger_crawler.get_db_connect(
        host=xrp_ledger_crawler.host,
        user=xrp_ledger_crawler.user,
        password='wrong_password',
        db_name=xrp_ledger_crawler.db_name
    )
    assert db == None

# ++++++ Get Notification URL
def test_get_notification_url():
    res,res_url,res_key,res_secret = xrp_ledger_crawler.get_notification_url(db_auxpay, address)
    assert res == True
    assert res_url == url
    assert res_key == app_key
    assert res_secret == app_secret

# ------- Get Notification URL - Address not present
def test_get_notification_url_no_address():
    address = 'wrong_address'
    res,res_url,res_key,res_secret = xrp_ledger_crawler.get_notification_url(db_auxpay, address)
    assert res == False
    assert res_url == ''
    assert res_key == ''
    assert res_secret == ''

# ------ Get Notification URL - Db Connection Error
def test_get_notification_url_db_error():
    res,res_url,res_key,res_secret = xrp_ledger_crawler.get_notification_url(None, address)
    assert res == False
    assert res_url == ''
    assert res_key == ''
    assert res_secret == ''

# ++++++ Send Notification
def test_send_notification():
    notification_url = url
    res = xrp_ledger_crawler.send_notification(to_address,from_address,destination_tag,amount,ledger,transaction_hash, status, notification_url, app_key, app_secret)
    assert res == True

# ------ Send Notification - URL not responding
def test_send_notification_wrong_url():
    notification_url = 'wrong_url'
    res = xrp_ledger_crawler.send_notification(to_address,from_address,destination_tag,amount,ledger,transaction_hash, status, notification_url, app_key, app_secret)
    assert res == False

# ++++++ Update Active Status - True
def test_update_active_status():
    res = xrp_ledger_crawler.update_active_status(db_auxpay, address, status=True)
    assert res == True

# ------ Update Active Status - True
def test_update_active_status_db_error():
    res = xrp_ledger_crawler.update_active_status(None, address, status=True)
    assert res == False

# ++++++ Insert Transaction
def test_insert_transaction():
    res = xrp_ledger_crawler.insert_transaction(db_auxpay, from_address, to_address, amount, txid, sequence, ledger, created, destination_tag, status)
    delete_transaction(db_auxpay, address)
    assert res == True

# ------ Insert Transaction - DB Error
def test_insert_transaction_db_error():
    res = xrp_ledger_crawler.insert_transaction(None, from_address, to_address, amount, txid, sequence, ledger, created, destination_tag, status)
    assert res == False

# ++++++ Receiver Crawler
def test_reciver_crawler():
    current_validated_ledger_index = 12345678
    # Temp Redis Data
    xrp_ledger_crawler.r.set("xrp_ledger_crawled", current_validated_ledger_index-2)
    xrp_ledger_crawler.r.sadd("xrp_aw_set",address)
    res = xrp_ledger_crawler.receiver_crawler(db_auxpay, current_validated_ledger_index)
    assert res == True

# ------ Receiver Crawler Job
def test_job_receiver_crawler():
    res = xrp_ledger_crawler.job_receiver_crawler()
    assert res == True