import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from expiringdict import ExpiringDict
from hashlib import blake2b
from .constants import FILE_SALT,KEY_SALT,SESSION_TTL



# Handle the file cryptage
class Cryptographer(object):

    #dictionaries that store entries for a limited amount of time
    _user_cache = ExpiringDict(max_len=500, max_age_seconds=SESSION_TTL) #user : key
    _file_cache = ExpiringDict(max_len=1000, max_age_seconds=10) #file : user
  
    #link a key to an user for the time of the session
    @classmethod
    def addUser(cls,user,key):
        cls._user_cache[user] = key
        
    @classmethod
    def getKey(cls,user):
        return cls._user_cache[user]

    #link a file to a user for a very short time 
    # (just enough time to encrypt the file with the proper user key in the EncryptedFile model which is
    # a wrapper of FieldFile that can't be given parameters in an usual way)
    @classmethod
    def addFile(cls,user,file):
        cls._file_cache[file] = user
        
    @classmethod
    def getUser(cls,file):
        print(cls._file_cache)
        return cls._file_cache[file]

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

    