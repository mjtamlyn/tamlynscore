from django.contrib import admin

from .models import League, Leg, ResultsMode, Season


class LegAdmin(admin.ModelAdmin):
    filter_horizontal = ('competitions',)


admin.site.register(League)
admin.site.register(Leg, LegAdmin)
admin.site.register(Season)
admin.site.register(ResultsMode)
