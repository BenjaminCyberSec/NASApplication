from django.conf import settings
from django.urls import path, re_path
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls
from two_factor.urls import urlpatterns as tf_urls
from .views import file_list, upload_file, delete_file, new_directory
from .views import (
    ExampleSecretView, HomeView, RegistrationCompleteView, RegistrationView,MyFetchView,EncryptionKey,
)


urlpatterns = [

    path(r"^files/list/(?P<goto>.+)", file_list, name='file_list'),
    path('files/upload/', upload_file, name='upload_file'),
    path('files/newDirectory/', new_directory, name='new_directory'),
    path('files/<int:pk>/', delete_file, name='delete_file'),
    re_path(r"^fetch/(?P<path>.+)",MyFetchView,name='FETCH_URL_NAME'),

    path('encryptionkey/', EncryptionKey, name='encryption_key'),

    url(
        regex=r'^$',
        view=HomeView.as_view(),
        name='home',
    ),
    url(
        regex=r'^account/logout/$',
        view=LogoutView.as_view(),
        name='logout',
    ),
    url(
        regex=r'^secret/$',
        view=ExampleSecretView.as_view(),
        name='secret',
    ),
    url(
        regex=r'^account/register/$',
        view=RegistrationView.as_view(),
        name='registration',
    ),
    url(
        regex=r'^account/register/done/$',
        view=RegistrationCompleteView.as_view(),
        name='registration_complete',
    ),
    url(r'', include(tf_urls)),
    url(r'', include(tf_twilio_urls)),
    url(r'', include('user_sessions.urls', 'user_sessions')),
    url(r'^admin/', admin.site.urls),



]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
    #Are we supposed to store the files elswhere than the device since we make a nas application?
    #if so, put the following line outside of DEBUG
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
