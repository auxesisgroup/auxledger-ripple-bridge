from uuid import uuid4
import hashlib
from Crypto.Cipher import AES
from Crypto import Random
import base64

L1_TOKEN_KEY_INDEX_FROM_START = 8
L1_TOKEN_KEY_INDEX_FROM_END = -8
L2_TOKEN_KEY_INDEX_START = 10
L2_TOKEN_KEY_INDEX_END = 26


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

token = 'a3b7797408d247009cac8dc22066d2c7'
# print('token : ',token)
secret = 'ssZxkUk2DCVz6VrKyCDEo7pHfEJeE'
# print('secret : ',secret)
# enc_key = encrypt_secret_key(token,secret)
# print('enc key : ',enc_key)
dec_key = decrypt_secret_key(token,'yzjNjwueP7/UYGaES9MsuIwUldXfG55LEwKThEHfE1ziYUstnZIaRsJXKNHBeNjQ')
print('dec key : ',dec_key)
print(dec_key == secret)