from admin_panel import util


def test_encryption():
    test_password = 'test_password@123'
    enc_pass = util.encrypt_password(test_password)
    dec_sk = util.decrypt_password(password=test_password,enc_pass=enc_pass)
    assert dec_sk == test_password