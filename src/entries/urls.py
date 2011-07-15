from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('entries.views',
    (r'^$', 'tournaments'),
    (r'^(?P<slug>[\w-]+)/$', 'competition_index'),
    (r'^(?P<slug>[\w-]+)/entries/$', 'entries'),
    (r'^(?P<slug>[\w-]+)/target-list/$', 'target_list'),
    (r'^(?P<slug>[\w-]+)/target-list/pdf/$', 'target_list_pdf'),
    (r'^(?P<slug>[\w-]+)/score-sheets/$', 'score_sheets'),
    (r'^(?P<slug>[\w-]+)/score-sheets/(?P<round_id>\d+)/$', 'score_sheets_pdf'),
    (r'^(?P<slug>[\w-]+)/running-slips/(?P<round_id>\d+)/$', 'running_slips_pdf'),

    (r'^(?P<slug>[\w-]+)/registration/$', 'registration'),
)
