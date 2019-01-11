from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, resolve_url,render
from django.views.decorators.cache import never_cache
from django.views.generic import FormView, TemplateView, ListView, CreateView

from two_factor.views import OTPRequiredMixin
from two_factor.views.utils import class_view_decorator

from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy
from django_otp.decorators import otp_required
from .decorators import key_required, file_address

from .forms import FileForm,KeyForm,SharedFileForm,OwnerFormSet,NewDirectoryForm,SignUpForm,RenameForm
from .models import File, SharedFile, Owner

from .crypt import Cryptographer
from .temporary_key_handler import TemporaryKeyHandler
from datetime import datetime  
from datetime import timedelta

import mimetypes

import os
from django.conf import settings
from django.core.validators import URLValidator, ValidationError
from django.http import Http404, HttpResponse
from django.views.generic import View
import requests
from django.contrib.auth.models import User
from cryptography.fernet import InvalidToken

from django.forms import formset_factory
from .emails import Email
from django.http import JsonResponse
import re
from pathlib import Path
from django.contrib import messages
from .message_handler import error, error_page
from django.core.exceptions import ObjectDoesNotExist



import zipfile
import io 



class HomeView(TemplateView):
    template_name = 'home.html'


class RegistrationView(FormView):
    template_name = 'registration.html'
    form_class = SignUpForm

    def form_valid(self, form):
        form.save()
        return redirect('registration_complete')


class RegistrationCompleteView(TemplateView):
    template_name = 'registration_complete.html'

    def get_context_data(self, **kwargs):
        context = super(RegistrationCompleteView, self).get_context_data(**kwargs)
        context['login_url'] = resolve_url(settings.LOGIN_URL)
        return context


@class_view_decorator(never_cache)
class ExampleSecretView(OTPRequiredMixin, TemplateView):
    template_name = 'secret.html'


@otp_required
def EncryptionKey(request, *args, **kwargs):
    if request.method == 'POST':
        form = KeyForm(request.POST, request.FILES)
        if form.is_valid():
            password= Cryptographer.derive(form.cleaned_data['password'])
            #(Django stores data on the server side and abstracts the sending and receiving of cookies. The content of what the user actually gets is only the session_id.)
            request.session['key'] = password
            return redirect('file_list')

    else:
        form = KeyForm()
    return render(request, 'keyform.html', {
        'form': form
    })

@otp_required
@key_required
def MyFetchView(request, *args, **kwargs):
    path = kwargs.get("path")

    if not path:
        raise Http404

    full_path = Path(settings.PROJECT_PATH + path)

    if not os.path.exists(full_path): #malicious or deleted
        raise Http404

    with open(full_path, "rb") as f:
            content = f.read()

    #This is a shared file
    if re.search("media/shared_files/",path) :
        f = SharedFile.objects.filter(url=path) 
        #page deleted or malicious attempt
        if not f:
            raise Http404
        else:
            f = f.get()
            
        if not request.user in f.users.all(): #user is trying to access something he shouldn't
            raise Http404

        key_set = []
        key_nbr = 0
        for owner in f.owner_set.all():
            if owner.wants_download and owner.date_key_given:
                key_set.append(Cryptographer.decryptKeyPart(owner.secret_key_given))
                key_nbr+=1
        if key_nbr >= f.minimum_validation:
            try:
                password =  bytes(Cryptographer.recoverKey(key_set), 'utf-8')
                content = Cryptographer.decrypted(content,password)
            except (InvalidToken,ValueError):
                for owner in f.owner_set.all():
                    owner.reset()
                return error_page(request, 'At least one key is incorrect. All saved keys & permissions will be deleted and each user will have to enter them again','shared_file_list')
        else:
            return render(request, 'lockedfile.html', {
                'name': f.name,
                'minimum': f.minimum_validation,
                'nbr' : key_nbr,
                'reason': 'read'
            })

    #This is a user owned file
    else:
        f = File.objects.filter(url=path)
        #page deleted or malicious attempt
        if not f:
            raise Http404
        else:
            f = f.get()

        if f.user.id != request.user.id: #user is trying to access something he shouldn't
            raise Http404

        #the user password is stored in django-session (In django stores data on the server side and abstracts the sending
        # and receiving of cookies. The content of what the user actually gets is only the session_id.)
        password =  bytes(request.session['key'], 'utf-8')
        try:
            content = Cryptographer.decrypted(content,password)
        except InvalidToken:
                return error_page(request, 'The key you previously entered doesn\'t match the one used when you uploaded this file. Please disconnect and enter the proper password.','file_list')
    return HttpResponse(content, content_type= mimetypes.guess_type(path, strict=True)[0] )

 
