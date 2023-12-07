from django.forms.renderers import TemplatesSetting
from django.utils.text import slugify


def generate_slug(cls, value, scope=None):
    """Given a model and a character string, return a suitable slug.

    Assumes the slug will be used for a field named `slug` and gets the
    maximum length restriction therefrom.

    Ensures the slug is unique by adding a number to the end if needed.
    """
    if not value:
        return ''

    if not isinstance(cls, type):
        cls = cls.__class__
    max_len = cls._meta.get_field('slug').max_length

    slug = slugify(value)[:max_len].rstrip('-') or 'x'

    # Ensure unique within scope.
    queryset = cls.objects.all()
    if scope:
        queryset = queryset.filter(**scope)
    count = 1
    while queryset.filter(slug=slug).exists():
        count_str = str(count)
        slug = slug[:(max_len - len(count_str) - 1)] + '-' + count_str
        count += 1

    return slug


class TamlynScoreFormRenderer(TemplatesSetting):
    form_template_name = "form-rows.html"
    field_template_name = "form-item.html"
