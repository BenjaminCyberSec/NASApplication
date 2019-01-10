from functools import wraps
from django.http import HttpResponseRedirect
from .temporary_key_handler import TemporaryKeyHandler
import re

def key_required(function):
  @wraps(function)
  def wrap(request, *args, **kwargs):
    #if we want to read a file that is shared between users the user_key is not necessary
    if 'path' in kwargs and re.search("media/shared_files/",kwargs.get("path")) :
        return function(request, *args, **kwargs)

    #redirect to a form asking for the key if the user key isn't in the session
    if 'key' in request.session:
        TemporaryKeyHandler.addUser(request.user.id,request.session['key'])
        return function(request, *args, **kwargs)
    else:
        return HttpResponseRedirect('/encryptionkey')
  return wrap

def file_address(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if 'file_address' in request.session:
            return function(request, *args, **kwargs)
        else:
            request.session['file_address'] = ""
            return function(request, *args, **kwargs)
    return wrap
