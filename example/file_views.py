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
import os
from threading import Timer


###### Methods relatives to files own by one user ######

@otp_required
@key_required
@file_address
def file_list(request):
    user = request.user.id
    files = File.objects.filter(user = User.objects.get(id=user),address = request.session['file_address'])
    return render(request, 'file_list.html', {
        'files': files,
        'address': request.session['file_address'],
    })

@otp_required
@key_required
@file_address
def change_address(request,name):
    request.session['file_address'] = request.session['file_address']+"/"+name
    return redirect('file_list')

@otp_required
@key_required
@file_address
def go_back(request):
    file_address = request.session['file_address']
    if len(file_address) != 0:
        address_split = file_address.split('/')
        address_split = address_split[:-1]
        address_split = '/'.join(address_split)
        request.session['file_address'] = address_split
    return redirect('file_list')

@otp_required
@key_required
def upload_file(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            user_id= request.user.id
            for f in request.FILES.getlist('file_field'):
                data =f
                name = data.name
                i = 0
                while len(File.objects.filter(user = User.objects.get(id=user_id),address = request.session['file_address'],name =  name)) != 0:
                    if i > 0:
                        name = name[1:]
                    name = str(i)+name
                    i += 1
                data.name = name
                TemporaryKeyHandler.addFile(user_id, str(data))
                File(name =  name,
                size = data.size/1000,
                modification_date = datetime.now(),
                file = data,
                category = "File",
                address = request.session['file_address'],
                user = User.objects.get(id=user_id)).save()
            return redirect('file_list')
    else:
        form = FileForm()
    return render(request, 'upload_file.html', {
        'form': form
    })

@otp_required
def new_directory(request):
    if request.method == 'POST':
        form =NewDirectoryForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user.id
            directory_name = form.cleaned_data['directory_name']
            i = 0
            while len(File.objects.filter(user = User.objects.get(id=user),address = request.session['file_address'],name =  directory_name)) != 0:
                if i > 0:
                    directory_name = directory_name[:-1]
                directory_name += str(i)
                i += 1
            TemporaryKeyHandler.addFile(user, directory_name)
            File(name =  directory_name,
            size = 0,
            modification_date = datetime.now(),
            file = 0,
            category = "Directory",
            address = request.session['file_address'],
            user = User.objects.get(id=user)).save()
            return redirect('file_list')
    else:
        form = NewDirectoryForm()
    return render(request, 'new_directory.html', {
        'form': form
    })

@otp_required
@key_required
def rename_file(request, pk, name):
    if request.method == 'POST':
        form = RenameForm(request.POST, request.FILES)
        if form.is_valid():
            File.objects.get(pk=pk).rename(form.cleaned_data['new_name'],request.user.id, request.session['file_address'])
            return redirect('file_list')
    else:
        form = RenameForm()
    return render(request, 'rename_file.html', {
        'form': form,
        'name': name,
        'pk': pk,
    })

    
@otp_required
@key_required
def rename_directory(request, pk, name):
    if request.method == 'POST':
        form = RenameForm(request.POST, request.FILES)
        if form.is_valid():
            root_file = File.objects.get(pk=pk)
            root_file.address
            full_address = root_file.address + "/" + root_file.name
            my_regex = r"^" + re.escape(full_address) + r".*"
            subdirectory_files = File.objects.filter(address__regex = my_regex)
            new_name = form.cleaned_data['new_name']
            i = 0
            user= request.user.id
            while len(File.objects.filter(user = User.objects.get(id=user),address = request.session['file_address'],name =  new_name)) != 0:
                if i > 0:
                    new_name = new_name[1:]
                new_name = str(i)+new_name
                i += 1
            File.objects.filter(pk=pk).update(name = new_name)
            for file in subdirectory_files:
                new_address = file.address.split(name)
                new_address = new_name.join(new_address)
                File.objects.filter(pk=file.pk).update(address = new_address)
            return redirect('file_list')
    else:
        form = RenameForm()
    return render(request, 'rename_file.html', {
        'form': form,
        'name': name,
        'pk': pk,
    })

@otp_required
@key_required
def delete_file(request, pk):
    if request.method == 'POST': 
        try:
            file = File.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return error_page(request,'The file has already been deleted', 'file_list')
        file.delete()
    return redirect('file_list')

@otp_required
@key_required
@file_address
def delete_directory(request, pk):
    if request.method == 'POST':
        try:
            root_file = File.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return error_page(request,'The folder has already been deleted', 'file_list')
        full_address = root_file.address + "/" + root_file.name
        my_regex = r"^" + re.escape(full_address) + r".*"
        subdirectory_files = File.objects.filter(address__regex = my_regex)
        for file in subdirectory_files:
            file.delete()
        root_file.delete()
    return redirect('file_list')

@otp_required
@key_required
@file_address
def download_folder(request, pk):

    def delete_zip_server_side(zip_name):
        if os.path.exists(zip_name):
            os.remove(zip_name)
        else:
            print(zip_name + " was not found")
    if request.method == 'GET':
        root_file = File.objects.get(pk=pk)
        full_address = root_file.address + "/" + root_file.name
        my_regex = r"^" + re.escape(full_address) + r".*"
        subdirectory_files = File.objects.filter(address__regex = my_regex)
        compression = zipfile.ZIP_DEFLATED
        zip_filename = root_file.name + ".zip"
        zip_deletion = Timer(5,delete_zip_server_side,args=(zip_filename,))
        zf = zipfile.ZipFile(zip_filename, "w") 
        password =  bytes(request.session['key'], 'utf-8')
        try:
            for file in subdirectory_files:
                if file.category == "File" :
                    file_url =  file.file.url.split("/")
                    file_url = file_url[2:]
                    file_url = "/".join(file_url)
                    with open(Path(settings.SERVER_PATH + file_url), "rb") as f:
                        content = f.read()
                    try:
                        content = Cryptographer.decrypted(content,password)
                    except InvalidToken:
                        return error_page(request, 'The key you previously entered doesn\'t match the one used when you uploaded this file. Please disconnect and enter the proper password.','file_list')
                    
                    zf.writestr(file.name,content)

        except FileNotFoundError:
            print("An error occurred")
        finally:
            # Don't forget to close the file!
            zf.close()
        zip_name = zf.filename
        print(zip_filename)
        f = open(zip_filename, "rb")
        response = HttpResponse(f, content_type='application/x-zip')
        response['Content-Disposition'] = 'attachment; filename="%s"' % zip_name
        #zip_deletion will delete the local zip file in 5 second.
        zip_deletion.start()
        return response
    return redirect('file_list')
