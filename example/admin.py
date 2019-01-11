from django.contrib.admin import AdminSite
from django.http import HttpResponseRedirect
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib import messages
from .forms import UserValidationSet
from django.contrib import messages
from .emails import Email


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
                for form in formset:
                    if('is_active' in form.cleaned_data and form.initial['is_active'] != form.cleaned_data['is_active']):
                        if(form.cleaned_data['is_active']):
                            Email.activation(form['email'])
                        else: 
                            Email.deactivation(form['email'])
                
                        
                formset.save()
                messages.info(request, 'Changes were saved! Email sent.')
            
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
            if not instance.is_staff:
                instance.is_active = False
        else:
            #if it's an update check if it's the activation to send email
            print(kwargs)
            print(instance.is_active)
                



admin_site = MyAdminSite()