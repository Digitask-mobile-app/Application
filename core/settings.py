"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 5.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-dj@g@p0zq76f6=wplo@znnuzclq4v=($p=ky@+x=$rx!9as@f2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

CORS_ALLOWED_ORIGINS = [
    'http://135.181.42.192',
    'http://135.181.42.192:100',
    'http://localhost:5173',
]

# Application definition
CSRF_TRUSTED_ORIGINS = [
    'http://135.181.42.192',
    'http://135.181.42.192:100',
    'http://localhost:5173',
]


# Application definition

CKEDITOR_CONFIGS = {
    "default": {
        "versionCheck": False
    }
}

SILENCED_SYSTEM_CHECKS = ['ckeditor.W001']

INSTALLED_APPS = [
    'daphne',
    'channels',
    # 'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    # 'mapwidgets',
    'drf_yasg',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'corsheaders',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    #myapps
    'accounts',
    "services",
]

ASGI_APPLICATION = 'core.asgi.application'
WSGI_APPLICATION = 'core.wsgi.application'

SITE_ID = 1

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("135.181.42.192", 100), ("135.181.42.192", 80), ('localhost', 5173), ('127.0.0.1', 8000)],
        },
    },
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'services.middleware.languages.SetDefaultLangMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware'
]

CORS_ORIGIN_WHITELIST = [
    'http://localhost:5173',
]


CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True


SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        }
    }
}

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
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

AUTH_USER_MODEL='accounts.User'

REST_FRAMEWORK={
    'NON_FIELD_ERRORS_KEY':'error',
        'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (  
    'rest_framework.authentication.SessionAuthentication',
    'rest_framework.authentication.BasicAuthentication',
    'rest_framework_simplejwt.authentication.JWTAuthentication', 
    'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ],
}




GDAL_LIBRARY_PATH = 'C:\\Program Files\\GDAL\\gdalxxx.dll'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

DOMAIN='localhost:3000'
SITE_NAME = 'Henry Ultimate Authentication Course'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'aytacmehdizade08@gmail.com'
EMAIL_HOST_PASSWORD = 'pful vvvc uhib hxup'
EMAIL_PORT = 587
EMAIL_USE_TLS=True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


from django.utils.translation import gettext_lazy as _


LANGUAGES = [
    ('az', _('Az')),
    ('en', _('En')),
]

MODELTRANSLATION_DEFAULT_LANGUAGE = 'az'
PARLER_LANGUAGES = {
    None : (
        {'code': 'az',},
        {'code': 'en',},
    ),
    'default': {
        'fallbacks': [],
        'hide_untranslated': False,
    }
}
LANGUAGE_CODE = 'az'
MODELTRANSLATION_DEFAULT_LANGUAGE = 'az'
DEFAULT_LANGUAGE = 'az'

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

TIME_ZONE = 'Asia/Baku'
SITE_ID = 1

USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'

# STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'PATCH',  
    'DELETE',
    'OPTIONS',
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "content-type",
    "authorization",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "token",
]


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "app",
        },
    },
    "formatters": {
        "app": {
            "format": (
                "%(asctime)s [%(levelname)-8s]" "(%(module)s.%(funcName)s) %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO"},
    },
}
