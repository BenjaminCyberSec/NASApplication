from django.conf import settings
from django.urls import path, re_path
from django.conf.urls import include, url
#from django.contrib import admin
from example.admin import admin_site
from django.contrib.auth.views import LogoutView
from django.conf.urls.static import static
from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls
from two_factor.urls import urlpatterns as tf_urls

#Import common views
from .views import (
    ExampleSecretView, HomeView, RegistrationCompleteView, RegistrationView,MyFetchView,EncryptionKey
)
#Import user owned files related views
from .file_views import (
     file_list, upload_file, delete_file,delete_directory,rename_file,rename_directory,
     download_folder,new_directory,change_address,go_back
)
#Import shared files related views
from .shared_file_views import (
    shared_file_list, upload_shared_file, delete_shared_file,deletion_consent,read_consent,shared_key
)


urlpatterns = [

    path('files/list/', file_list, name='file_list'),
    path('files/change_address/<str:name>/', change_address, name='change_address'),
    path('files/upload/', upload_file, name='upload_file'),
    path('files/newDirectory/', new_directory, name='new_directory'),
    path('files/go_back/', go_back, name='go_back'),
    path('files/delete_file/<int:pk>/', delete_file, name='delete_file'),
    path('files/delete_directory/<int:pk>/', delete_directory, name='delete_directory'),
    path('files/rename_file/<int:pk>/<str:name>/', rename_file, name='rename_file'),
    path('files/rename_directory/<int:pk>/<str:name>/', rename_directory, name='rename_directory'),
    path('files/download_folder/<int:pk>/', download_folder, name='download_folder'),
    re_path(r"^fetch(?P<path>.+)",MyFetchView,name='FETCH_URL_NAME'),

    path('shared_files/',shared_file_list, name='shared_file_list'),
    path('shared_files/upload/', upload_shared_file, name='upload_shared_file'),
    path('shared_files/<int:pk>/', delete_shared_file, name='delete_shared_file'),
    path('shared_files/deletion_consent/<int:pk>/', deletion_consent, name='deletion_consent'),
    path('shared_files/read_consent/<int:pk>/', read_consent, name='read_consent'),
    path('shared_files/shared_key/<int:pk>/', shared_key, name='shared_key'),

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
    url(r'^accounts/', include('registration.backends.admin_approval.urls')),



]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
