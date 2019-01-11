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



###### Methods relatives to shared files ######

@otp_required
def shared_file_list(request):
    user= request.user.id
    files = SharedFile.objects.prefetch_related('owner_set').filter(users__id=user).all()
    file_list = {}
    for f in files:
       file_list [f] = f.owner_set.filter(user_id=user).get() 
    return render(request, 'shared_file_list.html', {'file_list':file_list})

@otp_required
def upload_shared_file(request):
    if request.method == 'POST':
        owner_formset = OwnerFormSet(request.POST, request.FILES)
        form = SharedFileForm(request.POST, request.FILES)
        if form.is_valid() and owner_formset.is_valid():
            try:
                user = request.user.id
                owners = {}
                minimum_validation = form.cleaned_data.get('minimum_validation')
                if minimum_validation < 2: return error(request, 'The minimum of users minimum to decrypt a shared file is 2')
                for of in owner_formset:
                    owners[User.objects.filter(username=of.cleaned_data.get('name'))[0]]=[]
                owners[User.objects.get(id=user)]=[]
                size = len(owners)
                if size < minimum_validation: return error(request, 'minimum shared requires %s must be lower or equal to the number of owners(you included) %s' % (minimum_validation,size))
                owners = SharedFile.upload_list(request.FILES.getlist('file_field'),owners,minimum_validation,size)
                Email.sendKeys(owners)
                messages.info(request, 'Keys were sent by email and the file was added.')
                return redirect('shared_file_list')
            except IndexError:
                return error(request, 'One of the username entered was unknown')
    else:
        form = SharedFileForm()
        formset = OwnerFormSet()
    return render(request, 'upload_shared_file.html', {
        'form': form, 'formset': formset
    })

@otp_required
def delete_shared_file(request, pk):
    if request.method == 'POST':
        try:
            f = SharedFile.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return error_page(request,'The file has already been deleted', 'shared_file_list')
        if not request.user in f.users.all(): #user is trying to access something he shouldn't
            raise Http404
        key_set = []
        key_nbr = 0
        for owner in f.owner_set.all():
            if owner.wants_deletion and owner.date_key_given:
                key_set += owner.secret_key_given
                key_nbr+=1
        if key_nbr >= f.minimum_validation:
            f.delete()
            return redirect('shared_file_list')
        else:
            return render(request, 'lockedfile.html', {
                'name': f.name,
                'minimum': f.minimum_validation,
                'nbr' : key_nbr,
                'reason': 'delete'
            })
    return redirect('shared_file_list')

@otp_required
def deletion_consent(request, pk):
    if request.method == 'POST':
        try:
            o = Owner.objects.get(user=request.user.id,shared_file=pk)
        except ObjectDoesNotExist:
            return error_page(request,'The file has already been deleted', 'shared_file_list')
        if o.secret_key_given:
            o.grant_deletion()
        else:
            return redirect('shared_key', pk=pk)
    return redirect('shared_file_list')
        

@otp_required
def read_consent(request, pk):
    if request.method == 'POST':
        try:
            o = Owner.objects.get(user=request.user.id,shared_file=pk)
        except ObjectDoesNotExist:
            return error_page(request,'The file has been deleted by an other user or session', 'shared_file_list')
        if o.secret_key_given:
            o.grant_download()
        else:
            return redirect('shared_key', pk=pk)
    return redirect('shared_file_list')
        
@otp_required
def shared_key(request, pk):
    if request.method == 'POST':
        form = KeyForm(request.POST, request.FILES)
        if form.is_valid():
            Owner.objects.get(user=request.user.id,shared_file=pk).setKey( form.cleaned_data['password'])
            messages.info(request,'sharedkey added')
            messages.info(request,'you can now give permissions')
            return redirect('shared_file_list')
    else:
        form = KeyForm()
    return render(request, 'sharedkeyform.html', {
        'form': form
    })