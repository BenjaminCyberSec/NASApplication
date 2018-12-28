import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from expiringdict import ExpiringDict

from hashlib import blake2b

from .constants import FILE_SALT,KEY_SALT


#https://cryptography.io/en/latest/hazmat/primitives/cryptographic-hashes/

class Cryptographer(object):

    #dictionaries that store entries for a limited amount of time
    _user_cache = ExpiringDict(max_len=500, max_age_seconds=900) #user : key
    _file_cache = ExpiringDict(max_len=1000, max_age_seconds=900) #file : user
  


    @classmethod
    def addUser(cls,user,key):
        cls._user_cache[user] = key
        
    @classmethod
    def getKey(cls,user):
        return cls._user_cache[user]

    @classmethod
    def addFile(cls,user,file):
        cls._file_cache[file] = user
        
    @classmethod
    def getUser(cls,file):
        print(cls._file_cache)
        return cls._file_cache[file]

    #Encrypt password using argon2 as key derivation then aes encryption
    @classmethod
    def derive(cls,message):
        #salt = bytes("salt", "utf-8") #put in environement
        bm=bytes(message, "utf8")
        items = [KEY_SALT,bm]
        h = blake2b()
        for item in items:
            h.update(item)
        return h.hexdigest()


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

    