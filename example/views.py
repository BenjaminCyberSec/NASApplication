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
from .decorators import key_required

from .forms import FileForm,KeyForm,SharedFileForm,OwnerFormSet
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


###### Methods relatives to files own by one user ######

@otp_required
@key_required
def file_list(request):
    user= request.user.id
    files = File.objects.filter(user = User.objects.get(id=user))
    return render(request, 'file_list.html', {
        'files': files
    })

@otp_required
@key_required
def upload_file(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            user= request.user.id
            for f in request.FILES.getlist('file_field'):
                data =f
                TemporaryKeyHandler.addFile(user, data.name)

                File(name =  data.name,
                size = data.size/1000,
                modification_date = datetime.datetime.now(),
                file = data,
                user = User.objects.get(id=user)).save()
            return redirect('file_list')
    else:
        form = FileForm()
    return render(request, 'upload_file.html', {
        'form': form
    })

@otp_required
@key_required
def delete_file(request, pk):
    if request.method == 'POST':
        file = File.objects.get(pk=pk)
        file.delete()
    return redirect('file_list')



###### Methods relatives to shared files ######

@otp_required
def shared_file_list(request):
    user= request.user.id
    files = SharedFile.objects.filter(owners__id=user)
    return render(request, 'shared_file_list.html', {
        'files': files
    })

@otp_required
def upload_shared_file(request):
    if request.method == 'POST':
        owner_formset = OwnerFormSet(request.POST, request.FILES)
        form = SharedFileForm(request.POST, request.FILES)
        if form.is_valid() and owner_formset.is_valid():
            try:
                user = request.user.id
                owners = {}
                shares = []
                minimum_validation = form.cleaned_data.get('minimum_validation')
                for of in owner_formset:
                    owners[User.objects.filter(username=of.cleaned_data.get('name'))[0]]=[]
                owners[User.objects.get(id=user)]=[]
                size = len(owners)

                for data in request.FILES.getlist('file_field'):
                    key = Cryptographer.generateKey()
                    TemporaryKeyHandler.addSharedFile(key,data.name)
                    print(owners)
                    print(minimum_validation) 
                    print(size)
                    s=Cryptographer.shareKey(key, minimum_validation,size)
                    s+=data.name
                    shares.append(s)
                    
                    sh = SharedFile(name =  data.name,
                    size = data.size/1000,
                    modification_date = datetime.datetime.now(),
                    file = data,
                    nb_owners = size,
                    minimum_validation = minimum_validation)
                    sh.save()
                    for owner in owners:
                        Owner(user= owner,shared_file=sh ).save()
                Email.sendKeys(shares,owners)
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
        file = SharedFile.objects.get(pk=pk)
        file.delete()
    return redirect('shared_file_list')



class HomeView(TemplateView):
    template_name = 'home.html'


class RegistrationView(FormView):
    template_name = 'registration.html'
    form_class = UserCreationForm

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
        full_path ='http://127.0.0.1:8000' + path #when we stock this on the same machine

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

    if re.search("media/shared_files/",path) :
        f = SharedFile.objects.filter(url=path)[0]
        if not request.user in f.owners.all(): #user is trying to access something he shouldn't
            raise Http404
        print("access granted")
        
    else:
        f = File.objects.filter(url=path)[0]
        if f.user.id != request.user.id: #user is trying to access something he shouldn't
            raise Http404

        #the user password is stored in django-session (In django stores data on the server side and abstracts the sending
        # and receiving of cookies. The content of what the user actually gets is only the session_id.)
        password =  bytes(request.session['key'], 'utf-8')
        content = Cryptographer.decrypted(content,password)

    return HttpResponse(content, content_type= mimetypes.guess_type(path, strict=True)[0] )

 
