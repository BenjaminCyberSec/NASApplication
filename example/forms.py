from django import forms

from .models import File


class FileForm(forms.Form):
     password = forms.CharField(widget=forms.PasswordInput())
     file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
