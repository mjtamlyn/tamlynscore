from django.db import models

from entries.models import SessionEntry

class Score(models.Model):
    entry = models.ForeignKey(SessionEntry)

    score = models.PositiveIntegerField()
    hits = models.PositiveIntegerField()
    golds = models.PositiveIntegerField()
    xs = models.PositiveIntegerField()

    retired = models.BooleanField(default=False)

    def __unicode__(self):
        return u'Score for {0}'.format(self.entry)

class Arrow(models.Model):
    score = models.ForeignKey(Score)
    arrow_value = models.PositiveIntegerField()
    arrow_of_round = models.PositiveIntegerField()
    is_x = models.BooleanField(default=False)

    def __unicode__(self):
        if self.is_x:
            return u'X'
        if self.arrow_value == 0:
            return u'M'
        return unicode(self.score)

#TODO: H2H models
