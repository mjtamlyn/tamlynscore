from django.contrib import admin

from olympic.models import *

admin.site.register(OlympicRound)
admin.site.register(Category)
admin.site.register(OlympicSessionRound)
admin.site.register(Seeding)
admin.site.register(Match)
admin.site.register(Result)
