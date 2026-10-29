from django.contrib import admin

from .models import League, Leg, ResultsMode, Season


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    filter_horizontal = ('organisers', 'managed_accounts', 'tournaments')


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    filter_horizontal = ('non_leg_competitions',)
    list_filter = ('league',)


@admin.register(Leg)
class LegAdmin(admin.ModelAdmin):
    filter_horizontal = ('competitions',)
    list_filter = ('season__league', 'season',)


@admin.register(ResultsMode)
class ResultsModeAdmin(admin.ModelAdmin):
    list_display = ('leg', 'mode')
    list_filter = ('leg__season',)
