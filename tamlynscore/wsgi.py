import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tamlynscore.settings")  # NOQA

from django.core.wsgi import get_wsgi_application
from dj_static import Cling, MediaCling

from .wsgi_middleware import DomainRedirect

application = DomainRedirect(Cling(MediaCling(get_wsgi_application())))
