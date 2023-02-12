import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tamlynscore.settings")  # NOQA

from django.conf import settings  # NOQA
from django.core.wsgi import get_wsgi_application  # NOQA

from whitenoise import WhiteNoise  # NOQA

application = WhiteNoise(
    get_wsgi_application(),
    root=settings.MEDIA_ROOT,
)
