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
from ref_strings import UserExceptionStr

# Init Parser
parser = ConfigParser.RawConfigParser()

# Node Connection
xrp_node_conf_path = r'/var/xrp_config/xrp_node.ini'
parser.read(xrp_node_conf_path)
RIPPLE_URL = parser.get('ripple_node', 'url')

# Reference
headers = {'Content-type': 'application/json'}
payload = {"jsonrpc": "2.0","id": 1}
logger = None

# Encryption
xrp_enc_conf_path = r'/var/xrp_config/xrp_enc.ini'
parser.read(xrp_enc_conf_path)
L1_TOKEN_KEY_INDEX_FROM_START = int(parser.get('key_enc', 'l1_start'))
L1_TOKEN_KEY_INDEX_FROM_END = int(parser.get('key_enc', 'l1_end'))
L2_TOKEN_KEY_INDEX_START = int(parser.get('key_enc', 'l2_start'))
L2_TOKEN_KEY_INDEX_END = int(parser.get('key_enc', 'l2_end'))



# Logs
def init_logger():
    """
    Initialization of log object
    :return:
    """
    global logger
    log_path = '/var/log/xrp_logs/admin_logs/admin_%s.log'%(str(datetime.date.today()).replace('-','_'))
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


# AuxRipple DB - Start
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


def get_user_master_data(user_name=''):
    """
    Get user data for specified users.
    if no user is specified return all the user data.
    :param user_name:
    :return:
    """
    try:
        db = get_db_connect()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        query = "Select user_name,token,notification_url,app_key,app_secret from aux_ripp_user_master"
        if user_name:
            query += " where user_name = '%s'" %(str(user_name))
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return rows
    except Exception as e:
        init_logger()
        logger.info("Error get_user_master_data : " + str(e))
        raise UserException(UserExceptionStr.some_error_occurred)


def get_address_master_data(user_name=''):
    """
    Get Address of the specified user name
    if no user name is specified return all the addresses.
    :param user_name:
    :return:
    """
    try:
        db = get_db_connect()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        query = "Select address from aux_ripp_address_master"
        if user_name:
            query += " where user_name = '%s'"%(str(user_name))
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return rows
    except Exception as e:
        init_logger()
        logger.info("Error get_address_master_data : " + str(e))
        raise UserException(UserExceptionStr.some_error_occurred)


def get_transaction_master_data(address):
    """
    Get Transaction data for the given address either in to_address or from_address
    :param address:
    :return:
    """
    try:
        db = get_db_connect()
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        query = "Select from_address,to_address,amount,sequence,txid,ledger_index,created_at,bid_id,status from aux_ripp_transaction_master" \
                " where from_address = '%s' OR to_address = '%s'"%(str(address),str(address))
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return rows
    except Exception as e:
        init_logger()
        logger.info("Error get_transaction_master_data : " + str(e))
        raise UserException(UserExceptionStr.some_error_occurred)


def create_user(user_name,token,notification_url,app_key,app_secret):
    """
    Create Application User
    :param user_name:
    :param token:
    :param notification_url:
    :param app_key:
    :param app_secret:
    :return:
    """
    try:
        db = get_db_connect()
        cursor = db.cursor()
        insert_query = 'Insert into aux_ripp_user_master' \
                       ' (user_name,token,notification_url,app_key,app_secret)' \
                       ' values(%s,%s,%s,%s,%s)'

        cursor.execute(insert_query, (user_name, token, notification_url, app_key, app_secret))
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        init_logger()
        logger.info("Error create_user : " + str(e))
        raise UserException(UserExceptionStr.user_already_exist)


def update_user_url(user_name,notification_url):
    """
    Update URL for the user
    :param user_name:
    :param notification_url:
    :return:
    """
    try:
        db = get_db_connect()
        cursor = db.cursor()
        update_query = "Update aux_ripp_user_master set notification_url = '%s'" \
                       " where user_name = '%s'" %(str(notification_url),str(user_name))

        cursor.execute(update_query)
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        init_logger()
        logger.info("Error update_user_url : " + str(e))
        raise UserException(UserExceptionStr.some_error_occurred)

### AuxRipple DB - Ends

def super_user_authenticate(username,password):
    """
    Check if the super user is valid.
    Decrypt the password from database and check with the password
    :param username:
    :param password:
    :return:
    """
    try:
        authentic = False
        user = Login_Master.objects.filter(user_name=username)
        if user:
            enc_pass = user[0].password
            dec_pass = decrypt_password(password, enc_pass)
            if dec_pass == password:
                authentic = True
        return authentic
    except Exception as e:
        init_logger()
        logger.info("Error super_user_authenticate : " + str(e))
        raise UserException(UserExceptionStr.some_error_occurred)


def admin_user_authenticate(username,password):
    """
    Check if the panel user is valid.
    Decrypt the password from database and check with the password
    :param username:
    :param password:
    :return:
    """
    try:
        authentic = False
        role = ''
        user = Panel_Master.objects.filter(panel_user_name=username)
        if user:
            enc_pass = user[0].password
            dec_pass = decrypt_password(password,enc_pass)
            if dec_pass == password:
                authentic = True
                role = user[0].role

        return authentic, role
    except Exception as e:
        init_logger()
        logger.info("Error admin_user_authenticate : " + str(e))
        raise UserException(UserExceptionStr.some_error_occurred)


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
        user = Login_Master.objects.filter(user_name=username)
        if user:
            is_valid = True
        return is_valid
    except Exception as e:
        init_logger()
        logger.info("Error check_super_user_valid : " + str(e))
        raise UserException(UserExceptionStr.some_error_occurred)


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
        raise UserException(UserExceptionStr.some_error_occurred)


def get_token():
    """
    Generate token for the user
    :return: token
    """
    return uuid4().hex


def get_super_app_user_data():
    """
    Get Data of application users
    :return:
    """
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
        raise UserException(UserExceptionStr.some_error_occurred)


def get_super_panel_user_data():
    """
    Get Data of panel users
    :return:
    """
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
        raise UserException(UserExceptionStr.some_error_occurred)


def get_admin_application_user(user_name):
    """
    Get application user name based on panel user name
    :return:
    """
    try:
        application_user = Panel_Master.objects.filter(panel_user_name=user_name)
        if application_user:
            return application_user[0].application_user
        else:
            return ''
    except Exception as e:
        init_logger()
        logger.info("Error get_admin_application_user : " + str(e))
        raise UserException(UserExceptionStr.some_error_occurred)


def get_admin_panel_user_data(user_name):
    """
    Get Admin panel Data
    :param user_name:
    :return:
    """
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
            raise UserException(UserExceptionStr.user_not_found)
    except Exception as e:
        init_logger()
        logger.info("Error get_admin_panel_user_data : " + str(e))
        raise UserException(UserExceptionStr.some_error_occurred)


def get_admin_app_user_data(user_name):
    """
    Get Admin URL Data
    :param user_name:
    :return:
    """
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
            raise UserException(UserExceptionStr.user_not_found)
    except Exception as e:
        init_logger()
        logger.info("Error get_admin_app_user_data : " + str(e))
        raise UserException(UserExceptionStr.some_error_occurred)


def get_super_admin_home_data():
    """
    Get user data for super admin home
    :return:
    """
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
        raise UserException(UserExceptionStr.some_error_occurred)


def get_user_addresses(user_name):
    """
    Get user addresses
    :param user_name:
    :return:
    """
    try:
        addresses = []
        user_data = get_address_master_data(user_name=user_name)
        for data in user_data:
            addresses.append(data['address'])
        return addresses
    except Exception as e:
        init_logger()
        logger.info("Error get_user_addresses : " + str(e))
        raise UserException(UserExceptionStr.some_error_occurred)


def get_transaction_data(user_name):
    """
    Get Transaction Data
    :param user_name:
    :return:
    """
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
            raise UserException(UserExceptionStr.user_not_found)
    except Exception as e:
        init_logger()
        logger.info("Error get_transaction_data : " + str(e))
        raise UserException(UserExceptionStr.some_error_occurred)


### RPC
def get_account_info(address):
    """
    RPC for account information
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
        logger.info("Error get_account_info : " + str(e))
        raise UserException(UserExceptionStr.some_error_occurred)


def get_account_balance(address):
    """
    Getting balance from get_account_info
    :param address:
    :return:
    """
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
        raise UserException(UserExceptionStr.some_error_occurred)


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


def encrypt_password(password):
    """
    Encryption of key
    :param password:
    :return:
    """
    try:
        key = generate_key(password)
        enc_sk = AESCipher(key).encrypt(password)
        return enc_sk
    except Exception as e:
        init_logger()
        logger.info("Error encrypt_password : " + str(e))
        raise UserException(UserExceptionStr.some_error_occurred)


def decrypt_password(password, enc_pass):
    """
    Decryption of key
    :param password:
    :param enc_pass:
    :return:
    """
    try:
        key = generate_key(password)
        dec_sk = AESCipher(key).decrypt(enc_pass)
        return dec_sk
    except Exception as e:
        init_logger()
        logger.info("Error decrypt_password : " + str(e))
        raise UserException(UserExceptionStr.some_error_occurred)
### Encryption - Ends