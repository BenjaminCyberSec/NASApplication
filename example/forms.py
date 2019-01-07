from django import forms
from django.forms import formset_factory

from .models import File


class FileForm(forms.Form):
     file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

class KeyForm(forms.Form):
     password = forms.CharField(widget=forms.PasswordInput())

class OwnerForm(forms.Form):
     name = forms.CharField(
        label='Owner Name',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the correct owner\' name here'
        })
     )
OwnerFormSet = formset_factory(OwnerForm, extra=1)

class SharedFileForm(forms.Form):
     minimum_validation = forms.IntegerField()
     file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
     #OwnerFormSet = formset_factory(OwnerForm, extra=2)
     




