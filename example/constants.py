import os
from django.conf import settings
from django.utils import six


def _get_setting(name):
    setting_name = "DEFF_{}".format(name)
    return os.getenv(setting_name, getattr(settings, setting_name, None))


def get_bytes(v):

    if isinstance(v, six.string_types):
        return bytes(v.encode("utf-8"))

    if isinstance(v, bytes):
        return v

    raise TypeError(
        "KEY_SALT & FILE_SALT must be specified as strings that convert nicely to "
        "bytes (in the environnement -> export DEFF_KEY_SALT=\"salt\")."
    )


FILE_SALT = get_bytes(_get_setting("FILE_SALT")) 
KEY_SALT = get_bytes(_get_setting("KEY_SALT")) 
#FILE_SALT = get_bytes("FILE_SALT")
#KEY_SALT = get_bytes("KEY_SALT")
SESSION_TTL = 900  