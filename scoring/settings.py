import os

import dj_database_url


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = not os.environ.get('PRODUCTION')
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = [
    'archery-scoring.herokuapp.com',
    'archery-scoring.mjtamlyn.co.uk',
    '127.0.0.1',
    'localhost',
    '192.168.1.101',
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
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.Loader',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'scoring.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'south',
    'gunicorn',

    'scoring',
    'core',
    'entries',
    'scores',
    'olympic',
    'accounts',

    'debug_toolbar',
)

TEST_RUNNER = 'tests.runner.ScoringRunner'

LOGIN_REDIRECT_URL = '/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

INTERNAL_IPS = ('127.0.0.1',)

DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS': False}
