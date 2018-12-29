from django.db import models
from django.db.models.fields.files import (
    FieldFile,
    FileField
) 
from io import BytesIO
try:
    from django.urls import reverse
except ImportError:  # Django < 2.0 # pragma: no cover
    from django.core.urlresolvers import reverse
from .crypt import Cryptographer
try:
    from urllib.parse import quote as url_encode  # Python 3
except ImportError:
    from urllib import quote as url_encode  # Python 2
from django.contrib.auth.models import User



###### custom wrapper of FieldFile #######
## This Wrapper is used to encrypt files before they are saved ##

class EncryptedFile(BytesIO):
    def __init__(self, content,password):
        self.size = content.size
        BytesIO.__init__(self, Cryptographer.encrypted(content.file.read(),password))

class EncryptionMixin(object):

    def save(self, name, content, save=True):
        password = Cryptographer.getKey(Cryptographer.getUser(name))
        return FieldFile.save(
            self,
            name,
            EncryptedFile(content,bytes(password, "utf8")),
            save=save
        )
    save.alters_data = True

    def _get_url(self):
        return reverse('FETCH_URL_NAME', kwargs={
            "path": super(EncryptionMixin, self).url
        })
    url = property(_get_url)


class EncryptedFieldFile(EncryptionMixin, FieldFile):
    pass

class EncryptedFileField(FileField):
    attr_class = EncryptedFieldFile

####### MODELS #######

def generate_filename(self, filename):
    print("TEEEEESSSSSTTTTTT----------")
    print(self.user.username)
    print(filename)
    url = "files/users/%s/%s" % (self.user.username, filename)
    return url

class File(models.Model):
    name = models.CharField(max_length=100)
    size = models.IntegerField() #in ko
    modification_date = models.DateField()  
    fileType = models.CharField(max_length=100)
    file = EncryptedFileField(fileType,upload_to=generate_filename)    
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    #check here when we will want to modify users https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#proxy
    

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)
