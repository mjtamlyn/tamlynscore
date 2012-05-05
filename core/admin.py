from django.contrib import admin

from core.models import *


class ArcherAdmin(admin.ModelAdmin):
    list_display = ('name', 'club')
    list_filter= ('club',)

class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'abbreviation')

admin.site.register(Country)
admin.site.register(Region)
admin.site.register(County)
admin.site.register(Club, ClubAdmin)
admin.site.register(Archer, ArcherAdmin)
admin.site.register(Bowstyle)
admin.site.register(Round)
admin.site.register(Subround)
