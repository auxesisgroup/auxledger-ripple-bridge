from models import Login_Master, Panel_Master
from uuid import uuid4
import MySQLdb
import requests
import json
import logging
import datetime
import ConfigParser
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto import Random

# Init Parser
parser = ConfigParser.RawConfigParser()

# Node Connection
xrp_node_conf_path = r'/var/xrp_config/xrp_node.ini'
parser.read(xrp_node_conf_path)
RIPPLE_URL = parser.get('ripple_node', 'url')

headers = {'Content-type': 'application/json'}
payload = {"jsonrpc": "2.0","id": 1}
logger = None


# Logs
def init_logger():
    global logger
    log_path = '/var/log/xrp_logs/admin_logs/admin_%s.log'%(str(datetime.date.today()).replace('-','_'))
    handlers = [logging.FileHandler(log_path), logging.StreamHandler()]
    logging.basicConfig(filename=log_path,format='%(asctime)s %(message)s',filemode='a')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers = handlers


class UserException(Exception):
    pass


# AuxRipple DB - Start
def get_db_connect():
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
    return db.close()


def get_user_master_data(user_name=''):
    try:
        db = get_db_connect()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        query = "Select user_name,token,notification_url,app_key,app_secret from aux_ripp_user_master"
        if user_name:
            query += " where user_name = '%s'" %(str(user_name))
        cursor.execute(query)
        rows = cursor.fetchall()
        close_db(db)
        return rows
    except Exception as e:
        init_logger()
        err = 'Some error occurred. try again later!'
        logger.info("Error get_user_master_data : " + str(e))
        raise UserException(err)


def get_address_master_data(user_name=''):
    try:
        db = get_db_connect()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        query = "Select address from aux_ripp_address_master"
        if user_name:
            query += " where user_name = '%s'"%(str(user_name))
        cursor.execute(query)
        rows = cursor.fetchall()
        close_db(db)
        return rows
    except Exception as e:
        init_logger()
        err = 'Some error occurred. try again later!'
        logger.info("Error get_address_master_data : " + str(e))
        raise UserException(err)


def get_transaction_master_data(address):
    try:
        db = get_db_connect()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        query = "Select from_address,to_address,amount,sequence,txid,ledger_index,created_at,bid_id,status from aux_ripp_transaction_master" \
                " where from_address = '%s' OR to_address = '%s'"%(str(address),str(address))
        cursor.execute(query)
        rows = cursor.fetchall()
        close_db(db)
        return rows
    except Exception as e:
        init_logger()
        err = 'Some error occurred. try again later!'
        logger.info("Error get_transaction_master_data : " + str(e))
        raise UserException(err)


def create_user(user_name,token,notification_url,app_key,app_secret):
    try:
        db = get_db_connect()
        cursor = db.cursor()
        insert_query = 'Insert into aux_ripp_user_master' \
                       ' (user_name,token,notification_url,app_key,app_secret)' \
                       ' values(%s,%s,%s,%s,%s)'

        cursor.execute(insert_query, (user_name, token, notification_url, app_key, app_secret))
        db.commit()
        close_db(db)
    except Exception as e:
        init_logger()
        logger.info("Error create_user : " + str(e))
        raise UserException('Some Error Occurred')


def update_user_url(user_name,notification_url):
    try:
        db = get_db_connect()
        cursor = db.cursor()
        update_query = "Update aux_ripp_user_master set notification_url = '%s'" \
                       " where user_name = '%s'" %(str(notification_url),str(user_name))

        cursor.execute(update_query)
        db.commit()
        close_db(db)
    except Exception as e:
        init_logger()
        logger.info("Error update_user_url : " + str(e))
        raise UserException('Some Error Occurred')

### AuxRipple DB - Ends

def super_user_authenticate(username,password):
    try:
        authentic = False
        is_admin = False
        password = decrypt_password(password)
        user = Login_Master.objects.filter(user_name=username,password=password)
        if user:
            authentic = True
            is_admin = user[0].is_admin
        return authentic,is_admin
    except Exception as e:
        init_logger()
        logger.info("Error super_user_authenticate : " + str(e))
        raise UserException('Some Error Occurred!')


def admin_user_authenticate(username,password):
    try:
        authentic = False
        role = ''
        password = decrypt_password(password)
        user = Panel_Master.objects.filter(panel_user_name=username, password=password)
        if user:
            authentic = True
            role = user[0].role
        return authentic, role
    except Exception as e:
        init_logger()
        logger.info("Error admin_user_authenticate : " + str(e))
        raise UserException('Some Error Occurred!')


def check_super_user_valid(username,role):
    """
    This method is used to validate user based on username and role to check if the specific role is bound to user
    Note : This is secure since this check is done only after session checks
    This is done provide extra security for front end
    :param username: username
    :param role: user role
    :return: True if the user has the requested role
    """
    try:
        is_valid = False
        is_admin = True if role == 'Super_Admin' else False
        user = Login_Master.objects.filter(user_name=username,is_admin=is_admin)
        if user:
            is_valid = True
        return is_valid
    except Exception as e:
        init_logger()
        logger.info("Error check_super_user_valid : " + str(e))
        raise UserException('Some Error Occurred!')


def check_admin_user_valid(username,role):
    """
    This method is used to validate user based on username and role to check if the specific role is bound to user
    Note : This is secure since this check is done only after session checks
    This is done provide extra security for front end
    :param username: username
    :param role: user role
    :return: True if the user has the requested role
    """
    try:
        is_valid = False
        user = Panel_Master.objects.filter(panel_user_name=username,role=role)
        if user:
            is_valid = True
        return is_valid
    except Exception as e:
        init_logger()
        logger.info("Error check_admin_user_valid : " + str(e))
        raise UserException('Some Error Occurred!')


def get_token():
    return uuid4().hex


def get_super_app_user_data():
    try:
        user_data = get_user_master_data()
        result = []
        for user in user_data:
            dict_data = {}
            dict_data['user_name'] = user['user_name']
            dict_data['token'] = user['token']
            dict_data['notification_url'] = user['notification_url']
            dict_data['app_key'] = user['app_key']
            dict_data['app_secret'] = user['app_secret']
            result.append(dict_data)
        return result
    except Exception as e:
        init_logger()
        logger.info("Error get_super_app_user_data : " + str(e))
        raise UserException('Some Error Occurred')


def get_super_panel_user_data():
    try:
        panel_data = Panel_Master.objects.all()
        user_data = get_user_master_data()
        result = []
        app_users = set()
        for data in panel_data:
            dict_data = {}
            dict_data['application_user'] = data.application_user
            dict_data['panel_user_name'] = data.panel_user_name
            dict_data['password'] = data.password
            dict_data['role'] = data.role
            dict_data['mobile'] = data.mobile
            result.append(dict_data)

        for data in user_data:
            app_users.add(data['user_name'])

        return app_users,result
    except Exception as e:
        init_logger()
        logger.info("Error get_super_panel_user_data : " + str(e))
        raise UserException('Some Error Occurred')


def get_admin_application_user(user_name):
    try:
        application_user = Panel_Master.objects.filter(panel_user_name=user_name)
        if application_user:
            return application_user[0].application_user
        else:
            return ''
    except Exception as e:
        init_logger()
        logger.info("Error get_admin_application_user : " + str(e))
        raise UserException('Some Error Occurred')


def get_admin_panel_user_data(user_name):
    try:
        application_user = get_admin_application_user(user_name)
        if application_user:
            panel_data = Panel_Master.objects.filter(application_user=application_user)
            result = []
            for data in panel_data:
                dict_data = {}
                dict_data['application_user'] = application_user
                dict_data['panel_user_name'] = data.panel_user_name
                dict_data['password'] = data.password
                dict_data['role'] = data.role
                dict_data['mobile'] = data.mobile
                result.append(dict_data)
            return result
        else:
            raise UserException('User not found')
    except Exception as e:
        init_logger()
        logger.info("Error get_admin_panel_user_data : " + str(e))
        raise UserException('Some Error Occurred')


def get_admin_app_user_data(user_name):
    try:
        application_user = get_admin_application_user(user_name)
        if application_user:
            user_data = get_user_master_data(user_name=application_user)
            result = []
            for data in user_data:
                dict_data = {}
                dict_data['user_name'] = application_user
                dict_data['token'] = data['token']
                dict_data['notification_url'] = data['notification_url']
                dict_data['app_key'] = data['app_key']
                dict_data['app_secret'] = data['app_secret']
                result.append(dict_data)
            return result
        else:
            raise UserException('User not found')
    except Exception as e:
        init_logger()
        logger.info("Error get_admin_app_user_data : " + str(e))
        raise UserException('Some Error Occurred')


def get_super_admin_home_data():
    try:
        result = []
        users = get_user_master_data()
        for user in users:
            dic_data = {}
            dic_data['user_name'] = user['user_name']
            dic_data['token'] = user['token']
            result.append(dic_data)
        return result
    except Exception as e:
        init_logger()
        logger.info("Error get_super_admin_home_data : " + str(e))
        raise UserException('Some Error Occurred')


def get_user_addresses(user_name):
    try:
        addresses = []
        user_data = get_address_master_data(user_name=user_name)
        for data in user_data:
            addresses.append(data['address'])
        return addresses
    except Exception as e:
        init_logger()
        logger.info("Error get_user_addresses : " + str(e))
        raise UserException('Some Error Occurred')


def get_transaction_data(user_name):
    try:
        result = []
        balance_info = []
        total_balance = 0
        addresses = get_user_addresses(user_name)
        if addresses:
            sent = 0
            received = 0
            for address in addresses:

                # Get Balance
                balance = get_account_balance(address)
                balance_info.append({address:balance})

                if type(balance) == int:
                    total_balance += balance

                address = str(address)
                tx_data = get_transaction_master_data(address=address)
                for tx in tx_data:
                    dic_data = {}

                    if address == tx['to_address']:
                        received +=1
                    elif address == tx['from_address']:
                        sent +=1

                    dic_data['user_name'] = user_name
                    dic_data['from_address'] = tx['from_address']
                    dic_data['to_address'] = tx['to_address']
                    dic_data['amount'] = tx['amount']
                    dic_data['txid'] = tx['txid']
                    dic_data['sequence'] = tx['sequence']
                    dic_data['ledger_index'] = tx['ledger_index']
                    dic_data['created_at'] = tx['created_at']
                    dic_data['bid_id'] = tx['bid_id']
                    dic_data['status'] = tx['status']
                    result.append(dic_data)

            total_transactions = len(result)
            return result, total_transactions, sent, received, balance_info, total_balance
        else:
            raise UserException('User not found')
    except Exception as e:
        init_logger()
        logger.info("Error get_transaction_data : " + str(e))
        raise UserException('Some Error Occurred')


### RPC
def get_account_info(address):
    try :
        payload['method'] = 'account_info'
        payload['params'] = [{ "account": address }]
        response = requests.post(RIPPLE_URL, data=json.dumps(payload), headers=headers)
        return json.loads(response.text),True
    except Exception as e:
        init_logger()
        logger.info("Error get_account_info : " + str(e))
        raise UserException('Some Error Occurred')


def get_account_balance(address):
    data,result = get_account_info(address)
    if result:
        # Check if account is valid
        status = data.get('result',{}).get('status','')
        if status == 'success':
            return int(data.get('result',{}).get('account_data',{}).get('Balance',0))
        else:
            return "Address is not active or incorrect!"
    else:
        init_logger()
        logger.info("Error get_account_balance")
        raise UserException('Some Error Occurred')


### Encryption - Starts
xrp_enc_conf_path = r'/var/xrp_config/xrp_enc.ini'
parser.read(xrp_enc_conf_path)
L1_TOKEN_KEY_INDEX_FROM_START = int(parser.get('key_enc', 'l1_start'))
L1_TOKEN_KEY_INDEX_FROM_END = int(parser.get('key_enc', 'l1_end'))
L2_TOKEN_KEY_INDEX_START = int(parser.get('key_enc', 'l2_start'))
L2_TOKEN_KEY_INDEX_END = int(parser.get('key_enc', 'l2_end'))


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


def encrypt_password(password):
    key = generate_key(password)
    enc_sk = AESCipher(key).encrypt(password)
    return enc_sk


def decrypt_password(password):
    key = generate_key(password)
    dec_sk = AESCipher(key).decrypt(password)
    return dec_sk

### Encryption - Ends