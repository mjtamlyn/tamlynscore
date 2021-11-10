import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tamlynscore.settings")  # NOQA

from django.core.wsgi import get_wsgi_application  # NOQA

application = get_wsgi_application()
