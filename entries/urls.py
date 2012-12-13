from django.conf.urls.defaults import *

from entries import views

urlpatterns = patterns('entries.views',
    url(r'^$', views.CompetitionList.as_view(), name='tournaments_list'),
    url(r'^(?P<slug>[\w-]+)/$', views.CompetitionDetail.as_view(), name='competition_detail'),
    url(r'^(?P<slug>[\w-]+)/entries/$', views.EntryList.as_view(), name='entry_list'),
    url(r'^(?P<slug>[\w-]+)/target-list/$', views.BetterTargetList.as_view(), name='target_list'),
    (r'^(?P<slug>[\w-]+)/target-list/pdf/$', 'target_list_pdf'),
    (r'^(?P<slug>[\w-]+)/target-list/lunch/$', 'target_list_lunch'),
    url(r'^(?P<slug>[\w-]+)/score-sheets/$', views.ScoreSheets.as_view(), name='score_sheets'),
    (r'^(?P<slug>[\w-]+)/score-sheets/(?P<round_id>\d+)/$', 'score_sheets_pdf'),
    (r'^(?P<slug>[\w-]+)/running-slips/(?P<round_id>\d+)/$', 'running_slips_pdf'),

    url(r'^(?P<slug>[\w-]+)/registration/$', views.Registration.as_view(), name='registration'),
)