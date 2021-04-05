from .base import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'l=0zslut0dp9)(w1_3fl5ux#z&3i44n37ktqw=tlmb=+ygl4=x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1','192.168.100.58']

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
"""STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]"""
STATIC_ROOT = os.path.join(BASE_DIR, "static")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = '/media/'

######################### Email Settings##############################

#EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
#EMAIL_FILE_PATH = os.path.join(BASE_DIR, "sent_emails")
EMAIL_HOST = '192.168.50.54'
#EMAIL_HOST_USER = 'kazinavidanzum@nrbcommercialbank.com'

EMAIL_PORT = 25
######################### Rem app sepcific settings##############################

MAXIMUM_USER_PER_BRANCH=2

############################ django-registration settings ##############################

ACCOUNT_ACTIVATION_DAYS = 2


################################ Configurations #########################################
IMAGE_UPLOAD_REQUIRED = True
