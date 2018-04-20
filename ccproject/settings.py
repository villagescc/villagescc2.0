"""
Django settings for ccproject project.

Generated by 'django-admin startproject' using Django 1.9.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import elasticsearch
import ujson
from envparse import env
from datetime import timedelta
from database.databases import Database
from database.connection_strings import POSTGRESQL

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['villages.io']

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'ccproject', 'locale/'),
)

if os.path.isfile('.env'):
    env.read_envfile('.env')

MAILCHIMP_APIKEY = env.str('MAILCHIMP_APIKEY')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env.str('EMAIL_HOST')
EMAIL_PORT = env.str('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env.str('MAIL_USER')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env.str('MAIL_PASSWORD')
SITE_DOMAIN = 'villages.io'
HELP_EMAIL = env.str('MAIL_USER')
EMAIL_SUBJECT_PREFIX = "[Villages] "

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'social_django',

    # Custom apps
    'ccproject',
    'geo',
    'profile',
    'post',
    'feed',
    'relate',
    'general',
    'pages',
    'admin',
    'about',
    'listings',
    'tags',
    'notification',
    'django_user_agents',

    # Ripple
    'account',
    'payment',
    # 'management',

    'accounts.apps.AccountsConfig',
    'frontend.apps.FrontendConfig',
    'endorsement.apps.EndorsementConfig',
    'categories.apps.CategoriesConfig'

]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'profile.middleware.ProfileMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
    'geo.middleware.LocationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.request",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
)

ROOT_URLCONF = 'ccproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),
                 os.path.join(BASE_DIR, 'accounts', 'templates'),
                 os.path.join(BASE_DIR, 'accounts', 'sign_in', 'templates'),
                 os.path.join(BASE_DIR, 'notification', 'templates'),
                 os.path.join(BASE_DIR, 'listings', 'templates'),
                 os.path.join(BASE_DIR, 'management', 'templates'),
                 os.path.join(BASE_DIR, 'categories', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'ccproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': env.str('VILLAGES_DB_NAME'),
        'USER': env.str('VILLAGES_DB_USER'),
        'PASSWORD': env.str('VILLAGES_DB_PASS'),
        'HOST': env.str('VILLAGES_DB_HOST', default='localhost')
    },
    'ripple': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env.str('RIPPLE_DB_NAME'),
        'USER': env.str('RIPPLE_DB_USER'),
        'PASSWORD': env.str('RIPPLE_DB_PASS'),
        'HOST': env.str('RIPPLE_DB_HOST', default='localhost')
    }
}

SITE_ID = 1

ELASTICSEARCH = elasticsearch.Elasticsearch(hosts=["127.0.0.1:9200"])

DATABASE_ROUTERS = ('ripple.router.RippleRouter',)

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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

AUTHENTICATION_BACKENDS = (
    'social_core.backends.facebook.FacebookOAuth2',
    'profile.auth_backends.CaseInsensitiveModelBackend',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

SESSIONS_DIRECTORY = os.path.join(BASE_DIR, 'sessions')

SESSION_ENGINE = 'django.contrib.sessions.backends.file'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 43200      # 12 hours in seconds
SESSION_FILE_PATH = SESSIONS_DIRECTORY
# SESSION_COOKIE_SECURE = True
LOCATION_COOKIE_NAME = 'location_id'
LOCATION_COOKIE_AGE = timedelta(days=365)

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

MEDIA_URL = '/uploads/'

MEDIA_ROOT = 'uploads'

GEOIP_PATH = '/usr/share/GeoIP'

LOGIN_URL = '/accounts/sign_in/log_in'

PASSWORD_RESET_LINK_EXPIRY = timedelta(days=7)

LOCATION_SESSION_KEY = 'location_id'
DEFAULT_LOCATION = ('49.2696243', '-123.0696036')  # East Vancouver.
DEFAULT_RADIUS = -1  # infinity

INVITATION_ONLY = False

SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id,name,email',
}

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'

SOCIAL_AUTH_FACEBOOK_KEY = env.str('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = env.str('SOCIAL_AUTH_FACEBOOK_SECRET')

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'accounts.facebook_authentication.pipeline.bind_existing_account',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.mail.mail_validation',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'accounts.facebook_authentication.pipeline.create_profile_data',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

USE_X_FORWARDED_HOST = True

GOOGLE_MAPS_API_KEY = env.str('GOOGLE_MAPS_API_KEY')


ENDORSEMENT_BONUS = 5

FEED_ITEMS_PER_PAGE = 20

LISTING_ITEMS_PER_PAGE = 21

NOTIFICATIONS_PER_PAGE = 10

try:
    from ccproject.local_settings import *
except ImportError:
    pass
