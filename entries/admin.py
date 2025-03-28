from django.contrib import admin

from entries.models import (
    Competition, CompetitionEntry, ResultsMode, Session, SessionEntry,
    SessionRound, Sponsor, TargetAllocation, Tournament,
)


class CompetitionAdmin(admin.ModelAdmin):
    filter_horizontal = ('admins', 'sponsors',)


class CompetitionEntryAdmin(admin.ModelAdmin):
    list_display = ('archer', 'club', 'competition')
    list_filter = ('competition', 'club')
    raw_id_fields = ('archer',)


class SessionAdmin(admin.ModelAdmin):
    list_display = ('competition', 'start')
    ordering = ('-start',)
    raw_id_fields = ('competition',)


class SessionRoundAdmin(admin.ModelAdmin):
    list_display = ('session__competition', 'session__start', 'shot_round')
    ordering = ('-session__start',)
    raw_id_fields = ('session',)


class ResultModeAdmin(admin.ModelAdmin):
    list_display = ('competition', 'mode')


class SessionEntryAdmin(admin.ModelAdmin):
    list_display = ('competition_entry', 'session_round')
    list_filter = ('session_round',)

    raw_id_fields = ('competition_entry',)


class TargetAllocationAdmin(admin.ModelAdmin):
    raw_id_fields = ('session_entry',)

    def get_queryset(self, request):
        return super(TargetAllocationAdmin, self).get_queryset(request).select_related()


admin.site.register(Tournament)
admin.site.register(Sponsor)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(ResultsMode, ResultModeAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(SessionRound, SessionRoundAdmin)
admin.site.register(CompetitionEntry, CompetitionEntryAdmin)
admin.site.register(SessionEntry, SessionEntryAdmin)
admin.site.register(TargetAllocation, TargetAllocationAdmin)
