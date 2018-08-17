from ref_strings import UserExceptionStr
from django.test import Client
from django.urls import reverse
from django.test import TestCase
import pytest
from aux_ripp import util

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

def delete_sample_user(user_name):
    db_auxpay = util.get_db_connect()
    cur = db_auxpay.cursor()
    delete_user_query = "Delete from aux_ripp_user_master where user_name = '%s'" % (user_name)
    cur.execute(delete_user_query)
    db_auxpay.commit()
    cur.close()
    db_auxpay.close()

def delete_address_master(address):
    db_auxpay = util.get_db_connect()
    cur = db_auxpay.cursor()
    delete_user_query = "Delete from aux_ripp_address_master where address = '%s'" % (address)
    cur.execute(delete_user_query)
    db_auxpay.commit()
    cur.close()
    db_auxpay.close()


@pytest.mark.django_db
class TestGetFee(TestCase):
    """
    Get Fee Test Cases
    """
    @classmethod
    def setUpClass(cls):
        super(TestGetFee, cls).setUpClass()

        cls.user_name = 'test_user_name'
        cls.token = 'test_token'
        cls.url = 'test_url'
        cls.app_key = 'test_app_key'
        cls.app_secret = 'test_app_secret'

        # Generate Sample User
        insert_sample_user(cls.user_name, cls.token, cls.url, cls.app_key, cls.app_secret)


    @classmethod
    def tearDownClass(cls):
        # Delete Sample User
        delete_sample_user(cls.user_name)

    # Positive
    def test_get_fee(self):
        path = reverse('aux_ripp:get_fee')
        data = {
            'user_name': self.user_name,
            'token': self.token,
            'app_key': self.app_key,
            'app_secret': self.app_secret
        }
        response = self.client.post(path, data)
        assert (response.json().get('status')) == 200
        assert ('fee' in response.json())

    # Negative - Wrong Token
    def test_get_fee_wrong_token(self):
        path = reverse('aux_ripp:get_fee')
        data = {
            'user_name': self.user_name,
            'token': 'wrong_token',
            'app_key': self.app_key,
            'app_secret': self.app_secret
        }
        response = self.client.post(path, data)
        assert (response.json().get('status')) == 400
        assert (response.json().get('error')) == UserExceptionStr.invalid_user

    # Negative - Blank Fields
    def test_get_fee_blank_fields(self):
        path = reverse('aux_ripp:get_fee')
        data = {
            'user_name': '',
            'token': self.token,
            'app_key': self.app_key,
            'app_secret': self.app_secret
        }
        response = self.client.post(path, data)
        assert (response.json().get('status')) == 400
        assert (response.json().get('error')) == UserExceptionStr.specify_required_fields

    # Negative - Missing Fields (Token)
    def test_get_fee_missing_fields(self):
        path = reverse('aux_ripp:get_fee')
        data = {
            'user_name': self.user_name,
            'app_key': self.app_key,
            'app_secret': self.app_secret
        }
        response = self.client.post(path, data)
        assert (response.json().get('status')) == 400
        assert (response.json().get('error')) == UserExceptionStr.specify_required_fields


@pytest.mark.django_db
class TestGenerateAddress(TestCase):
    """
    Generate Address Test Cases
    """
    @classmethod
    def setUpClass(cls):
        super(TestGenerateAddress, cls).setUpClass()

        cls.user_name = 'test_user_name'
        cls.token = 'test_token'
        cls.url = 'test_url'
        cls.app_key = 'test_app_key'
        cls.app_secret = 'test_app_secret'

        # Generate Sample User
        insert_sample_user(cls.user_name, cls.token, cls.url, cls.app_key, cls.app_secret)


    @classmethod
    def tearDownClass(cls):
        # Delete Sample User
        delete_sample_user(cls.user_name)

    # Positive
    def test_generate_address(self):
        path = reverse('aux_ripp:generate_address')
        data = {
            'user_name': self.user_name,
            'token': self.token,
            'app_key': self.app_key,
            'app_secret': self.app_secret
        }
        response = self.client.post(path, data)

        address = response.json().get('address')
        delete_address_master(address)

        assert (response.json().get('status')) == 200
        assert ('address' in response.json())

    # Negative - Invalid Token
    def test_generate_address_invalid_fields(self):
        path = reverse('aux_ripp:generate_address')
        data = {
            'user_name': self.user_name,
            'token': 'wrong_token',
            'app_key': self.app_key,
            'app_secret': self.app_secret
        }
        response = self.client.post(path, data)
        assert (response.json().get('status')) == 400
        assert (response.json().get('error')) == UserExceptionStr.invalid_user

    # Negative - Blank Fields
    def test_generate_address_blank_fields(self):
        path = reverse('aux_ripp:generate_address')
        data = {
            'user_name': '',
            'token': self.token,
            'app_key': self.app_key,
            'app_secret': self.app_secret
        }
        response = self.client.post(path, data)
        assert (response.json().get('status')) == 400
        assert (response.json().get('error')) == UserExceptionStr.specify_required_fields

    # Negative - Missing Fields (Token)
    def test_generate_address_missing_fields(self):
        path = reverse('aux_ripp:generate_address')
        data = {
            'user_name': self.user_name,
            'app_key': self.app_key,
            'app_secret': self.app_secret
        }
        response = self.client.post(path, data)
        assert (response.json().get('status')) == 400
        assert (response.json().get('error')) == UserExceptionStr.specify_required_fields


@pytest.mark.django_db
class TestGetBalance(TestCase):
    """
    Generate Address Test Cases
    """
    @classmethod
    def setUpClass(cls):
        super(TestGetBalance, cls).setUpClass()

        cls.user_name = 'test_user_name'
        cls.token = 'test_token'
        cls.url = 'test_url'
        cls.app_key = 'test_app_key'
        cls.app_secret = 'test_app_secret'
        cls.address = 'test_address','test_address_2'

        # Generate Sample User
        insert_sample_user(cls.user_name, cls.token, cls.url, cls.app_key, cls.app_secret)


    @classmethod
    def tearDownClass(cls):
        # Delete Sample User
        delete_sample_user(cls.user_name)

    # Positive - Address does not correspond to the user
    def test_generate_address(self):
        path = reverse('aux_ripp:get_balance')
        data = {
            'user_name': self.user_name,
            'token': self.token,
            'app_key': self.app_key,
            'app_secret': self.app_secret,
            'address': self.address
        }
        response = self.client.post(path, data)
        assert (response.json().get('status')) == 200
        assert ('result' in response.json())

    # Positive - With Valid Address - Address correspond to the user
    def test_generate_address_valid_address(self):

        # Genreat Address
        path = reverse('aux_ripp:generate_address')
        data = {
            'user_name': self.user_name,
            'token': self.token,
            'app_key': self.app_key,
            'app_secret': self.app_secret
        }
        response = self.client.post(path, data)
        address = response.json().get('address')
        path = reverse('aux_ripp:get_balance')
        data = {
            'user_name': self.user_name,
            'token': self.token,
            'app_key': self.app_key,
            'app_secret': self.app_secret,
            'address': address
        }
        response = self.client.post(path, data)
        delete_address_master(address)
        assert (response.json().get('status')) == 200
        assert ('result' in response.json())


    # Negative - Wrong fields(token)
    def test_generate_address_wrong_fields(self):
        path = reverse('aux_ripp:get_balance')
        data = {
            'user_name': self.user_name,
            'token': 'wrong_token',
            'app_key': self.app_key,
            'app_secret': self.app_secret,
            'address': self.address
        }
        response = self.client.post(path, data)
        assert (response.json().get('status')) == 400
        assert (response.json().get('error')) == UserExceptionStr.invalid_user

    # Negative - Blank fields(user_name)
    def test_generate_address_blank_fields(self):
        path = reverse('aux_ripp:get_balance')
        data = {
            'user_name': '',
            'token': self.token,
            'app_key': self.app_key,
            'app_secret': self.app_secret,
            'address': self.address
        }
        response = self.client.post(path, data)
        assert (response.json().get('status')) == 400
        assert (response.json().get('error')) == UserExceptionStr.specify_required_fields


    # Negative - Missing fields (address)
    def test_generate_address_missing_fields(self):
        path = reverse('aux_ripp:get_balance')
        data = {
            'user_name': self.token,
            'token': self.token,
            'app_key': self.app_key,
            'app_secret': self.app_secret
        }
        response = self.client.post(path, data)
        assert (response.json().get('status')) == 400
        assert (response.json().get('error')) == UserExceptionStr.specify_required_fields