from django.test import RequestFactory,Client
from django.urls import reverse
from admin_panel.models import Login_Master,Panel_Master
import pytest
from django.test import TestCase
from admin_panel import util
from ref_strings import UserExceptionStr
import datetime

@pytest.mark.django_db
class TestSuperAdminViews(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestSuperAdminViews, cls).setUpClass()

        # Init User
        cls.user_name = 'test1_1111111'
        cls.password = 'test1_1111111'
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

        # Create User
        enc_password = util.encrypt_password(cls.password)
        cls.test_user = Login_Master.objects.create(user_name=cls.user_name, password=enc_password)

        # Auxpay Db Connection
        db_auxpay = util.get_db_connect()
        cursor_address = db_auxpay.cursor()
        cursor_txs = db_auxpay.cursor()

        # Generate Address
        insert_address = "Insert into aux_ripp_address_master(user_name,address,public_key,enc_master_seed,enc_master_key,is_active,is_multi_sig) values (%s,%s,%s,%s,%s,%s,%s)"
        cursor_address.execute(insert_address, (cls.user_name, cls.address, cls.public_key, cls.enc_master_seed, cls.enc_master_key, False, False))

        # Create Transactions
        insert_transaction = 'Insert into aux_ripp_transaction_master' \
                       ' (from_address,to_address,amount,txid,sequence,ledger_index,created_at,bid_id,status)' \
                       ' values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'

        cursor_txs.execute(insert_transaction,(cls.from_address, cls.to_address,cls.amount, cls.txid, cls.sequence, cls.ledger, cls.created, cls.destination_tag, cls.status))

        db_auxpay.commit()
        cursor_address.close()
        cursor_txs.close()
        del cursor_txs
        del cursor_address
        db_auxpay.close()


    @classmethod
    def tearDownClass(cls):
        # Delete Temp Data
        db_auxpay = util.get_db_connect()
        delete_address_query = "Delete from aux_ripp_address_master where user_name = '%s'"%(cls.user_name)
        delete_tx_query = "Delete from aux_ripp_transaction_master where from_address = '%s' or to_address = '%s'" % (cls.address,cls.address)
        cursor_address = db_auxpay.cursor()
        cursor_txs = db_auxpay.cursor()
        cursor_address.execute(delete_address_query)
        cursor_txs.execute(delete_tx_query)
        db_auxpay.commit()

        cursor_address.close()
        cursor_txs.close()
        del cursor_txs
        del cursor_address
        db_auxpay.close()

    ### Login - Starts
    # Positive Test Case
    def test_authenticate(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        response = self.client.post(self.path, data)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:super_admin_home')

    # Negative Test Case
    def test_unauthenticate_wrong_password(self):
        data = {
            'user_name': self.user_name,
            'password': 'wrong_password'
        }
        response = self.client.post(self.path, data)
        assert response.status_code == 200
        assert response.context['error_message'] == UserExceptionStr.incorrect_user_pass

    # Negative Test Case
    def test_unauthenticate_wrong_username(self):
        data = {
            'user_name': 'wrong_username',
            'password': self.password
        }
        response = self.client.post(self.path, data)
        assert response.status_code == 200
        assert response.context['error_message'] == UserExceptionStr.incorrect_user_pass
    ### Login - Ends

    ### Home - Starts
    # Positive
    def test_home_authentic(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_admin_home')
        response = self.client.get(path)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')

    # Negative
    def test_home_unauthenticate_wrong_username(self):
        data = {
            'user_name': 'wrong_username',
            'password': self.password
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_admin_home')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out')

    # Negative
    def test_home_unauthenticate_wrong_password(self):
        data = {
            'user_name': self.user_name,
            'password': 'wrong_password'
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_admin_home')
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out')
    ### Home - Ends

    ### User Details - Starts
    # Positive - No User Data
    def test_user_details_authentic_no_data(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_admin_user_details',kwargs={'user_name':'wrong_username'})
        response = self.client.get(path)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')

    # Positive - With User Data
    def test_user_details_authentic_with_data(self):
        data = {
            'user_name': self.user_name,
            'password': self.password
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_admin_user_details', kwargs={'user_name': self.user_name})
        response = self.client.get(path)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')

    # Negative
    def test_user_details_unauthenticate_wrong_username(self):
        data = {
            'user_name': 'wrong_username',
            'password': self.password
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_admin_user_details', kwargs={'user_name': 'wrong_username'})
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out')

    # Negative
    def test_user_details_unauthenticate_wrong_password(self):
        data = {
            'user_name': self.user_name,
            'password': 'wrong_password'
        }
        self.client.post(self.path, data)
        path = reverse('admin_panel:super_admin_user_details', kwargs={'user_name': self.user_name})
        response = self.client.get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:log_out')
    ### User Details - Ends

# Login
class TestLoginView(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_login_page(self):
        path = reverse('admin_panel:login_page')
        response = Client().get(path)
        assert response.status_code == 200
        assert path == response.request.get('PATH_INFO')


# # Logout
class TestLogoutView(TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
    def test_logout_page(self):
        path = reverse('admin_panel:log_out')
        response = Client().get(path)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:login_page')


@pytest.mark.django_db
class TestOtherUsersViews(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestOtherUsersViews, cls).setUpClass()
        cls.panel_user_name = 'test1'
        cls.password = 'test1'
        enc_password = util.encrypt_password(cls.password)
        cls.test_user = Panel_Master.objects.create(panel_user_name=cls.panel_user_name, password=enc_password)
        cls.path = reverse('admin_panel:login_page')
        cls.client = Client()

    ### Login - Starts
    # Positive Test Case
    def test_authenticate(self):
        data = {
            'user_name': self.panel_user_name,
            'password': self.password
        }
        response = self.client.post(self.path, data)
        assert response.status_code == 302
        assert response.url == reverse('admin_panel:admin_home')

    # Negative Test Case
    def test_unauthenticate_wrong_password(self):
        data = {
            'user_name': self.panel_user_name,
            'password': 'wrong_password'
        }
        response = self.client.post(self.path, data)
        assert response.status_code == 200
        assert response.context['error_message'] == UserExceptionStr.incorrect_user_pass

    # Negative Test Case
    def test_unauthenticate_wrong_username(self):
        data = {
            'user_name': 'wrong_username',
            'password': self.password
        }
        response = self.client.post(self.path, data)
        assert response.status_code == 200
        assert response.context['error_message'] == UserExceptionStr.incorrect_user_pass
#     ### Login - Ends