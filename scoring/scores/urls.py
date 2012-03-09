from django.conf.urls.defaults import *

from scores import views

urlpatterns = patterns('scores.views',
    url(r'^(?P<slug>(\w+-?)+)/input-scores/$', views.InputScores.as_view(), name='input_scores'),
    url(r'^(?P<slug>(\w+-?)+)/input-scores/mobile/$', views.InputScoresMobile.as_view(), name='input_scores-mobile'),
    (r'^(?P<slug>(\w+-?)+)/input-arrows/(?P<round_id>\d+)/doz(?P<dozen>\d+)/boss(?P<boss>\d+)/$', 'input_arrows'),
    (r'^(?P<slug>(\w+-?)+)/leaderboard/$', 'leaderboard'),
    url(r'^(?P<slug>(\w+-?)+)/leaderboard/combined/$', views.LeaderboardCombined.as_view(), name='leaderboard_combined'),
    url(r'^(?P<slug>(\w+-?)+)/leaderboard/combined/experienced/$', views.LeaderboardCombinedExperienced.as_view(), name='leaderboard_combined_experienced'),
    url(r'^(?P<slug>(\w+-?)+)/leaderboard/combined/novice/$', views.LeaderboardCombinedNovice.as_view(), name='leaderboard_combined_novice'),
    url(r'^(?P<slug>(\w+-?)+)/leaderboard/teams/$', views.LeaderboardTeams.as_view(), name='leaderboard_teams'),
    url(r'^(?P<slug>(\w+-?)+)/leaderboard/butc/$', views.LeaderboardBUTC.as_view(), name='leaderboard_butc'),
    url(r'^(?P<slug>(\w+-?)+)/leaderboard/summary/$', views.LeaderboardSummary.as_view(), name='leaderboard_summary'),
    (r'^(?P<slug>(\w+-?)+)/leaderboard/big-screen/$', 'leaderboard_big_screen'),
    (r'^(?P<slug>(\w+-?)+)/results/$', 'results'),
    (r'^(?P<slug>(\w+-?)+)/results/pdf/$', 'results_pdf'),
)
