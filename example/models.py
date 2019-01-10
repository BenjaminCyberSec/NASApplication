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
from datetime import datetime




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
    category = models.CharField(max_length=10)
    address = models.CharField(max_length=1000)
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
        self.url = "%sfiles/users/%s/%s" % (MEDIA_URL,self.user.username, self.name) #don't keep ben
        super(File, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def rename(self, new_name, user_id, address):
        i = 0
        #This while is necessary because of we don't know if name + i already exists
        while len(File.objects.filter(user = User.objects.get(id=user_id),address = address,name =  new_name)) != 0:
            if i > 0:
                new_name = new_name[1:]
            new_name = str(i)+new_name
            i += 1
        self.name = new_name
        self.save()

#The SharedFile model is used to store shared files
class SharedFile(AbstractBaseFile):
    fileType = models.CharField(max_length=100)
    file = EncryptedFileField(fileType,upload_to="shared_files/")   
    nb_owners =  models.IntegerField()
    minimum_validation =  models.IntegerField()
    users = models.ManyToManyField(User, through='Owner')
    url = models.CharField(max_length=100, null=True)

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        self.url = "%sshared_files/%s" % (MEDIA_URL,self.name)
        super(SharedFile, self).save(*args, **kwargs)

    #The following methods upload a list of shared files and create the corresponding owners
    #It takes a owners parameter wich is a dictionary owner : [], it fills the list with couple file keys
    @classmethod
    def upload_list(cls, file_list,owners,minimum_validation,size):
        for data in file_list:
            key = Cryptographer.generateKey()
            TemporaryKeyHandler.addSharedFile(key,data.name)
            s=Cryptographer.shareKey(key, minimum_validation,size)
            i=0
            for k,v in owners.items():
                v.append(data.name)
                v.append(s[i])
                i+=1
            sh = SharedFile(name =  data.name,
            size = data.size/1000,
            modification_date = datetime.now(),
            file = data,
            nb_owners = size,
            minimum_validation = minimum_validation)
            sh.save()
            for user in owners.keys():
                Owner(user= user,shared_file=sh ).save()
        return owners


#The Owner model is the model use to make a custom m to n relationship between users and sharedfiles 
# and store the (encrypted) keys of the threshold algorythm as they come 
# and the intenions of the user (if he has given his key for deletion or for allowing users to download it)
class Owner(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    shared_file = models.ForeignKey(SharedFile,on_delete=models.CASCADE)
    secret_key_validation = models.CharField(max_length=100)
    date_key_given = models.DateField(null=True)
    secret_key_given = models.BinaryField(max_length=130, null=True)#real length is 128
    wants_deletion = models.BooleanField(default=False)
    wants_download = models.BooleanField(default=False)

    def reset(self):
        self.date_key_given = None
        self.secret_key_given = None
        self.wants_deletion = False
        self.wants_download = False
        self.save()

    def setKey(self,password):
        self.date_key_given = datetime.now()
        self.secret_key_given = Cryptographer.encryptKeyPart(password)
        self.save()

    def grant_download(self):
        self.wants_download = True
        self.save()

    def grant_deletion(self):
        self.wants_deletion = True
        self.save()

    
    


