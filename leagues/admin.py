from django.contrib import admin

from .models import League, Leg, Season


class SeasonAdmin(admin.ModelAdmin):
    filter_horizontal = ('clubs',)


admin.site.register(League)
admin.site.register(Leg)
admin.site.register(Season, SeasonAdmin)
