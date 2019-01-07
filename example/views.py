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

from .forms import FileForm,KeyForm,NewDirectoryForm
from .models import File

from .crypt import Cryptographer

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


@otp_required
@file_address
def file_list(request, *args, **kwargs):
    goto = kwargs.get("goto")
    if goto:
        request.session['file_address'] = request.session['file_address']+"/"+goto
        print("goto parameter passed")
    print(request.session['file_address'])
    user = request.user.id
    files = File.objects.filter(user = User.objects.get(id=user),file_address = request.session['file_address'])
    return render(request, 'file_list.html', {
        'files': files,
        'address': request.session['file_address'],
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
                Cryptographer.addFile(user, data.name)
                File(name =  data.name,
                size = data.size/1000,
                modification_date = datetime.datetime.now(),
                file = data,
                category = "Fichier",
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
            Cryptographer.addFile(user, directory_name)
            File(name =  directory_name,
            size = 0,
            modification_date = datetime.datetime.now(),
            file = 0,
            category = "Dossier",
            address = request.session['file_address'],
            user = User.objects.get(id=user)).save()
            return redirect('file_list')
    else:
        form = NewDirectoryForm()
    return render(request, 'new_directory.html', {
        'form': form
    })

@otp_required
def delete_file(request, pk):
    if request.method == 'POST':
        file = File.objects.get(pk=pk)
        file.delete()
    return redirect('file_list')



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
            Cryptographer.addUser(user,password) #move to connection
            return redirect('file_list')

    else:
        form = KeyForm()
    return render(request, 'keyform.html', {
        'form': form
    })

@otp_required
@key_required
def MyFetchView(request, *args, **kwargs):
    """
    Limit user access to this view has to be added,
    check if they own the files
    """


    def is_url(path):
        try:
            URLValidator()(path)
            return True
        except ValidationError:
            return False

    path = kwargs.get("path")

    #keep for right verification, might be needed
    #result = File.objects.all().files.urls#.filter(url=path)[0]
    #result = File.objects.raw('SELECT eu.id FROM example_user eu, example_files ef where eu.file = ef.id and ef.url = \"'+path+'\"')
    #result = User.objects.raw('SELECT * FROM auth_user u')[0]
    #result = File.objects.raw('SELECT * FROM example_file f ')[0]
    #print(result.file)

    if not path:
        raise Http404
    else:
        path ='http://127.0.0.1:8000' + path #when we stock this on the same machine

    if is_url(path):

        content = requests.get(path, stream=True).raw.read()

    else:

        # Normalise the path to strip out naughty attempts
        path = os.path.normpath(path).replace(
            settings.MEDIA_URL, settings.MEDIA_ROOT, 1)

        # Evil path request!
        if not path.startswith(settings.MEDIA_ROOT):
            raise Http404

        # The file requested doesn't exist locally.  A legit 404
        if not os.path.exists(path):
            raise Http404

        with open(path, "rb") as f:
            content = f.read()

    #stored in django-session (In django stores data on the server side and abstracts the sending
    # and receiving of cookies. The content of what the user actually gets is only the session_id.)
    if not 'key' in request.session:
        raise Http404
    password =  bytes(request.session['key'], 'utf-8')

    content = Cryptographer.decrypted(content,password)
    return HttpResponse(content, content_type= mimetypes.guess_type(path, strict=True)[0] )
