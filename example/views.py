from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, resolve_url,render
from django.views.decorators.cache import never_cache
from django.views.generic import FormView, TemplateView, ListView, CreateView

from two_factor.views import OTPRequiredMixin
from two_factor.views.utils import class_view_decorator

#from django.shortcuts import render, redirect
#from django.views.generic import TemplateView, ListView, CreateView
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy
from django_otp.decorators import otp_required

from .forms import FileForm
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


@otp_required
def file_list(request):
    files = File.objects.all()
    return render(request, 'file_list.html', {
        'files': files
    })

@otp_required
def upload_file(request):
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            password= Cryptographer.derive(form.cleaned_data['password'])
            data = form.cleaned_data['file']
            user= request.user.id
            
            Cryptographer.addUser(user,password) #move to connection or something #put in session?
            Cryptographer.addFile(user, data.name)

            File(name =  data.name,
            size = data.size/1000,
            modification_date = datetime.datetime.now(),
            file = data,
            user = User.objects.get(user)).save()
            return redirect('file_list')
    else:
        form = FileForm()
    return render(request, 'upload_file.html', {
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

def MyFetchView(request, *args, **kwargs):
    """
    This is a generic, insecure view that effectively undoes any security made
    available via this module.  To make it useful, you have to subclass it and
    make use of your own rules or simply rely on the auth mixins provided by
    Django:
      from django.contrib.auth.mixins import LoginRequiredMixin
      from django_encrypted_fields.views import FetchView as BaseFetchView
      class FetchView(LoginRequiredMixin, BaseFetchView):
          pass
    Using LoginRequiredMixin would effectively allow anyone with a site login
    to view *all* files, while using something like StaffRequiredMixin would
    mean that only staff members could read the file.
    Theoretically you could also write your view to be smart enough to take the
    requested path and match it against a list of permissions, allowing you to
    set out per-user permissions whilst still only using one encryption key for
    the whole site.
    """

    
    def is_url(path):
        try:
            URLValidator()(path)
            return True
        except ValidationError:
            return False

    path = kwargs.get("path")
    result = File.objects.files.urls #.filter(url=path)[0]
    print(result)

    
    # No path?  You're boned.  Move along.
    if not path:
        raise Http404
    else:
        path ='http://127.0.0.1:8000' + path #to put in dev only

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
    
    password = bytes("password", 'utf-8')
    salt = bytes("salt", 'utf-8')
    content = Cryptographer.decrypted(content,salt,password)
    return HttpResponse(content, content_type= mimetypes.guess_type(path, strict=True)[0] )
