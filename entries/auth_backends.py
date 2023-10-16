from django.contrib.auth.backends import BaseBackend

from .models import EntryUser


class EntryUserAuthBackend(BaseBackend):
    def get_user(self, user_id):
        try:
            return EntryUser.objects.get(pk=user_id)
        except EntryUser.DoesNotExist:
            return None
