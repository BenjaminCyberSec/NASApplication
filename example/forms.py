from django import forms
from django.forms import formset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import File


class FileForm(forms.Form):
     file_field = forms.FileField(label='Select the file(s) you want to add',widget=forms.ClearableFileInput(attrs={'multiple': True}))

class KeyForm(forms.Form):
     password = forms.CharField(widget=forms.PasswordInput())

class NewDirectoryForm(forms.Form):
     directory_name = forms.CharField()
     
class OwnerForm(forms.Form):
     name = forms.CharField(
        label='Add a user by his username',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the correct owner\'s name here'
        })
     )
OwnerFormSet = formset_factory(OwnerForm, extra=1)

class SharedFileForm(forms.Form):
     minimum_validation = forms.IntegerField(label='Enter the minimum users required to unlock the file (at least 2)')
     file_field = forms.FileField(label='Select the file(s) you want to add',widget=forms.ClearableFileInput(attrs={'multiple': True}))

#This form extends the default user creation form to get the user email
class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )
     




