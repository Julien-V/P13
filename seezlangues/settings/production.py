#!/usr/bin/python3
# coding : utf-8

import os

from .base import *

DEBUG = False

ALLOWED_HOSTS = ['localhost']

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'seezlangues',
    }
}


# SECURE_SSL_REDIRECT = True
# SESSION__COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_BROWSER_XSS_FILTER = True
