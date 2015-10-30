import os

import dj_database_url


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = not os.environ.get('PRODUCTION')
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = [
    'archery-scoring.herokuapp.com',
    'archery-scoring-public.herokuapp.com',
    'archery-scoring.mjtamlyn.co.uk',
    'live.mjtamlyn.co.uk',
    '127.0.0.1',
    'localhost',
    '192.168.1.101',
    '192.168.1.100',
]

ADMINS = (
    ('Marc Tamlyn', 'marc.tamlyn@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {'default': dj_database_url.config(default='postgres://localhost/archery')}

TIME_ZONE = 'Europe/London'
LANGUAGE_CODE = 'en-gb'
USE_I18N = True
USE_L10N = True

SECRET_KEY = '(0z9j8dsp!3&@tqx$=&@56&q!pr5(1&6wd0*&7@%hiwt3@k!qt'
SITE_ID = 1

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

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

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = os.environ.get('ROOT_URLCONF', 'scoring.urls')

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'gunicorn',
    'debug_toolbar',

    'scoring',
    'core',
    'entries',
    'scores',
    'olympic',
    'accounts',
)

TEST_RUNNER = 'tests.runner.ScoringRunner'

LOGIN_REDIRECT_URL = '/'
AUTH_USER_MODEL = 'core.User'
PASSWORD_RESET_TIMEOUT_DAYS = 7  # also used for registration.

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    MIDDLEWARE_CLASSES = ('sslify.middleware.SSLifyMiddleware',) + MIDDLEWARE_CLASSES

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'console': {
            'format': '[%(asctime)s][%(levelname)s] %(name)s %(filename)s:%(funcName)s:%(lineno)d | %(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

DEBUG_TOOLBAR_CONFIG = {
    'JQUERY_URL': STATIC_URL + 'lib/jquery/jquery-2.1.3.min.js',
}

CURRENT_EVENT = os.environ.get('CURRENT_EVENT', 'bucs-outdoors-2014')
