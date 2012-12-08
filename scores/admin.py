from django.contrib import admin

from scores.models import *


class ArrowAdmin(admin.ModelAdmin):
    list_display = ('arrow_value', 'score')


class ScoreAdmin(admin.ModelAdmin):
    raw_id_fields = ('target',)
    list_display = ('target', 'score', 'hits', 'golds')
    list_editable = ('score', 'hits', 'golds')
    list_filter = ('target__session_entry__competition_entry__competition',)

    def queryset(self, request):
        return super(ScoreAdmin, self).queryset(request).select_related()


admin.site.register(Score, ScoreAdmin)
admin.site.register(Arrow, ArrowAdmin)
admin.site.register(Dozen)
