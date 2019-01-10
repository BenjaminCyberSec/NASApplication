from django.contrib.admin import AdminSite
from django.http import HttpResponseRedirect
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib import messages
from .forms import UserValidationSet
from django.contrib import messages

class MyAdminSite(AdminSite):

    #custom url
    def get_urls(self):
        from django.conf.urls import url
        urls = super(MyAdminSite, self).get_urls()
        urls += [
            url(r'^registration_validation/$', self.admin_view(self.validation_view))
        ]
        return urls

    #form
    def validation_view(self, request):
        if request.method == 'POST':
            formset = UserValidationSet(request.POST)
            if formset.is_valid():
                formset.save()
                messages.info(request, 'Changes were saved! Come again.')
            
            return HttpResponseRedirect(request.path_info)
    

        formset = UserValidationSet()
        return render(request, 'user_confirmation.html', {
            'formset': formset
        })
    



    #get a signal when a user is saved
    #(quick hack to not have to redefine 2FA)
    @classmethod
    @receiver(pre_save, sender=User)
    def set_new_user_inactive(sender, instance, **kwargs):
        if instance._state.adding is True: #set as inactive if he is new
            instance.is_active = False
        #else
            #do nothing if it's an update



admin_site = MyAdminSite()