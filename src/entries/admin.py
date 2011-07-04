from django.contrib import admin

from entries.models import *

admin.site.register(Tournament)
admin.site.register(Competition)
admin.site.register(Session)
admin.site.register(SessionRound)
admin.site.register(CompetitionEntry)
admin.site.register(SessionEntry)
admin.site.register(TargetAllocation)
