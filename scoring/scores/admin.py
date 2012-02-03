from django.contrib import admin

from scores.models import *


class ArrowAdmin(admin.ModelAdmin):
    list_display = ('arrow_value', 'score')


admin.site.register(Score)
admin.site.register(Arrow, ArrowAdmin)
