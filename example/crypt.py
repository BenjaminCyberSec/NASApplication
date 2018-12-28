import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

from expiringdict import ExpiringDict

from hashlib import blake2b


#https://cryptography.io/en/latest/hazmat/primitives/cryptographic-hashes/

class Cryptographer(object):
    backend = default_backend()
    salt = bytes("salt", "utf-8") #put in environement
    password = bytes("pasword","utf-8")

    mapEncryption  = Fernet(base64.urlsafe_b64encode(PBKDF2HMAC( #change for a thing not decryptable
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    ).derive(password)))

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

    @classmethod
    def derive(cls,message):
        salt = bytes("salt", "utf-8") #put in environement
        bm=bytes(message, "utf8")
        items = [salt,bm]
        h = blake2b()
        for item in items:
            h.update(item)
        return h.hexdigest()

        #return cls.mapEncryption.encrypt(bytes(message, "utf8"))
    #@classmethod
    #def verify(cls,signature,key):
    #    return cls.mapEncryption.decrypt(bytes(signature, "utf8"),key)


    @classmethod
    def encrypted(cls, content,salt, password):
        fernet = Fernet(base64.urlsafe_b64encode(PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        ).derive(password)))
        return fernet.encrypt(content)

    @classmethod
    def decrypted(cls, content,salt, password):
        fernet = Fernet(base64.urlsafe_b64encode(PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        ).derive(password)))
        return fernet.decrypt(content)

    