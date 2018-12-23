#These fields are a modification of the one presented in the following github: https://github.com/danielquinn/django-encrypted-filefield/blob/master/django_encrypted_filefield/fields.py
from io import BytesIO

try:
    from django.urls import reverse
except ImportError:  # Django < 2.0 # pragma: no cover
    from django.core.urlresolvers import reverse

from django.db.models.fields.files import (
    FieldFile,
    FileField,
    ImageField,
    ImageFieldFile
)

from .constants import FETCH_URL_NAME
from .crypt import Cryptographer

try:
    from urllib.parse import quote as url_encode  # Python 3
except ImportError:
    from urllib import quote as url_encode  # Python 2


class EncryptedFile(BytesIO):
    def __init__(self, content):
        self.size = content.size
        BytesIO.__init__(self, Cryptographer.encrypted(content.file.read()))


class EncryptionMixin(object):

    def save(self, name, content, save=True):
        return FieldFile.save(
            self,
            name,
            EncryptedFile(content),
            save=save
        )
    save.alters_data = True

    def _get_url(self):
        return reverse(FETCH_URL_NAME, kwargs={
            "path": super(EncryptionMixin, self).url
        })
    url = property(_get_url)


class EncryptedFieldFile(EncryptionMixin, FieldFile):
    pass

class EncryptedFileField(FileField):
    attr_class = EncryptedFieldFile


