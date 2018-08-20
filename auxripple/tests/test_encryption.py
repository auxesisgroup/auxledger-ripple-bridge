from aux_ripp import util


def test_encryption():
    test_token = util.get_token()
    test_secret = 'shATmQKP52eVDwpYaTQsNDUuRJv12'
    enc_sk = util.encrypt_secret_key(token=test_token,secret=test_secret)
    dec_sk = util.decrypt_secret_key(token=test_token,enc_sk=enc_sk)
    assert dec_sk == test_secret