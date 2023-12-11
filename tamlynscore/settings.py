import os

import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = not os.environ.get('PRODUCTION')
ALLOWED_HOSTS = [
    'tamlynscore.co.uk',
    'www.tamlynscore.co.uk',
    '127.0.0.1',
    'localhost',
    '192.168.1.101',
    '192.168.1.100',
]

ADMINS = (
    ('Marc Tamlyn', 'marc.tamlyn@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {'default': dj_database_url.config(default='postgres://localhost/tamlynscore')}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

TIME_ZONE = 'Europe/London'
USE_TZ = True
LANGUAGE_CODE = 'en-gb'
USE_I18N = True
USE_L10N = True

SECRET_KEY = '(0z9j8dsp!3&@tqx$=&@56&q!pr5(1&6wd0*&7@%hiwt3@k!qt'
SITE_ID = 1

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'build')]
STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')
STATIC_URL = '/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

WEBPACK_LOADER = {
    'DEFAULT': {
        'CACHE': not DEBUG,
        'BUNDLE_DIR_NAME': 'bundles/',
        'STATS_FILE': os.path.join(BASE_DIR, 'build', 'webpack-stats.json'),
    },
}

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': (
            'django.contrib.auth.context_processors.auth',
            'django.template.context_processors.debug',
            'django.template.context_processors.i18n',
            'django.template.context_processors.media',
            'django.template.context_processors.static',
            'django.template.context_processors.request',
            'django.template.context_processors.tz',
            'django.contrib.messages.context_processors.messages',
        ),
    },
}]
FORM_RENDERER = 'tamlynscore.utils.TamlynScoreFormRenderer'

MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = os.environ.get('ROOT_URLCONF', 'tamlynscore.urls')
WSGI_APPLICATION = 'tamlynscore.wsgi.application'

INSTALLED_APPS = (
    'tamlynscore',
    'core',
    'leagues',
    'entries',
    'scores',
    'olympic',
    'judging',
    'accounts',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.forms',
    'gunicorn',
    'debug_toolbar',
    'webpack_loader',
    'custom_user',
    'qr_code',
    'raven.contrib.django.raven_compat',
)

TEST_RUNNER = 'tests.runner.ScoringRunner'

LOGIN_REDIRECT_URL = '/'
AUTH_USER_MODEL = 'core.User'
AUTHENTICATION_BACKENDS = [
    'judging.auth_backends.JudgeAuthBackend',
    'entries.auth_backends.EntryUserAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

servers = os.environ.get('MEMCACHIER_SERVERS')
username = os.environ.get('MEMCACHIER_USERNAME')
password = os.environ.get('MEMCACHIER_PASSWORD')

if servers and username and password:
    CACHES['default'].update({
        'BACKEND': 'django_bmemcached.memcached.BMemcached',
        'LOCATION': servers,
        'OPTIONS': {
            'username': username,
            'password': password,
        }
    })

if not DEBUG and not os.environ.get('LOCAL'):
    SESSION_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DEBUG_TOOLBAR_CONFIG = {
    'JQUERY_URL': STATIC_URL + 'lib/jquery/jquery-2.1.3.min.js',
}

INTERNAL_IPS = [
    '127.0.0.1',
]

if os.environ.get('RAVEN_DSN'):
    RAVEN_CONFIG = {
        'dsn': os.environ['RAVEN_DSN'],
    }

CURRENT_EVENT = os.environ.get('CURRENT_EVENT', 'bucs-outdoors-2014')
