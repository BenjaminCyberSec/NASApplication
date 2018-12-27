from django.db import models


class File(models.Model):
    name = models.CharField(max_length=100)
    size = models.IntegerField() #in ko
    modification_date = models.DateField()   
    file = models.FileField(upload_to='files/')


    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)
