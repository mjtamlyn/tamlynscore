from django.contrib import admin

from core.models import *


class ArcherAdmin(admin.ModelAdmin):
    list_display = ('name', 'club')
    list_filter= ('club',)


class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'abbreviation')


class RoundAdmin(admin.ModelAdmin):
    filter_horizontal = ('subrounds',)
    list_display = ('name', 'total_arrows', 'subround_details', 'scoring_type')

    def queryset(self, request):
        return super(RoundAdmin, self).queryset(request).prefetch_related('subrounds')

    def total_arrows(self, instance):
        return sum(map(lambda s: s.arrows, instance.subrounds.all()))

    def subround_details(self, instance):
        return ', '.join(map(unicode, instance.subrounds.all()))


admin.site.register(Country)
admin.site.register(Region)
admin.site.register(County)
admin.site.register(Club, ClubAdmin)
admin.site.register(Archer, ArcherAdmin)
admin.site.register(Bowstyle)
admin.site.register(Round, RoundAdmin)
admin.site.register(Subround)