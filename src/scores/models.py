from django.db import models
from django.forms import ValidationError

from itertools import groupby

class Arrow(models.Model):
    subround = models.ForeignKey(Subround)
    entry = models.ForeignKey(Entry)
    score = models.PositiveIntegerField()
    arrow_of_round = models.PositiveIntegerField()
    is_x = models.BooleanField(default=False)

    def __unicode__(self):
        if self.is_x:
            return u'X'
        if self.score == 0:
            return u'M'
        return unicode(self.score)

    def clean(self):
        if self.arrow_of_round > self.subround.arrows:
            raise ValidationError('You can\'t have arrow {0} in a subround of {1} arrows.'.format(self.arrow_of_round, self.subround.arrows))

    class Meta:
        unique_together = ('subround', 'arrow_of_round', 'entry')
