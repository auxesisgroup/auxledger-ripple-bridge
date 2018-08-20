from django.test import Client
from django.urls import reverse
from admin_panel.models import Login_Master,Panel_Master
import pytest
from django.test import TestCase
from admin_panel import util
from ref_strings import UserExceptionStr
import datetime

def insert_sample_user(user_name,token,url,app_key,app_secret):
    # Auxpay Db Connection
    db_auxpay = util.get_db_connect()
    cur = db_auxpay.cursor()
    # Generate Address
    insert_address = "Insert into aux_ripp_user_master(user_name,token,notification_url,app_key,app_secret) values (%s,%s,%s,%s,%s)"
    cur.execute(insert_address, (user_name, token, url, app_key, app_secret))
    db_auxpay.commit()
    cur.close()
    db_auxpay.close()

def insert_sample_address(user_name,address,public_key,enc_master_seed,enc_master_key):
    # Auxpay Db Connection
    db_auxpay = util.get_db_connect()
    cur = db_auxpay.cursor()
    # Generate Address
    insert_address = "Insert into aux_ripp_address_master(user_name,address,public_key,enc_master_seed,enc_master_key,is_active,is_multi_sig) values (%s,%s,%s,%s,%s,%s,%s)"
    cur.execute(insert_address, (user_name, address, public_key, enc_master_seed, enc_master_key, False, False))
    db_auxpay.commit()
    cur.close()
    db_auxpay.close()

def insert_sample_transaction(from_address, to_address, amount, txid, sequence,ledger,destination_tag,status):
    # Auxpay Db Connection
    db_auxpay = util.get_db_connect()
    cur = db_auxpay.cursor()
    insert_transaction = 'Insert into aux_ripp_transaction_master' \
                         ' (from_address,to_address,amount,txid,sequence,ledger_index,created_at,bid_id,status)' \
                         ' values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    cur.execute(insert_transaction, (
        from_address, to_address, amount, txid, sequence, ledger, datetime.datetime.now(), destination_tag,
        status))
    db_auxpay.commit()
    cur.close()
    db_auxpay.close()

def delete_sample_user(user_name):
    db_auxpay = util.get_db_connect()
    cur = db_auxpay.cursor()
    delete_user_query = "Delete from aux_ripp_user_master where user_name = '%s'" % (user_name)
    cur.execute(delete_user_query)
    db_auxpay.commit()
    cur.close()
    db_auxpay.close()

def delete_sample_address(user_name):
    # Delete Temp Data
    db_auxpay = util.get_db_connect()
    cur = db_auxpay.cursor()
    delete_address_query = "Delete from aux_ripp_address_master where user_name = '%s'" % (user_name)
    cur.execute(delete_address_query)
    db_auxpay.commit()
    cur.close()
    db_auxpay.close()

def delete_sample_transaction(address):
    # Delete Temp Data
    db_auxpay = util.get_db_connect()
    cur = db_auxpay.cursor()
    delete_tx_query = "Delete from aux_ripp_transaction_master where from_address = '%s' or to_address = '%s'" % (address,address)
    cur.execute(delete_tx_query)
    db_auxpay.commit()
    cur.close()
    db_auxpay.close()

@pytest.mark.django_db
class TestSuperAdminViewsWithData(TestCase):
    """
    Super Admin Test cases with sample data.
    """
    @classmethod
    def setUpClass(cls):
        super(TestSuperAdminViewsWithData, cls).setUpClass()

        # Init User
        cls.user_name = 'test_super_admin1'
        cls.password = 'test_super_admin1'
        cls.address = 'test_address_111111111'
        cls.public_key = 'test_publickey'
        cls.enc_master_seed = 'test_enc_master_seed'
        cls.enc_master_key = 'test_enc_master_key'
        # Transaction
        cls.from_address = cls.address
        cls.to_address = cls.address
        cls.amount = 10000000
        cls.sequence = 20
        cls.ledger = 12345678
        cls.created = datetime.datetime.now()
        cls.destination_tag = 11111111
        cls.status = 'test_status'
        cls.txid = 'dcsac89dsachd98ahc98adh'
        cls.path = reverse('admin_panel:login_page')
        cls.client = Client()

        # Common DB
        cls.cm_db = util.get_db_connect()

        # Create User
        enc_password = util.encrypt_password(cls.password)
        cls.test_user = Login_Master.objects.create(user_name=cls.user_name, password=enc_password)

        # Sample data
        insert_sample_address(cls.user_name,cls.address,cls.public_key,cls.enc_master_seed,cls.enc_master_key)
        insert_sample_transaction(cls.from_address, cls.to_address, cls.amount, cls.txid, cls.sequence,cls.ledger,cls.destination_tag,cls.status)

    @classmethod
    def tearDownClass(cls):
        # Delete Temp Data
        delete_sample_address(cls.user_name)
        delete_sample_transaction(cls.address)

    ### Login - Starts
    # Positive Test Case
    def test_login(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        response = self.client.post(self.path, data)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:super_admin_home')
    ### Login - Ends

    ### Home - Starts
    # Positive
    def test_home(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_admin_home')
        response = self.client.get(path)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')
    ### Home - Ends

    ### User Details - Starts
    # Get - Positive - No User Data
    def test_user_details_no_data(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_admin_user_details',kwargs={'user_name':'no_user'})
        response = self.client.get(path)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')
    # Get - Positive - With User Data
    def test_user_details_with_data(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_admin_user_details', kwargs={'user_name': self.user_name})
        response = self.client.get(path)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')
    ### User Details - Ends

    ### Add Application User - Starts
    # Get - Positive
    def test_get_add_app_user(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_add_app_user')
        response = self.client.get(path)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')
    # Post - Positive
    def test_post_add_app_user(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        post_data = {
            'app_user_name' : 'test_app_user_name',
            'app_user_url' : 'test_app_user_url'
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_add_app_user')
        response = self.client.post(path,post_data)

        delete_query = "Delete from aux_ripp_user_master where user_name = 'test_app_user_name'"
        cur = self.cm_db.cursor()
        cur.execute(delete_query)
        cur.close()
        self.cm_db.commit()

        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')
        assert response.context['result'] == UserExceptionStr.success
    # Post - Negative - Duplicate user name
    def test_post_add_app_user_duplicate_user_name(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        post_data = {
            'app_user_name' : 'test_app_user_name',
            'app_user_url' : 'test_app_user_url'
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_add_app_user')
        self.client.post(path,post_data)
        response = self.client.post(path, post_data)

        delete_query = "Delete from aux_ripp_user_master where user_name = 'test_app_user_name'"
        cur = self.cm_db.cursor()
        cur.execute(delete_query)
        cur.close()
        self.cm_db.commit()
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')
        assert response.context['result'] == UserExceptionStr.user_already_exist

    # Post - Negative - Blank Fields
    def test_post_add_app_user_blank_fields(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        post_data = {
            'app_user_name': '',
            'app_user_url': 'test_app_user_url'
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_add_app_user')
        response = self.client.post(path, post_data)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')
        assert response.context['result'] == UserExceptionStr.specify_required_fields

    ### Add Application User - Ends

    ### Add Panel User - Starts
    # Get - Positive
    def test_get_add_panel_user(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_add_panel_user')
        response = self.client.get(path)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')
    # Post - Positive
    def test_post_add_panel_user(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        post_data = {
            'panel_app_user': 'test_panel_app_user',
            'panel_user_name': 'test_panel_user_name',
            'panel_password' : 'test_panel_password',
            'panel_role' : 'test_panel_role',
            'panel_mobile_number': '032103205'
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_add_panel_user')
        response = self.client.post(path, post_data)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')
        assert response.context['result'] == UserExceptionStr.success
    # Post - Negative
    def test_post_add_panel_user_duplicate_user_name(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        post_data = {
            'panel_app_user': 'test_panel_app_user',
            'panel_user_name': 'test_panel_user_name',
            'panel_password': 'test_panel_password',
            'panel_role': 'test_panel_role',
            'panel_mobile_number': '123456789'
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_add_panel_user')
        self.client.post(path, post_data)
        response = self.client.post(path, post_data)
        assert response.status_code == 400
        assert path == response.request.get('PATH_INFO')
        assert response.context['result'] == UserExceptionStr.user_already_exist

    # Post - Negative - Blank Fields
    def test_post_add_panel_user_blank_fields(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        post_data = {
            'panel_app_user': '',
            'panel_user_name': 'test_panel_user_name',
            'panel_password': 'test_panel_password',
            'panel_role': 'test_panel_role',
            'panel_mobile_number': '123456789'
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_add_panel_user')
        response = self.client.post(path, post_data)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')
        assert response.context['result'] == UserExceptionStr.specify_required_fields

    ### Add Panel User - Ends

@pytest.mark.django_db
class TestSuperAdminUnauthenticAccess(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestSuperAdminUnauthenticAccess, cls).setUpClass()
        # Init User
        cls.user_name = 'test_super_admin2'
        cls.password = 'test_super_admin2'
        cls.path = reverse('admin_panel:login_page')

        # Create User
        enc_password = util.encrypt_password(cls.password)
        cls.test_user = Login_Master.objects.create(user_name=cls.user_name, password=enc_password)

    @classmethod
    def tearDownClass(cls):
        pass

    # Get - Negative - Wrong User Name
    def test_get_add_panel_user_wrong_username(self):
        data = {
            'user_name': 'wrong_username',
            'password': self.password
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_add_panel_user')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out',kwargs={'reason':UserExceptionStr.bad_request})
    # Get - Negative - Wrong Password
    def test_get_add_panel_user_wrong_password(self):
        data = {
            'user_name': self.user_name,
            'password': 'wrong_password'
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_add_panel_user')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})
    # Get - Negative - Wrong User Name
    def test_get_add_app_user_wrong_username(self):
        data = {
            'user_name': 'wrong_username',
            'password': self.password
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_add_app_user')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})
    # Get - Negative - Wrong Password
    def test_get_add_app_user_wrong_password(self):
        data = {
            'user_name': self.user_name,
            'password': 'wrong_password'
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_add_app_user')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})
    # Get - Negative - Wrong User Name
    def test_user_details_wrong_username(self):
        data = {
            'user_name': 'wrong_username',
            'password': self.password
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_admin_user_details', kwargs={'user_name': 'wrong_username'})
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})
    # Get - Negative - Wrong Password
    def test_user_details_wrong_password(self):
        data = {
            'user_name': self.user_name,
            'password': 'wrong_password'
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_admin_user_details', kwargs={'user_name': self.user_name})
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})
    # Get - Home - Negative
    def test_home_wrong_username(self):
        data = {
            'user_name': 'wrong_username',
            'password': self.password
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_admin_home')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})
    # Get - Home - Negative
    def test_home_wrong_password(self):
        data = {
            'user_name': self.user_name,
            'password': 'wrong_password'
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_admin_home')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})
    # Login - Negative Test Case
    def test_login_wrong_password(self):
        data = {
            'user_name': self.user_name,
            'password': 'wrong_password'
        }
        response = self.client.post(self.path, data)
        assert response.status_code == 200
        assert response.context['error_message'] == UserExceptionStr.incorrect_user_pass
    # Login - Negative Test Case
    def test_login_wrong_username(self):
        data = {
            'user_name': 'wrong_username',
            'password': self.password
        }
        response = self.client.post(self.path, data)
        assert response.status_code == 200
        assert response.context['error_message'] == UserExceptionStr.incorrect_user_pass

@pytest.mark.django_db
class TestSuperAdminUnauthenticAccessFromPanelUsers(TestCase):
    """
    These are the test cases for checking if other users have access to superadmin pages.
    Expected Result : If any panel user try to access super admin pages, session should log out.
    """
    @classmethod
    def setUpClass(cls):
        super(TestSuperAdminUnauthenticAccessFromPanelUsers, cls).setUpClass()
        # Init User
        cls.user_name = 'test_super_admin3'
        cls.password = 'test_super_admin3'
        cls.login_path = reverse('admin_panel:login_page')

        # Create User
        enc_password = util.encrypt_password(cls.password)
        cls.test_user = Panel_Master.objects.create(panel_user_name=cls.user_name, password=enc_password,role='admin')

    @classmethod
    def tearDownClass(cls):
        pass

    def test_get_add_panel_user(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:super_add_panel_user')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

    def test_post_add_panel_user(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        post_data = {
            'panel_app_user': 'test_panel_app_user',
            'panel_user_name': 'test_panel_user_name',
            'panel_password' : 'test_panel_password',
            'panel_role' : 'test_panel_role',
            'panel_mobile_number': '13203043'
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:super_add_panel_user')
        response = self.client.post(path, post_data)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

    def test_get_add_app_user(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:super_add_app_user')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

    def test_post_add_app_user(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        post_data = {
            'app_user_name' : 'test_app_user_name',
            'app_user_url' : 'test_app_user_url'
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:super_add_app_user')
        response = self.client.post(path,post_data)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

    def test_user_details(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:super_admin_user_details', kwargs={'user_name': 'wrong_username'})
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

    def test_home(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:super_admin_home')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

class TestLoginView(TestCase):
    """
    Test Cases for Login
    """
    @classmethod
    def setUpClass(cls):
        super(TestLoginView, cls).setUpClass()
        # Init User
        cls.user_name = 'test_login_1'
        cls.password = 'test_login_1'
        cls.login_path = reverse('admin_panel:login_page')

        # Create User
        enc_password = util.encrypt_password(cls.password)
        cls.test_user = Panel_Master.objects.create(panel_user_name=cls.user_name, password=enc_password, role='admin')

    @classmethod
    def tearDownClass(cls):
        pass
    # Positive
    def test_login_page(self):
        response = Client().get(self.login_path)
        assert response.status_code == 200
        assert self.login_path == response.request.get('PATH_INFO')

    # Negative Test Case
    def test_login_blank_user_name(self):
        data = {
            'user_name': '',
            'password': self.password
        }
        response = self.client.post(self.login_path, data)
        assert response.status_code == 200
        assert response.context['error_message'] == UserExceptionStr.specify_required_fields
    # Negative Test Case
    def test_login_blank_password(self):
        data = {
            'user_name': self.user_name,
            'password': ''
        }
        response = self.client.post(self.login_path, data)
        assert response.status_code == 200
        assert response.context['error_message'] == UserExceptionStr.specify_required_fields

    # Negative Test Case
    def test_login_blank_all(self):
        data = {
            'user_name': '',
            'password': ''
        }
        response = self.client.post(self.login_path, data)
        assert response.status_code == 200
        assert response.context['error_message'] == UserExceptionStr.specify_required_fields

class TestLogoutView(TestCase):
    """
    Test Cases for logout
    """
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_logout_page(self):
        path = reverse('admin_panel:log_out',kwargs={'reason':''})
        response = Client().get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:login_page')

@pytest.mark.django_db
class TestPanelUsersAdmin(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestPanelUsersAdmin, cls).setUpClass()
        cls.user_name = 'test_admin_1'
        cls.panel_user_name = 'test_admin_1'
        cls.password = 'test_admin_1'
        cls.address = 'test_address'
        cls.public_key = 'test_public_key'
        cls.enc_master_seed = 'test_enc_master_seed'
        cls.enc_master_key = 'test_enc_master_key'
        cls.from_address = cls.address
        cls.to_address = cls.address
        cls.amount = 100000
        cls.txid = 'asdacsacaw23f43c23'
        cls.sequence = 13548921
        cls.ledger = 123456
        cls.destination_tag = 00025415
        cls.status = 'success'
        cls.role = 'admin'
        cls.token = 'test_token'
        cls.url = 'test_url'
        cls.app_key = 'test_app_key'
        cls.app_secret = 'test_app_secret'
        enc_password = util.encrypt_password(cls.password)
        cls.test_user = Panel_Master.objects.create(application_user=cls.user_name,panel_user_name=cls.panel_user_name, password=enc_password,role=cls.role)
        insert_sample_user(cls.user_name,cls.token,cls.url,cls.app_key,cls.app_secret)
        cls.login_path = reverse('admin_panel:login_page')
        cls.client = Client()

    @classmethod
    def tearDownClass(cls):
        delete_sample_user(cls.user_name)
    # Positive
    def test_login(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        response = self.client.post(self.login_path, data)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:admin_home')

    # Positive
    def test_home_no_data(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_home')
        response = self.client.get(path)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')

    # Positive - with data
    def test_home_with_data(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_home')

        # Insert Data
        insert_sample_address(self.user_name, self.address, self.public_key, self.enc_master_seed, self.enc_master_key)
        insert_sample_transaction(self.from_address, self.to_address, self.amount, self.txid, self.sequence, self.ledger,self.destination_tag, self.status)
        response = self.client.get(path)
        delete_sample_address(self.user_name)
        delete_sample_transaction(self.address)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')

    # Positive
    def test_get_add_panel_user(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_add_panel_user')
        response = self.client.get(path)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')

    # Positive
    def test_post_add_panel_user(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        post_data = {
            'admin_panel_user_name': 'test_admin_panel_user_name',
            'admin_panel_password': 'test_panel_password',
            'admin_panel_role': 'test_panel_role',
            'admin_panel_mobile_number': '1213213213'
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_add_panel_user')
        response = self.client.post(path, post_data)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')
        assert response.context['result'] == UserExceptionStr.success

    # Negative - Sending any Blank field
    def test_post_add_panel_user_blank_field(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        post_data = {
            'admin_panel_user_name': '',
            'admin_panel_password': 'test_panel_password',
            'admin_panel_role': 'test_panel_role',
            'admin_panel_mobile_number': '1213213213'
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_add_panel_user')
        response = self.client.post(path, post_data)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')
        assert response.context['result'] == UserExceptionStr.specify_required_fields

    # Negative - Duplicate Entry
    def test_post_add_panel_user_duplicate(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        post_data = {
            'admin_panel_user_name': 'test_admin_panel_user_name',
            'admin_panel_password': 'test_panel_password',
            'admin_panel_role': 'test_panel_role',
            'admin_panel_mobile_number': '1213213213'
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_add_panel_user')
        self.client.post(path, post_data)
        response = self.client.post(path, post_data)
        assert response.status_code == 400
        assert path == response.request.get('PATH_INFO')
        assert response.context['result'] == UserExceptionStr.user_already_exist

    # Positive
    def test_get_edit_url(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_edit_url')
        response = self.client.get(path)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')

    # Positive
    def test_post_edit_url(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        post_data = {
            'admin_notification_url': 'test_admin_notification_url',
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_edit_url')
        response = self.client.post(path, post_data)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')
        assert response.context['result'] == UserExceptionStr.success

    # Negative - Sending Blank
    def test_post_edit_url_blank(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        post_data = {
            'admin_notification_url': '',
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_edit_url')
        response = self.client.post(path, post_data)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')
        assert response.context['result'] == UserExceptionStr.specify_required_fields

@pytest.mark.django_db
class TestPanelUsersAdminUnauthenticAccess(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestPanelUsersAdminUnauthenticAccess, cls).setUpClass()
        cls.user_name = ''
        cls.panel_user_name = 'test_admin_2'
        cls.password = 'test_admin_2'
        cls.role = 'admin'
        enc_password = util.encrypt_password(cls.password)
        cls.test_user = Panel_Master.objects.create(application_user=cls.user_name, panel_user_name=cls.panel_user_name,
                                                    password=enc_password, role=cls.role)
        cls.login_path = reverse('admin_panel:login_page')
        cls.client = Client()

    @classmethod
    def tearDownClass(cls):
        pass

    ### Login - Starts
    # Negative Test Case
    def test_login_wrong_password(self):
        data = {
            'user_name': self.panel_user_name,
            'password': 'wrong_password'
        }
        response = self.client.post(self.login_path, data)
        assert response.status_code == 200
        assert response.context['error_message'] == UserExceptionStr.incorrect_user_pass

    # Negative Test Case
    def test_login_wrong_username(self):
        data = {
            'user_name': 'wrong_username',
            'password': self.password
        }
        response = self.client.post(self.login_path, data)
        assert response.status_code == 200
        assert response.context['error_message'] == UserExceptionStr.incorrect_user_pass

    # Get - Home - Negative
    def test_home_wrong_username(self):
        data = {
            'user_name': 'wrong_username',
            'password': self.password
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_home')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

    # Get - Home - Negative
    def test_home_wrong_password(self):
        data = {
            'user_name': self.panel_user_name,
            'password': 'wrong_password'
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_home')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

    # Get - Negative - Wrong User Name
    def test_get_add_panel_user_wrong_username(self):
        data = {
            'user_name': 'wrong_username',
            'password': self.password
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_add_panel_user')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})
    # Get - Negative - Wrong Password
    def test_get_add_panel_user_wrong_password(self):
        data = {
            'user_name': self.panel_user_name,
            'password': 'wrong_password'
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_add_panel_user')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})
    # Get - Negative - Wrong User Name
    def test_get_edit_url_wrong_username(self):
        data = {
            'user_name': 'wrong_username',
            'password': self.password
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_edit_url')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})
    # Get - Negative - Wrong Password
    def test_get_edit_url_wrong_password(self):
        data = {
            'user_name': self.panel_user_name,
            'password': 'wrong_password'
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_edit_url')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

@pytest.mark.django_db
class TestPanelAdminUnauthenticAccessFromManager(TestCase):
    """
    These are the test cases for checking if other users have access to superadmin pages.
    Expected Result : If any panel user try to access super admin pages, session should log out.
    """
    @classmethod
    def setUpClass(cls):
        super(TestPanelAdminUnauthenticAccessFromManager, cls).setUpClass()
        # Init User
        cls.panel_user_name = 'test_admin_3'
        cls.password = 'test_admin_3'
        cls.login_path = reverse('admin_panel:login_page')

        # Create User
        enc_password = util.encrypt_password(cls.password)
        cls.test_user = Panel_Master.objects.create(panel_user_name=cls.panel_user_name, password=enc_password,role='manager')

    @classmethod
    def tearDownClass(cls):
        pass

    def test_get_add_panel_user(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_add_panel_user')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

    def test_post_add_panel_user(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        post_data = {
            'panel_app_user': 'test_panel_app_user',
            'panel_user_name': 'test_panel_user_name',
            'panel_password' : 'test_panel_password',
            'panel_role' : 'test_panel_role',
            'panel_mobile_number': '13203043'
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_add_panel_user')
        response = self.client.post(path, post_data)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

    def test_get_edit_url(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_edit_url')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

    def test_post_edit_url(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        post_data = {
            'app_user_name' : 'test_app_user_name',
            'app_user_url' : 'test_app_user_url'
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_edit_url')
        response = self.client.post(path,post_data)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

@pytest.mark.django_db
class TestPanelAdminUnauthenticAccessFromCustomer(TestCase):
    """
    These are the test cases for checking if other users have access to superadmin pages.
    Expected Result : If any panel user try to access super admin pages, session should log out.
    """
    @classmethod
    def setUpClass(cls):
        super(TestPanelAdminUnauthenticAccessFromCustomer, cls).setUpClass()
        # Init User
        cls.panel_user_name = 'test_admin_4'
        cls.password = 'test_admin_4'
        cls.login_path = reverse('admin_panel:login_page')

        # Create User
        enc_password = util.encrypt_password(cls.password)
        cls.test_user = Panel_Master.objects.create(panel_user_name=cls.panel_user_name, password=enc_password,role='customer_service')

    @classmethod
    def tearDownClass(cls):
        pass

    def test_get_add_panel_user(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_add_panel_user')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

    def test_post_add_panel_user(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        post_data = {
            'panel_app_user': 'test_panel_app_user',
            'panel_user_name': 'test_panel_user_name',
            'panel_password' : 'test_panel_password',
            'panel_role' : 'test_panel_role',
            'panel_mobile_number': '13203043'
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_add_panel_user')
        response = self.client.post(path, post_data)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

    def test_get_edit_url(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_edit_url')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

    def test_post_edit_url(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        post_data = {
            'app_user_name' : 'test_app_user_name',
            'app_user_url' : 'test_app_user_url'
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_edit_url')
        response = self.client.post(path,post_data)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

@pytest.mark.django_db
class TestPanelAdminUnauthenticAccessFromSuperAdmin(TestCase):
    """
    These are the test cases for checking if other users have access to superadmin pages.
    Expected Result : If any panel user try to access super admin pages, session should log out.
    """
    @classmethod
    def setUpClass(cls):
        super(TestPanelAdminUnauthenticAccessFromSuperAdmin, cls).setUpClass()
        # Init User
        cls.panel_user_name = 'test_admin_5'
        cls.password = 'test_admin_5'
        cls.login_path = reverse('admin_panel:login_page')

        # Create User
        enc_password = util.encrypt_password(cls.password)
        cls.test_user = Login_Master.objects.create(user_name=cls.panel_user_name, password=enc_password)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_get_add_panel_user(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_add_panel_user')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

    def test_post_add_panel_user(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        post_data = {
            'panel_app_user': 'test_panel_app_user',
            'panel_user_name': 'test_panel_user_name',
            'panel_password' : 'test_panel_password',
            'panel_role' : 'test_panel_role',
            'panel_mobile_number': '13203043'
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_add_panel_user')
        response = self.client.post(path, post_data)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

    def test_get_edit_url(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_edit_url')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

    def test_post_edit_url(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        post_data = {
            'app_user_name' : 'test_app_user_name',
            'app_user_url' : 'test_app_user_url'
        }
        self.client.post(self.login_path, data)
        path = reverse('admin_panel:admin_edit_url')
        response = self.client.post(path,post_data)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out', kwargs={'reason': UserExceptionStr.bad_request})

