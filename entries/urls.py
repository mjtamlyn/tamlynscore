from django.conf.urls import patterns, url

from entries import views

urlpatterns = patterns('entries.views',
    url(r'^$', views.CompetitionList.as_view(), name='tournaments_list'),
    url(r'^(?P<slug>[\w-]+)/$', views.CompetitionDetail.as_view(), name='competition_detail'),
    url(r'^(?P<slug>[\w-]+)/entries/$', views.EntryList.as_view(), name='entry_list'),
    url(r'^(?P<slug>[\w-]+)/entries/search/$', views.ArcherSearch.as_view(), name='archer_search'),
    url(r'^(?P<slug>[\w-]+)/entries/add/(?P<archer_id>\d+)/$', views.EntryAdd.as_view(), name='entry_add'),
    url(r'^(?P<slug>[\w-]+)/entries/delete/(?P<entry_id>\d+)/?$', views.EntryDelete.as_view(), name='entry_delete'),
    url(r'^(?P<slug>[\w-]+)/target-list/$', views.TargetList.as_view(), name='target_list'),
    url(r'^(?P<slug>[\w-]+)/target-list/pdf/$', 'target_list_pdf', name='target_list_pdf'),
    (r'^(?P<slug>[\w-]+)/target-list/lunch/$', 'target_list_lunch'),
    url(r'^(?P<slug>[\w-]+)/score-sheets/$', views.ScoreSheets.as_view(), name='score_sheets'),
    url(r'^(?P<slug>[\w-]+)/score-sheets/(?P<round_id>\d+)/$', views.ScoreSheetsPdf.as_view(), name='score_sheets_pdf'),
    url(r'^(?P<slug>[\w-]+)/score-sheets/session/(?P<session_id>\d+)/$', views.SessionScoreSheetsPdf.as_view(),
        name='session_score_sheets_pdf'),
    (r'^(?P<slug>[\w-]+)/running-slips/(?P<round_id>\d+)/$', 'running_slips_pdf'),

    url(r'^(?P<slug>[\w-]+)/registration/$', views.Registration.as_view(), name='registration'),
)
