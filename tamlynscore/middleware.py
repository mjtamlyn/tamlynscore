import zoneinfo

from django.conf import settings
from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        timezone.activate(zoneinfo.ZoneInfo(settings.TIME_ZONE))
        return self.get_response(request)
