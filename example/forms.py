from django import forms

from .models import File


class FileForm(forms.Form):
     file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

class KeyForm(forms.Form):
     password = forms.CharField(widget=forms.PasswordInput())

class NewDirectoryForm(forms.Form):
     directory_name = forms.CharField()
