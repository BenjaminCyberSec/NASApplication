from django import forms

from .models import File


class FileForm(forms.Form):
     file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
