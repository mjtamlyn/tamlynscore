from django.contrib.auth.backends import BaseBackend

from .models import Judge


class JudgeAuthBackend(BaseBackend):
    def get_user(self, user_id):
        try:
            return Judge.objects.get(pk=user_id)
        except Judge.DoesNotExist:
            return None
