from .base import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool)

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
DEFAULT_FROM_EMAIL='no-reply@cfrdsnrbc.com'
ADMINS=[('Navid', 'kazinavidanzum@nrbcommercialbank.com'), ('Chakibbai', 'nazmussaqib@nrbcommercialbank.com')]
MANAGERS=[('Navid', 'kazinavidanzum@nrbcommercialbank.com'), ('Chakibbai', 'nazmussaqib@nrbcommercialbank.com')]
