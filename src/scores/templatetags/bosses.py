from django.db.models import Max
from django import template

from scores.models import Arrow

register = template.Library()

@register.filter
def bosscomplete(scores, dozen):
    if Arrow.objects.filter_by_dozen(dozen).filter(score__in=scores).count() == len(scores) * 12:
        return u'done'
    else:
        return u''
