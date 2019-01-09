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

import datetime
import mimetypes

import os
from django.conf import settings
from django.core.validators import URLValidator, ValidationError
from django.http import Http404, HttpResponse
from django.views.generic import View
import requests
from django.contrib.auth.models import User

from .constants import SESSION_TTL

from django.forms import formset_factory
from .emails import Email
from django.http import JsonResponse
import re

from django.shortcuts import redirect

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
    #print(request.session['file_address'])
    return redirect('file_list')

@otp_required
@key_required
@file_address
def go_back(request):
    file_address = request.session['file_address']
    if len(file_address) != 0:
        #print(file_address)
        address_split = file_address.split('/')
        address_split = address_split[:-1]
        address_split = '/'.join(address_split)
        #print(address_split)
        request.session['file_address'] = address_split
    return redirect('file_list')

@otp_required
@key_required
def upload_file(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            user= request.user.id
            for f in request.FILES.getlist('file_field'):
                data =f
                name = data.name
                i = 0
                while len(File.objects.filter(user = User.objects.get(id=user),address = request.session['file_address'],name =  name)) != 0:
                    if i > 0:
                        name = name[1:]
                    name = str(i)+name
                    i += 1
                print(name)
                print(TemporaryKeyHandler.addFile(user, name))
                #print(name)
                File(name =  name,
                size = data.size/1000,
                modification_date = datetime.datetime.now(),
                file = data,
                category = "File",
                address = request.session['file_address'],
                user = User.objects.get(id=user)).save()
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
            modification_date = datetime.datetime.now(),
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
        print("dans POST")
        print(pk)
        print(name)
        form = RenameForm(request.POST, request.FILES)
        if form.is_valid():
            new_name = form.cleaned_data['new_name']
            print(new_name)
            i = 0
            while len(File.objects.filter(user = User.objects.get(id=user),address = request.session['file_address'],name =  new_name)) != 0:
                if i > 0:
                    new_name = new_name[1:]
                new_name = str(i)+new_name
                i += 1
            File.objects.filter(pk=pk).update(name = new_name)
            return redirect('file_list')
    else:
        print("dans GET")
        print(pk)
        print(name)
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
        print("dans POST")
        print(pk)
        print(name)
        form = RenameForm(request.POST, request.FILES)
        if form.is_valid():
            root_file = File.objects.get(pk=pk)
            root_file.address
            full_address = root_file.address + "/" + root_file.name
            my_regex = r"^" + re.escape(full_address) + r".*"
            subdirectory_files = File.objects.filter(address__regex = my_regex)
            new_name = form.cleaned_data['new_name']
            #print(new_name)
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
                print(new_address)
                print(file.address)
                File.objects.filter(pk=file.pk).update(address = new_address)
            return redirect('file_list')
    else:
        print("dans GET")
        print(pk)
        print(name)
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
        file = File.objects.get(pk=pk)
        file.delete()
    return redirect('file_list')

@otp_required
@key_required
@file_address
def delete_directory(request, pk):
    if request.method == 'POST':
        root_file = File.objects.get(pk=pk)
        root_file.address
        full_address = root_file.address + "/" + root_file.name
        my_regex = r"^" + re.escape(full_address) + r".*"
        subdirectory_files = File.objects.filter(address__regex = my_regex)
        for file in subdirectory_files:
            file.delete()
        root_file.delete()
    return redirect('file_list')


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
                for of in owner_formset:
                    owners[User.objects.filter(username=of.cleaned_data.get('name'))[0]]=[]
                owners[User.objects.get(id=user)]=[]
                size = len(owners)

                for data in request.FILES.getlist('file_field'):
                    key = Cryptographer.generateKey()
                    TemporaryKeyHandler.addSharedFile(key,data.name)
                    s=Cryptographer.shareKey(key, minimum_validation,size)
                    i=0
                    for k,v in owners.items():
                        v.append(data.name)
                        v.append(s[i])
                        i+=1
                    sh = SharedFile(name =  data.name,
                    size = data.size/1000,
                    modification_date = datetime.datetime.now(),
                    file = data,
                    nb_owners = size,
                    minimum_validation = minimum_validation)
                    sh.save()
                    for user in owners.keys():
                        Owner(user= user,shared_file=sh ).save()
                Email.sendKeys(owners)
                return redirect('shared_file_list')
            except IndexError:
                status_code = 400
                message = "The request is not valid."
                explanation = "You entered a username that is not in use."
                return JsonResponse({'message':message,'explanation':explanation}, status=status_code)
    else:
        form = SharedFileForm()
        formset = OwnerFormSet()
    return render(request, 'upload_shared_file.html', {
        'form': form, 'formset': formset
    })

@otp_required
def delete_shared_file(request, pk):
    if request.method == 'POST':
        f = SharedFile.objects.get(pk=pk)
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
        o = Owner.objects.filter(user=request.user.id,shared_file=pk)[0]
        if o.secret_key_given:
            o.wants_deletion = True
            o.save()
        else:
            return redirect('shared_key', pk=pk)
    return redirect('shared_file_list')
        

@otp_required
def read_consent(request, pk):
    if request.method == 'POST':
        o = Owner.objects.filter(user=request.user.id,shared_file=pk)[0]
        if o.secret_key_given:
            o.wants_download = True
            o.save()
        else:
            return redirect('shared_key', pk=pk)
    return redirect('shared_file_list')
        
@otp_required
def shared_key(request, pk):
    if request.method == 'POST':
        form = KeyForm(request.POST, request.FILES)
        if form.is_valid():
            password= form.cleaned_data['password']
            o = Owner.objects.filter(user=request.user.id,shared_file=pk)[0]
            o.date_key_given = datetime.datetime.now()
            o.secret_key_given = Cryptographer.encryptKeyPart(password)
            o.save()
            return redirect('shared_file_list')
    else:
        form = KeyForm()
    return render(request, 'sharedkeyform.html', {
        'form': form
    })
            


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
            user= request.user.id
            password= Cryptographer.derive(form.cleaned_data['password'])
            #(Django stores data on the server side and abstracts the sending and receiving of cookies. The content of what the user actually gets is only the session_id.)
            request.session['key'] = password#.decode("utf-8") #move to connection
            request.session.set_expiry(SESSION_TTL)
            TemporaryKeyHandler.addUser(user,password) #move to connection
            return redirect('file_list')

    else:
        form = KeyForm()
    return render(request, 'keyform.html', {
        'form': form
    })

@otp_required
@key_required
def MyFetchView(request, *args, **kwargs):

    def is_url(path):
        try:
            URLValidator()(path)
            return True
        except ValidationError:
            return False

    path = kwargs.get("path")

    if not path:
        raise Http404
    else:
        full_path=re.sub('/fetch', '', request.build_absolute_uri())
    if is_url(full_path):
        content = requests.get(full_path, stream=True).raw.read()

    else:

        # Normalise the path to strip out naughty attempts
        full_path = os.path.normpath(full_path).replace(
            settings.MEDIA_URL, settings.MEDIA_ROOT, 1)

        # Evil path request!
        if not full_path.startswith(settings.MEDIA_ROOT):
            raise Http404

        # The file requested doesn't exist locally.  A legit 404
        if not os.path.exists(full_path):
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
            password =  bytes(Cryptographer.recoverKey(key_set), 'utf-8')
            content = Cryptographer.decrypted(content,password)
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
        content = Cryptographer.decrypted(content,password)
    return HttpResponse(content, content_type= mimetypes.guess_type(path, strict=True)[0] )

 
