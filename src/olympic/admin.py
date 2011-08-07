from django.contrib import admin

from olympic.models import *

class MatchAdmin(admin.ModelAdmin):
    list_filter = ('level', 'session_round')

class ResultAdmin(admin.ModelAdmin):
    list_display = ('match', 'seed', 'total', 'win')
    list_filter = ('match__session_round',)
    
admin.site.register(OlympicRound)
admin.site.register(Category)
admin.site.register(OlympicSessionRound)
admin.site.register(Seeding)
admin.site.register(Match, MatchAdmin)
admin.site.register(Result, ResultAdmin)
