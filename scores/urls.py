from django.conf.urls import url

from scores import views


urlpatterns = [
    url(r'^(?P<slug>(\w+-?)+)/input-scores/$', views.InputScores.as_view(), name='input_scores'),
    url(r'^(?P<slug>(\w+-?)+)/input-scores/team/$', views.InputScoresTeam.as_view(), name='input_scores_team'),
    url(r'^(?P<slug>(\w+-?)+)/input-scores/mobile/$', views.InputScoresMobile.as_view(), name='input_scores_mobile'),
    url(r'^(?P<slug>(\w+-?)+)/input-arrows/(?P<session_id>\d+)/doz(?P<dozen>\d+)/boss(?P<boss>\d+)/$', views.InputArrowsView.as_view(), name='input_arrows'),
    url(r'^(?P<slug>(\w+-?)+)/input-arrows/archer/(?P<score_id>\d+)/$', views.InputArrowsArcher.as_view(), name='input_arrows_archer'),
    url(r'^(?P<slug>(\w+-?)+)/input-scores/team/(?P<team_id>\d+)/doz(?P<dozen>\d+)/$', views.InputDozensTeam.as_view(), name='input_dozens_team'),
    url(r'^(?P<slug>(\w+-?)+)/input-dozens/(?P<session_id>\d+)/doz(?P<dozen>\d+)/boss(?P<boss>\d+)/$', views.InputDozens.as_view(), name='input_dozens'),
    url(r'^(?P<slug>(\w+-?)+)/input-arrows/(?P<session_id>\d+)/doz(?P<dozen>\d+)/boss(?P<boss>\d+)/mobile/$', views.InputArrowsViewMobile.as_view(), name='input_arrows_mobile'),
    url(r'^(?P<slug>[\w-]+)/leaderboard/(?P<mode>[\w-]+)/(?P<format>[\w-]+)/', views.Leaderboard.as_view(), name='leaderboard'),
    url(r'^(?P<slug>[\w-]+)/results/(?P<mode>[\w-]+)/(?P<format>[\w-]+)/', views.Results.as_view(), name='results'),
    url(r'^(?P<slug>[\w-]+)/rankings-export.csv', views.RankingsExport.as_view(), name='rankings_export'),
]
