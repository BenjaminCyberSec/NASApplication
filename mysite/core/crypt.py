import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .constants import SALT, PASSWORD


class Cryptographer(object):

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

    