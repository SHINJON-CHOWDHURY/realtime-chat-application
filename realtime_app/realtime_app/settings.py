
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# MEDIA_URL = "media/"
# MEDIA_ROOT = BASE_DIR / "media"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^+zc+289wowx2l5ypn=dgx-raxy^=q(it@)4k5!!5!$be76-y1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "founder-coins-forming-feof.trycloudflare.com",
]

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "https://founder-coins-forming-feof.trycloudflare.com",
]
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'allauth',
       'allauth.account',
       'allauth.socialaccount',
       'allauth.socialaccount.providers.google',

    'channels',
    'chatclear',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ROOT_URLCONF = 'realtime_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'realtime_app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'realtime_chat_db',
        'USER': 'postgres',
        'PASSWORD': 'iboyshinjon',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'

WSGI_APPLICATION = 'realtime_app.wsgi.application'

ASGI_APPLICATION = 'realtime_app.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",

        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
LOGIN_URL = '/login/'
SITE_ID = 1

# LOGIN_REDIRECT_URL = '/'
# LOGOUT_REDIRECT_URL = '/login/'

ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']

SOCIALACCOUNT_LOGIN_ON_GET = True

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(
    BASE_DIR,
    "media"
)