from .base import *

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1','192.168.100.58','192.168.30.41']

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': '5432',
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

EMAIL_PORT = 465
#EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'cfrd.support@nrbcommercialbank.com'
EMAIL_HOST_PASSWORD = 'Dhaka@1234'
DEFAULT_FROM_EMAIL='cfrd.support@nrbcommercialbank.com'
#ADMINS=[('Navid', 'kazinavidanzum@nrbcommercialbank.com'), ('Chakibbai', 'nazmussaqib@nrbcommercialbank.com')]
#MANAGERS=[('Navid', 'kazinavidanzum@nrbcommercialbank.com'), ('Chakibbai', 'nazmussaqib@nrbcommercialbank.com')]


################################ Configurations #########################################
IMAGE_UPLOAD_REQUIRED = True
