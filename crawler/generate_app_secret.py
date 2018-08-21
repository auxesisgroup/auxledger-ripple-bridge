import hashlib
import base64
from Crypto.Cipher import AES
from Crypto import Random

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
            print(str(e))

    def encrypt(self, raw):
        try:
            raw = self._pad(raw)
            iv = Random.new().read(AES.block_size)
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            return base64.b64encode(iv + cipher.encrypt(raw))
        except Exception as e:
            print(str(e))

    def decrypt(self, enc):
        try:
            enc = base64.b64decode(enc)
            iv = enc[:AES.block_size]
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('cp1252')
        except Exception as e:
            print(str(e))

    def _pad(self, s):
        try:
            return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)
        except Exception as e:
            print(str(e))

    @staticmethod
    def _unpad(s):
        try:
            return s[:-ord(s[len(s)-1:])]
        except Exception as e:
            print(str(e))

def encrypt_app_secret(app_key,app_secret):
    """
    Encryption of key
    :param password:
    :return:
    """
    try:
        enc_sk = AESCipher(app_key).encrypt(app_secret)
        return enc_sk
    except Exception as e:
        print(str(e))

def main():
    print("App Secret Encryption :::::::::")
    print("Enter App Key : ")
    app_key = raw_input()
    print("Enter App Secret : ")
    app_secret = raw_input()
    print(encrypt_app_secret(app_key,app_secret))


if __name__ == "__main__":
    main()