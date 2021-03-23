"""
Django settings for report project.

Generated by 'django-admin startproject' using Django 2.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
######### Required for python decouple#######################
from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Application definition

INSTALLED_APPS = [
    'rem.apps.RemConfig',
    'schedules.apps.SchedulesConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    ########################## Additional Apps###################################
    'widget_tweaks',
    #Crsipy forms,
    'crispy_forms',
    #Rules
    'rules',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'report.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'report.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

#LANGUAGE_CODE = 'en-us'

#USE_THOUSAND_SEPARATOR = True
#NUMBER_GROUPING = (3, 2, 0)

TIME_ZONE = 'Asia/Dhaka'

#USE_I18N = True

#USE_L10N = True

USE_TZ = True

DATE_FORMAT = 'd/m/Y'

SHORT_DATETIME_FORMAT = 'm/d/Y P'
#DATETIME_FORMAT= '%Y-%m-%d %H:%M:%S'





#User registration and Authentication

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

LOGOUT_REDIRECT_URL='login'
LOGIN_REDIRECT_URL='index'

######################### Rem app sepcific settings##############################

MAXIMUM_USER_PER_BRANCH=10
MAXIMUM_USER_PER_BOOTH=5
MAXIMUM_USER_HEAD_OFFICE=10

############################ django-registration settings ##############################

ACCOUNT_ACTIVATION_DAYS = 2

####################### Crispy Forms #############################
CRISPY_TEMPLATE_PACK = 'bootstrap4'