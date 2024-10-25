from django.contrib import admin

from olympic.models import (
    Category, Match, OlympicRound, OlympicSessionRound, Result, Seeding,
)


class MatchAdmin(admin.ModelAdmin):
    raw_id_fields = ('session_round',)

    def get_queryset(self, request):
        return super(MatchAdmin, self).get_queryset(request).select_related()


class OlympicSessionRoundAdmin(admin.ModelAdmin):
    raw_id_fields = ('session', 'ranking_rounds',)

    def get_queryset(self, request):
        return super(OlympicSessionRoundAdmin, self).get_queryset(request).select_related()


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
