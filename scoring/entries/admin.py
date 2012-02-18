from django.contrib import admin

from entries.models import *


class CompetitionEntryAdmin(admin.ModelAdmin):
    list_display = ('archer', 'club', 'competition')
    list_filter = ('competition', 'club')

admin.site.register(Tournament)
admin.site.register(Competition)
admin.site.register(Session)
admin.site.register(SessionRound)
admin.site.register(CompetitionEntry, CompetitionEntryAdmin)
admin.site.register(SessionEntry)
admin.site.register(TargetAllocation)
