import base64, secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from hashlib import blake2b
from secretsharing import SecretSharer
from .constants import FILE_SALT,KEY_SALT


# Handle the file cryptage
class Cryptographer(object):

    #hash the given password using blake2 and return the key that will be use as password 
    # to encrypt & decrypt files
    @classmethod
    def derive(cls,message):
        bm=bytes(message, "utf8")
        items = [KEY_SALT,bm]
        h = blake2b()
        for item in items:
            h.update(item)
        return h.hexdigest()

    #Encrypt the file using the given password with sha512
    @classmethod
    def encrypted(cls, content, password):
        fernet = Fernet(base64.urlsafe_b64encode(PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=32,
            salt=FILE_SALT,
            iterations=100000,
            backend=default_backend()
        ).derive(password)))
        return fernet.encrypt(content)

    @classmethod
    def decrypted(cls, content, password):
        fernet = Fernet(base64.urlsafe_b64encode(PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=32,
            salt=FILE_SALT,
            iterations=100000,
            backend=default_backend()
        ).derive(password)))
        return fernet.decrypt(content)

    #generate a random key using python 3 secret function https://docs.python.org/3/library/secrets.html
    @classmethod
    def generateKey(cls):
        return secrets.token_hex(64)
    
    #encrypt the key using a secret sharing algorythm https://github.com/blockstack/secret-sharing
    #then return the generated keys
    @classmethod
    def shareKey(cls, key, agreement_nbr, total_nbr):
        shares = SecretSharer.split_secret(key, agreement_nbr, total_nbr)
        return shares

    @classmethod
    def recoverKey(cls, shares):
        return SecretSharer.recover_secret(shares)#[0:size])

    