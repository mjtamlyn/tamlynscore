from django.db.models import Max
from django import template

from scores.models import Arrow

register = template.Library()

@register.filter
def dozcomplete(complete_lookup, dozen):
    if complete_lookup[dozen]:
        return u'done'
    else:
        return u''
