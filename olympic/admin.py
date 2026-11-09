from django.contrib import admin

from olympic.models import (
    Category, Match, MatchArrow, OlympicRound, OlympicSessionRound, Result,
    Seeding,
)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    raw_id_fields = ('session_round',)

    def get_queryset(self, request):
        return super(MatchAdmin, self).get_queryset(request).select_related()


@admin.register(OlympicSessionRound)
class OlympicSessionRoundAdmin(admin.ModelAdmin):
    raw_id_fields = ('session', 'ranking_rounds',)

    def get_queryset(self, request):
        return super(OlympicSessionRoundAdmin, self).get_queryset(request).select_related()


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('match', 'seed', 'total', 'win')
    list_filter = ('match__session_round', 'match__level')

    raw_id_fields = ('seed', 'match')


@admin.register(MatchArrow)
class MatchArrowAdmin(admin.ModelAdmin):
    raw_id_fields = ('result',)


admin.site.register(OlympicRound)
admin.site.register(Category)
admin.site.register(Seeding)
