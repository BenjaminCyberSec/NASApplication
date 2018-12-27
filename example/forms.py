from django import forms

from .models import File

class FileForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = File
        fields = ('file',)
