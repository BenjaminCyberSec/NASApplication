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
from .temporary_key_handler import TemporaryKeyHandler
try:
    from urllib.parse import quote as url_encode  # Python 3
except ImportError:
    from urllib import quote as url_encode  # Python 2
from django.contrib.auth.models import User
from .settings import MEDIA_URL



###### custom wrapper of FieldFile #######
## This Wrapper is used to encrypt files before they are saved ##

class EncryptedFile(BytesIO):
    def __init__(self, content,password):
        self.size = content.size
        BytesIO.__init__(self, Cryptographer.encrypted(content.file.read(),password))

class EncryptionMixin(object):

    def save(self, name, content, save=True):
     
        password = TemporaryKeyHandler.getFileKey(name)

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
    url = "files/users/%s/%s" % (self.user.username, filename)
    return url

#The AbstractBaseFile abstract model defines the common fields of every type of files models
class AbstractBaseFile(models.Model):
    name = models.CharField(max_length=100)
    size = models.IntegerField() #in ko
    modification_date = models.DateField()  
    

    def get_fileType(self):
        return self.fileType

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ('name',)

#The File model is used to store non-shared files
class File(AbstractBaseFile):
    fileType = models.CharField(max_length=100)
    file = EncryptedFileField(fileType,upload_to=generate_filename)    
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    url = models.CharField(max_length=100, null=True)
    #check here when we will want to modify users 
    # https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#proxy

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.url = "%sfiles/users/%s/%s" % (MEDIA_URL,"ben", self.name)
        super(File, self).save(*args, **kwargs)

    

#The SharedFile model is used to store shared files
class SharedFile(AbstractBaseFile):
    fileType = models.CharField(max_length=100)
    file = EncryptedFileField(fileType,upload_to="shared_files/")   
    nb_owners =  models.IntegerField()
    minimum_validation =  models.IntegerField()
    owners = models.ManyToManyField(User, through='Owner')
    url = models.CharField(max_length=100, null=True)

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        self.url = "%sshared_files/%s" % (MEDIA_URL,self.name)
        super(SharedFile, self).save(*args, **kwargs)

#The Owner model is the model use to make a custom m to n relationship between users and sharedfiles 
# and store the (encrypted) keys of the threshold algorythm as they come 
# and the intenions of the user (if he has given his key for deletion or for allowing users to download it)
class Owner(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    shared_file = models.ForeignKey(SharedFile,on_delete=models.CASCADE)
    secret_key_validation = models.CharField(max_length=100)
    date_key_given = models.DateField(null=True)
    secret_key_given = models.CharField(max_length=100, null=True)
    wants_deletion = models.BooleanField(default=False)
    wants_download = models.BooleanField(default=False)
    


