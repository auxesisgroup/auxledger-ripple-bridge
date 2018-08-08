import requests
import traceback
import logging
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto import Random
import redis
import json

# References
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
json_path = 'http://127.0.0.1:8080'
log_path = '/home/auxesis/Documents/RIpple/Logs/log_test.log'
testnet_URL = 'https://s.altnet.rippletest.net:51234'
headers = {'Content-type': 'application/json'}
payload = {"jsonrpc": "2.0","id": 1}


# Global Variables
URL_JSON = json_path
RED = redis.Redis(connection_pool=pool)
TOKEN_SHA_START = 10
TOKEN_SHA_END = 26
QUORAM = 2

# Logs
handlers = [logging.FileHandler(log_path), logging.StreamHandler()]
logging.basicConfig(filename=log_path,format='%(asctime)s %(message)s',filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
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

def generate_address():
    """
    This method generates new address for a user
    :return: address {publicKey,privateKey} if success
    """
    method = URL_JSON + '/get_account_data'
    get = requests.get(method)
    if get.status_code == 200:
        return get.json()
    else:
        logger.info("Error : " + str(get.reason))
        raise Exception("Error : " + str(get.reason))

def get_token():
    """
    This method returns the token of user
    :return: Token number
    """
    return '1fcasdc21312cdscsdsdacdsfsdacsda31sda35c4sd'

def generate_key(input):
    """
    This method is used for creating key for aes cipher
    :param input: token number
    :return: sha256 of the input
    """
    return hashlib.sha256(input.encode()).hexdigest()

def create_multi_sign_account(ms_address,ms_secret):
    payload['method'] = 'submit'
    signer_enteries = []
    multi_sig_accounts = RED.smembers('xrp_multi_address')
    for sign in multi_sig_accounts:
        signer_enteries.append(
            {
                "SignerEntry":{
                    "Account" : sign,
                    "SignerWeight" : 1

                }
            }
        )
    params = {
        "secret" : ms_secret,
        'tx_json':{
            "Flags": 0,
            "TransactionType": "SignerListSet",
            "Account": ms_address,
            "SignerQuorum": QUORAM,
            "SignerEntries": signer_enteries
        }
    }
    payload['params'] = [params]
    response = requests.post(testnet_URL, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception("create_multi_sign_account : " + str(response.reason))

def get_fee():
    payload['method'] = 'fee'
    payload['params'] = []
    response = requests.post(testnet_URL, data=json.dumps(payload), headers=headers)
    data_json = json.loads(response.text)
    if response.status_code == 200:
        result = json.loads(response.text)['result']
        return result['drops']['base_fee']
    else:
        raise Exception("get_fee : " + str(response.reason))

def get_account_info(address):
    payload['method'] = 'account_info'
    payload['params'] = [{ "account": address }]
    response = requests.post(testnet_URL, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception("get_account_info : " + str(response.reason))

def get_account_balance(address):
    json_data = get_account_info(address)
    try:
        return json_data['result']['account_data']['Balance']
    except Exception as e:
        raise Exception('get_account_balance : ' + str(e))


def sig_xrp(from_address,secret_key,to_address,amount):
    payload['method'] = 'sign'
    params = {
        "offline": False,
        "secret": secret_key,
        "tx_json": {
            "TransactionType": "Payment",
            "Account": from_address,
            "Amount" : str(amount),
            "Destination": to_address
        },
    }

    payload['params'] = [params]
    response = requests.post(testnet_URL, data=json.dumps(payload), headers=headers)
    print('Payment Init')
    if response.status_code == 200:
        return json.loads(response.text)['result']['tx_blob']
    else:
        raise Exception("sig_xrp : " + str(response.reason))


def submit_txs(blob):
    payload['method'] = 'submit'
    payload['params'] = [{'tx_blob':blob}]
    response = requests.post(testnet_URL, data=json.dumps(payload), headers=headers)
    print('Payment Submitted')
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception("submit_txs : " + str(response.reason))

def main():

    try:
        # Generate new Address
        print('Generating Address................')
        # account = generate_address()
        # secret = str(account['secret'])
        # address = str(account['address'])
        # # account_ms = generate_address()
        # # secret_multi_sig = str(account_ms['secret'])
        # # address_multisig = str(account_ms['address'])
        # RED.sadd('xrp_aw_set',address)
        # print('address : ',address)
        # print('secret : ',secret)
        #
        # # Get Token
        # token = get_token()
        #
        # # Key
        # key = generate_key(token)
        # print('key : ',key)
        # trim_key = key[TOKEN_SHA_START:TOKEN_SHA_END]
        # print('trim_key : ',trim_key)
        #
        # # Encrypt
        # enc_sk = AESCipher(trim_key).encrypt(secret)
        # print('enc_sk :',enc_sk)
        #
        # # Add funds
        # print('-' * 100)
        # print('Adding funds................')
        source_acc = 'rfLFKGKSq4K9eZg1LzaXuPuxZc5GdKwyRt'
        print(source_acc + ' : ' + get_account_balance(source_acc))
        blob = sig_xrp(from_address=source_acc,secret_key='ssuRA5X1xAUepv5ejhdEfyPHzNvZZ',to_address='rGBEnJpVdEH8L1aUvvbJrZppa82AZAqzHt',amount=1)
        print(submit_txs(blob))
        # blob = sig_xrp(from_address=source_acc, secret_key='ssuRA5X1xAUepv5ejhdEfyPHzNvZZ', to_address=address,amount=50000000)
        # print(submit_txs(blob))
        print(source_acc + ' : ' + get_account_balance(source_acc))
        print('Normal : ' + address + ' : ' + get_account_balance(address))


        # Generate Multisig
        print('-' * 100)
        print('Generating Multisig................')
        print create_multi_sign_account(address,secret)
        print('Multisig : ' + address + ' : ' + get_account_balance(address))
        print('-' * 100)

        # Decrypt
        # dec_sk = AESCipher(key).decrypt(enc_sk)
        # print('dec_sk : ',dec_sk)

    except Exception as e:
        print(e)
        traceback.print_exc()

if __name__ == "__main__":
    main()



