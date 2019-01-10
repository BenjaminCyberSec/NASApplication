from django.contrib import messages
from django.http import HttpResponseRedirect
import logging

logger = logging.getLogger('django')

def error(request, message):
    logger.error('%s :: %s' % (request.user.id,message))
    messages.error(request,message)
    return HttpResponseRedirect(request.path_info)