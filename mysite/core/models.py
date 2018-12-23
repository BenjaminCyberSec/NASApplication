from django.db import models
from django.db.models.fields.files import (
    FieldFile,
    FileField
) 
#here
from io import BytesIO
try:
    from django.urls import reverse
except ImportError:  # Django < 2.0 # pragma: no cover
    from django.core.urlresolvers import reverse
from .constants import FETCH_URL_NAME
from .crypt import Cryptographer
try:
    from urllib.parse import quote as url_encode  # Python 3
except ImportError:
    from urllib import quote as url_encode  # Python 2


###### custom wrapper of FieldFile #######

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

####### MODEL #######

class File(models.Model):
    name = models.CharField(max_length=100)
    size = models.IntegerField() #in ko
    modification_date = models.DateField()  
    fileType = models.CharField(max_length=100)
    file = EncryptedFileField(fileType,upload_to='files/')


    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)
