from functools import wraps
from django.http import HttpResponseRedirect


def key_required(function):
  @wraps(function)
  def wrap(request, *args, **kwargs):
    if 'key' in request.session:
        return function(request, *args, **kwargs)
    else:
        return HttpResponseRedirect('/encryptionkey')
  return wrap