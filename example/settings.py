import os


DEBUG = True

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

MEDIA_URL = '/media/'

SERVER_PATH = os.getcwd() + '/example/'

#PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(PROJECT_PATH, 'database.sqlite'),
#    }
#}


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_PATH, 'db.sqlite3'),
    }
}


#STATIC_URL = '/static/'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

TIME_ZONE = 'Europe/Brussels'

# Make this unique, and don't share it with anybody.
#This key is required by django
#CHANGE THIS IN PROD
SECRET_KEY = 'NASr(-7kmnxko$t+odw4yzu6u^$*~-7%h0w@7t_(_r@l75_b&6*&gasjmCYbER'

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'user_sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'two_factor.middleware.threadlocals.ThreadLocals',

    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

)

ROOT_URLCONF = 'example.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_PATH, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'user_sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    'example',
    'registration',
    'debug_toolbar',
    'bootstrapform',
    'crispy_forms',
)

CRISPY_TEMPLATE_PACK = 'bootstrap4'

LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'two_factor:login'
LOGIN_REDIRECT_URL = 'two_factor:profile'

INTERNAL_IPS = ('127.0.0.1',)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': PROJECT_PATH + '/logs/all.log',
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        }
    }
}


TWO_FACTOR_CALL_GATEWAY = 'example.gateways.Messages'
TWO_FACTOR_SMS_GATEWAY = 'example.gateways.Messages'



#PHONENUMBER_DEFAULT_REGION = 'BE'

PHONENUMBER_DEFAULT_REGION = 'BE'

SESSION_ENGINE = 'user_sessions.backends.db'
SESSION_COOKIE_AGE = 3600

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL = 'noreply@nasapp.be'

#EMAIL_HOST
#EMAIL_PORT
#EMAIL_HOST_USER
#EMAIL_HOST_PASSWORD
#EMAIL_USE_TLS
# EMAIL_USE_SSL

#Django-registrationr-edux settings

ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_AUTO_LOGIN = False
#REGISTRATION_ADMINS = ['niwei.wang@gmail.com','niwei.wang@outlook.com']


ADMINS = (
    ('admin1', 'niwei.wang@gmail.com'),
    ('admin2', 'niwei.wang@outlook.com'),
)


REGISTRATION_ADMINS = (
    ('admin1', 'niwei.wang@gmail.com'),
    ('admin2', 'niwei.wang@outlook.com'),
)



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_ROOT = os.path.join(PROJECT_PATH, 'staticfiles')

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(PROJECT_PATH, 'static')
]

MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

try:
    from .settings_private import *  # noqa
except ImportError:
    pass
