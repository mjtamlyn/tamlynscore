from django.conf.urls import url

from entries import views

urlpatterns = [
    url(r'^$', views.CompetitionList.as_view(), name='tournaments_list'),
    url(r'^add/$', views.CompetitionCreate.as_view(), name='competition_create'),
    url(r'^(?P<slug>[\w-]+)/$', views.CompetitionDetail.as_view(), name='competition_detail'),
    url(r'^(?P<slug>[\w-]+)/edit/$', views.CompetitionUpdate.as_view(), name='competition_update'),
    url(r'^(?P<slug>[\w-]+)/entries/$', views.EntryList.as_view(), name='entry_list'),
    url(r'^(?P<slug>[\w-]+)/entries/search/$', views.ArcherSearch.as_view(), name='archer_search'),
    url(r'^(?P<slug>[\w-]+)/entries/add/(?P<archer_id>\d+)/$', views.EntryAdd.as_view(), name='entry_add'),
    url(r'^(?P<slug>[\w-]+)/entries/edit/(?P<entry_id>\d+)/?$', views.EntryUpdate.as_view(), name='entry_update'),
    url(r'^(?P<slug>[\w-]+)/entries/delete/(?P<entry_id>\d+)/?$', views.EntryDelete.as_view(), name='entry_delete'),
    url(r'^(?P<slug>[\w-]+)/target-list/$', views.TargetList.as_view(), name='target_list'),
    url(r'^(?P<slug>[\w-]+)/target-list/edit/$', views.TargetListEdit.as_view(), name='target_list_edit'),
    url(r'^(?P<slug>[\w-]+)/target-list/pdf/$', views.TargetListPdf.as_view(), name='target_list_pdf'),
    url(r'^(?P<slug>[\w-]+)/target-list/lunch/$', views.TargetListLunch.as_view()),
    url(r'^(?P<slug>[\w-]+)/score-sheets/$', views.ScoreSheets.as_view(), name='score_sheets'),
    url(r'^(?P<slug>[\w-]+)/score-sheets/(?P<round_id>\d+)/$', views.ScoreSheetsPdf.as_view(), name='score_sheets_pdf'),
    url(r'^(?P<slug>[\w-]+)/score-sheets/session/(?P<session_id>\d+)/$', views.SessionScoreSheetsPdf.as_view(),
        name='session_score_sheets_pdf'),
    url(r'^(?P<slug>[\w-]+)/running-slips/(?P<round_id>\d+)/$', views.RunningSlipsPdf.as_view(), name='running_slips_pdf'),

    url(r'^(?P<slug>[\w-]+)/registration/$', views.Registration.as_view(), name='registration'),
]
