import uuid

from django.db import models

from entries.models import Competition


class Judge(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4)
    competition = models.OneToOneField(Competition, on_delete=models.CASCADE)
    last_login = models.DateTimeField(null=True, blank=True)

    is_anonymous = False
    is_superuser = False

    def __str__(self):
        return 'Judges - %s' % self.competition
