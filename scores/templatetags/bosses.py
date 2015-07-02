from django import template


register = template.Library()


@register.filter
def dozcomplete(complete_lookup, dozen):
    if complete_lookup[dozen]:
        return u'done'
    else:
        return u''
