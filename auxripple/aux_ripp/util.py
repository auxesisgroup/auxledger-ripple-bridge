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

# Connections
POOL = redis.ConnectionPool(host='localhost', port=6379, db=0)
RED = redis.Redis(connection_pool=POOL)
LOG_PATH = '/var/log/xrp_logs/end_point_logs/end_%s.log'%(str(datetime.date.today()).replace('-','_'))

# TODO
RIPPLE_URL = 'http://167.99.228.1:5005'

# Global Variables
L1_TOKEN_KEY_INDEX_FROM_START = 8
L1_TOKEN_KEY_INDEX_FROM_END = -8
L2_TOKEN_KEY_INDEX_START = 10
L2_TOKEN_KEY_INDEX_END = 26

# References
headers = {'Content-type': 'application/json'}
payload = {"jsonrpc": "2.0","id": 1}

# Logs
handlers = [logging.FileHandler(LOG_PATH), logging.StreamHandler()]
logging.basicConfig(filename=LOG_PATH,format='%(asctime)s %(message)s',filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.handlers = handlers


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
            raise Exception(error)
    except Exception as e:
        logger.info("Error : " + error)
        raise Exception(error)


def get_account_info(address):
    try :
        payload['method'] = 'account_info'
        payload['params'] = [{ "account": address }]
        response = requests.post(RIPPLE_URL, data=json.dumps(payload), headers=headers)
        return json.loads(response.text),True
    except Exception as e:
        return "Some error occured. Please try again later!.",False


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
            raise Exception("Some error occured. Please try again later!.")
    except Exception as e:
        raise Exception( "Some error occured. Please try again later!.")

# SELF GARB GWEN PHI WELD LUST FLED MINI KANE AHEM CRY SHED