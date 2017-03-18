from django.contrib import admin

from olympic.models import OlympicRound, Category, OlympicSessionRound, Match, Result, Seeding


class MatchAdmin(admin.ModelAdmin):
    list_filter = ('level', 'session_round')


class OlympicSessionRoundAdmin(admin.ModelAdmin):
    raw_id_fields = ('session', 'ranking_rounds',)


class ResultAdmin(admin.ModelAdmin):
    list_display = ('match', 'seed', 'total', 'win')
    list_filter = ('match__session_round', 'match__level')

    raw_id_fields = ('seed', 'match')


admin.site.register(OlympicRound)
admin.site.register(Category)
admin.site.register(OlympicSessionRound, OlympicSessionRoundAdmin)
admin.site.register(Seeding)
admin.site.register(Match, MatchAdmin)
admin.site.register(Result, ResultAdmin)
