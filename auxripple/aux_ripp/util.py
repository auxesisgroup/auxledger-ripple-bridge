import requests
import logging
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto import Random
import redis
import json
import datetime
import MySQLdb
import ConfigParser
from ref_strings import UserExceptionStr

# Init Parser
parser = ConfigParser.RawConfigParser()

# Node Connection
xrp_node_conf_path = r'/var/xrp_config/xrp_node.ini'
parser.read(xrp_node_conf_path)
RIPPLE_URL = parser.get('ripple_node', 'url')

# Redis Connection
xrp_redis_conf_path = r'/var/xrp_config/xrp_redis.ini'
parser.read(xrp_redis_conf_path)
pool = redis.ConnectionPool(host=parser.get('redis', 'host'), port=int(parser.get('redis', 'port')), db=int(parser.get('redis', 'db')))
RED = redis.Redis(connection_pool=pool)

# Key
xrp_enc_conf_path = r'/var/xrp_config/xrp_enc.ini'
parser.read(xrp_enc_conf_path)
L1_TOKEN_KEY_INDEX_FROM_START = int(parser.get('key_enc', 'l1_start'))
L1_TOKEN_KEY_INDEX_FROM_END = int(parser.get('key_enc', 'l1_end'))
L2_TOKEN_KEY_INDEX_START = int(parser.get('key_enc', 'l2_start'))
L2_TOKEN_KEY_INDEX_END = int(parser.get('key_enc', 'l2_end'))

# References
headers = {'Content-type': 'application/json'}
payload = {"jsonrpc": "2.0","id": 1}
logger = None


# Logs
def init_logger():
    """
    Initialization of log object
    :return:
    """
    global logger
    log_path = '/var/log/xrp_logs/end_point_logs/end_%s.log'%(str(datetime.date.today()).replace('-','_'))
    handlers = [logging.FileHandler(log_path), logging.StreamHandler()]
    logging.basicConfig(filename=log_path,format='%(asctime)s %(message)s',filemode='a')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers = handlers

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class UserException(Exception):
    """
    For Handling Exceptions need to be shown on the UI.
    """
    pass

# RPC - Starts
def generate_address():
    """
    Generating new address by RPC on the Ripple Node
    :return:
    """
    error = UserExceptionStr.server_not_responding
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
    """
    RPC for getting account information
    :param address:
    :return:
    """
    try :
        payload['method'] = 'account_info'
        payload['params'] = [{ "account": address }]
        response = requests.post(RIPPLE_URL, data=json.dumps(payload), headers=headers)
        return json.loads(response.text),True
    except Exception as e:
        init_logger()
        logger.info("get_account_info : " + str(e))
        return UserExceptionStr.server_not_responding,False

def get_account_balance(address):
    """
    Method for extracting balance from the response of get_account_info
    :param address:
    :return:
    """
    data,result = get_account_info(address)
    if result:
        # Check if account is valid
        status = data.get('result',{}).get('status','')
        if status == 'success':
            return data.get('result',{}).get('account_data',{}).get('Balance',0),True
        else:
            return UserExceptionStr.address_not_active_incorrect,False
    else:
        return data,result

def get_fee():
    """
    RPC for getting fee
    :return:
    """
    try:
        payload['method'] = 'fee'
        payload['params'] = []
        response = requests.post(RIPPLE_URL, data=json.dumps(payload), headers=headers)
        data = json.loads(response.text)
        fee = data.get("result",{}).get('drops',{}).get("base_fee")
        if fee:
            return fee
        else:
            raise UserException(UserExceptionStr.server_not_responding)
    except Exception as e:
        init_logger()
        logger.info("get_fee : " + str(e))
        raise UserException(UserExceptionStr.server_not_responding)
# RPC - Ends


### DB Methods - Starts
def get_db_connect():
    """
    MySQL Connection
    :return: DB object
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

def close_db(db):
    """
    closing Database connection
    :param db:
    :return:
    """
    return db.close()

def check_user_validation(user_name,token,app_key,app_secret):
    """
    Check if the user is valid.
    :param user_name:
    :param token:
    :param app_key:
    :param app_secret:
    :return: True if the user is valid, false if not
    """
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
        logger.info("Error check_user_validation : " + str(e))
        raise UserException(UserExceptionStr.server_not_responding)
    finally:
        close_db(db)

def insert_address_master(user_name,address,public_key,enc_master_seed,enc_master_key,is_multi_sig):
    """
    Insert newely generated address in the aux_ripp_address_master table.
    :param user_name:
    :param address:
    :param public_key:
    :param enc_master_seed:
    :param enc_master_key:
    :param is_multi_sig:
    :return: True if insertion is successful
    """
    try:
        db = get_db_connect()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        query = "Insert into aux_ripp_address_master(user_name,address,public_key,enc_master_seed,enc_master_key,is_active,is_multi_sig) values (%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(query,(user_name,address,public_key,enc_master_seed,enc_master_key,False,is_multi_sig))
        db.commit()
        return True
    except Exception as e:
        init_logger()
        logger.info("Error insert_address_master : " + str(e))
        raise UserException(UserExceptionStr.server_not_responding)
    finally:
        close_db(db)

def check_address_valid(user_name,address):
    """
    Check the address correspond to the user.
    :param user_name:
    :param address:
    :return: True if address correspond to the user.
    """
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
        logger.info("Error check_user_validation : " + str(e))
        raise UserException(UserExceptionStr.server_not_responding)
    finally:
        close_db(db)
### DB Methods - Ends


### Encryption - Starts
class AESCipher(object):
    """
    AES Cipher Encryption
    Source : https://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256
    """

    def __init__(self,key):
        try:
            self.bs = 32
            self.key = hashlib.sha256(key.encode()).digest()
        except Exception as e:
            init_logger()
            logger.info("Error AESCipher __init__ : " + str(e))
            raise UserException(UserExceptionStr.some_error_occurred)

    def encrypt(self, raw):
        try:
            raw = self._pad(raw)
            iv = Random.new().read(AES.block_size)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            return base64.b64encode(iv + cipher.encrypt(raw))
        except Exception as e:
            init_logger()
            logger.info("Error AESCipher encrypt : " + str(e))
            raise UserException(UserExceptionStr.some_error_occurred)

    def decrypt(self, enc):
        try:
            enc = base64.b64decode(enc)
            iv = enc[:AES.block_size]
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('cp1252')
        except Exception as e:
            init_logger()
            logger.info("Error AESCipher decrypt : " + str(e))
            raise UserException(UserExceptionStr.some_error_occurred)

    def _pad(self, s):
        try:
            return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)
        except Exception as e:
            init_logger()
            logger.info("Error AESCipher _pad : " + str(e))
            raise UserException(UserExceptionStr.some_error_occurred)

    @staticmethod
    def _unpad(s):
        try:
            return s[:-ord(s[len(s)-1:])]
        except Exception as e:
            init_logger()
            logger.info("Error AESCipher _unpad : " + str(e))
            raise UserException(UserExceptionStr.some_error_occurred)

def generate_key(token):
    """
    This method is used for creating key for aes cipher
    :param input: token number
    :return: sha256 of the input
    """
    try:
        token_key = hashlib.sha256(token.encode()).hexdigest()
        l1_token_key = token_key[:L1_TOKEN_KEY_INDEX_FROM_START] + token_key[L1_TOKEN_KEY_INDEX_FROM_END:]
        l2_token_key = hashlib.sha256(l1_token_key.encode()).hexdigest()
        l2_token_key = l2_token_key[L2_TOKEN_KEY_INDEX_START:L2_TOKEN_KEY_INDEX_END]
        return l2_token_key
    except Exception as e:
        init_logger()
        logger.info("Error generate_key : " + str(e))
        raise UserException(UserExceptionStr.some_error_occurred)

def encrypt_secret_key(token,secret):
    """
    Encryption of key
    :param password:
    :return:
    """
    try:
        key = generate_key(token)
        enc_sk = AESCipher(key).encrypt(secret)
        return enc_sk
    except Exception as e:
        init_logger()
        logger.info("Error encrypt_password : " + str(e))
        raise UserException(UserExceptionStr.some_error_occurred)
### Encryption - Ends

