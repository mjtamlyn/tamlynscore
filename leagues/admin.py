from django.contrib import admin

from .models import League, Leg, ResultsMode, Season


class SeasonAdmin(admin.ModelAdmin):
    filter_horizontal = ('non_leg_competitions',)


class LegAdmin(admin.ModelAdmin):
    filter_horizontal = ('competitions',)


admin.site.register(League)
admin.site.register(Leg, LegAdmin)
admin.site.register(Season, SeasonAdmin)
admin.site.register(ResultsMode)
