from django.contrib import admin

from entries.models import *


class CompetitionAdmin(admin.ModelAdmin):
    filter_horizontal = ('sponsors',)


class CompetitionEntryAdmin(admin.ModelAdmin):
    list_display = ('archer', 'club', 'competition')
    list_filter = ('competition', 'club')
    raw_id_fields = ('archer',)


class SessionEntryAdmin(admin.ModelAdmin):
    list_display = ('competition_entry', 'session_round')
    list_filter = ('session_round',)

    raw_id_fields = ('competition_entry',)


class TargetAllocationAdmin(admin.ModelAdmin):
    raw_id_fields = ('session_entry',)

    def queryset(self, request):
        return super(TargetAllocationAdmin, self).queryset(request).select_related()


admin.site.register(Tournament)
admin.site.register(Sponsor)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(ResultsMode)
admin.site.register(Session)
admin.site.register(SessionRound)
admin.site.register(CompetitionEntry, CompetitionEntryAdmin)
admin.site.register(SessionEntry, SessionEntryAdmin)
admin.site.register(TargetAllocation, TargetAllocationAdmin)
