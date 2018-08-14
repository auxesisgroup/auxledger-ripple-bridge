import requests
import logging
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto import Random
import redis
import json
from uuid import uuid4
import datetime
import MySQLdb

# Connections
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
RED = redis.Redis(connection_pool=POOL)
RIPPLE_URL = 'http://167.99.228.1:5005'


# Global Variables
L1_TOKEN_KEY_INDEX_FROM_START = 8
L1_TOKEN_KEY_INDEX_FROM_END = -8
L2_TOKEN_KEY_INDEX_START = 10
L2_TOKEN_KEY_INDEX_END = 26

# References
headers = {'Content-type': 'application/json'}
payload = {"jsonrpc": "2.0","id": 1}
logger = None


# Logs
def init_logger():
    global logger
    log_path = '/var/log/xrp_logs/end_point_logs/end_%s.log'%(str(datetime.date.today()).replace('-','_'))
    handlers = [logging.FileHandler(log_path), logging.StreamHandler()]
    logging.basicConfig(filename=log_path,format='%(asctime)s %(message)s',filemode='a')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers = handlers


class UserException(Exception):
    pass


class AESCipher(object):
    # https://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256
    def __init__(self,key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


def get_token():
    return uuid4().hex


def generate_key(token):
    """
    This method is used for creating key for aes cipher
    :param input: token number
    :return: sha256 of the input
    """
    token_key = hashlib.sha256(token.encode()).hexdigest()
    l1_token_key = token_key[:L1_TOKEN_KEY_INDEX_FROM_START] + token_key[L1_TOKEN_KEY_INDEX_FROM_END:]
    l2_token_key = hashlib.sha256(l1_token_key.encode()).hexdigest()
    l2_token_key = l2_token_key[L2_TOKEN_KEY_INDEX_START:L2_TOKEN_KEY_INDEX_END]
    return l2_token_key


def encrypt_secret_key(token,secret):
    key = generate_key(token)
    enc_sk = AESCipher(key).encrypt(secret)
    return enc_sk


def decrypt_secret_key(token,enc_sk):
    key = generate_key(token)
    dec_sk = AESCipher(key).decrypt(enc_sk)
    return dec_sk


def generate_address():
    error = 'Server is down, please try in some time!'
    try:
        payload['method'] = 'wallet_propose'
        params = {}
        payload['params'] = [params]
        response = requests.post(RIPPLE_URL, data=json.dumps(payload), headers=headers)
        result = json.loads(response.text).get('result',{})
        if result:
            return result
        else:
            raise UserException(error)
    except Exception as e:
        init_logger()
        logger.info("generate_address : " + str(e))
        raise UserException(error)


def get_account_info(address):
    try :
        payload['method'] = 'account_info'
        payload['params'] = [{ "account": address }]
        response = requests.post(RIPPLE_URL, data=json.dumps(payload), headers=headers)
        return json.loads(response.text),True
    except Exception as e:
        init_logger()
        logger.info("get_account_info : " + str(e))
        return "Some error occured. Please try again later!",False


def get_account_balance(address):
    data,result = get_account_info(address)
    if result:
        # Check if account is valid
        status = data.get('result',{}).get('status','')
        if status == 'success':
            return data.get('result',{}).get('account_data',{}).get('Balance',0),True
        else:
            return "Address is not active or incorrect!",False
    else:
        return data,result


def get_fee():
    try:
        payload['method'] = 'fee'
        payload['params'] = []
        response = requests.post(RIPPLE_URL, data=json.dumps(payload), headers=headers)
        data = json.loads(response.text)
        fee = data.get("result",{}).get('drops',{}).get("base_fee")
        if fee:
            return fee
        else:
            raise UserException("Some error occured. Please try again later!.")
    except Exception as e:
        init_logger()
        logger.info("get_fee : " + str(e))
        raise UserException( "Some error occured. Please try again later!.")


### DB Methods
def get_db_connect():
    return MySQLdb.connect(host="localhost",
                     user="my1",
                     passwd="some_pass",
                     db="test_xrp_auxpay")


def close_db(db):
    return db.close()


def check_user_validation(user_name,token,app_key,app_secret):
    try:
        db = get_db_connect()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        query = "Select * from aux_ripp_user_master where user_name = '%s' and " \
                "token = '%s' and app_key = '%s' and app_secret = '%s' "%(user_name,token,app_key,app_secret)
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            return True
        return False
    except Exception as e:
        init_logger()
        err = 'Some error occurred. try again later!'
        logger.info("Error check_user_validation : " + str(e))
        raise UserException(err)
    finally:
        close_db(db)


def insert_address_master(user_name,address,public_key,enc_master_seed,enc_master_key,is_multi_sig):
    try:
        db = get_db_connect()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        query = "Insert into aux_ripp_address_master(user_name,address,public_key,enc_master_seed,enc_master_key,is_active,is_multi_sig) values (%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(query,(user_name,address,public_key,enc_master_seed,enc_master_key,False,is_multi_sig))
        db.commit()
        return True
    except Exception as e:
        init_logger()
        err = 'Some error occurred. try again later!'
        logger.info("Error insert_address_master : " + str(e))
        raise UserException(err)
    finally:
        close_db(db)


def check_address_valid(user_name,address):
    try:
        db = get_db_connect()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        query = "Select * from aux_ripp_address_master where user_name = '%s' and address = '%s'"%(user_name,address)
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            return True
        return False
    except Exception as e:
        init_logger()
        err = 'Some error occurred. try again later!'
        logger.info("Error check_user_validation : " + str(e))
        raise UserException(err)
    finally:
        close_db(db)