from django.conf.urls import patterns, url

from scores import views


urlpatterns = patterns('scores.views',
    url(r'^(?P<slug>(\w+-?)+)/input-scores/$', views.InputScores.as_view(), name='input_scores'),
    url(r'^(?P<slug>(\w+-?)+)/input-scores/mobile/$', views.InputScoresMobile.as_view(), name='input_scores_mobile'),
    url(r'^(?P<slug>(\w+-?)+)/input-arrows/(?P<session_id>\d+)/doz(?P<dozen>\d+)/boss(?P<boss>\d+)/$', 'input_arrows', name='input_arrows'),
    url(r'^(?P<slug>(\w+-?)+)/input-arrows/archer/(?P<score_id>\d+)/$', views.InputArrowsArcher.as_view(), name='input_arrows_archer'),
    url(r'^(?P<slug>(\w+-?)+)/input-dozens/(?P<session_id>\d+)/doz(?P<dozen>\d+)/boss(?P<boss>\d+)/$', views.InputDozens.as_view(), name='input_dozens'),
    url(r'^(?P<slug>(\w+-?)+)/input-arrows/(?P<session_id>\d+)/doz(?P<dozen>\d+)/boss(?P<boss>\d+)/mobile/$', views.InputArrowsViewMobile.as_view(), name='input_arrows_mobile'),
    url(r'^(?P<slug>(\w+-?)+)/leaderboard/$', views.LeaderboardView.as_view(), name='leaderboard'),
    url(r'^(?P<slug>(\w+-?)+)/leaderboard/combined/$', views.LeaderboardCombined.as_view(), name='leaderboard_combined'),
    url(r'^(?P<slug>(\w+-?)+)/leaderboard/combined/experienced/$', views.LeaderboardCombinedExperienced.as_view(), name='leaderboard_combined_experienced'),
    url(r'^(?P<slug>(\w+-?)+)/leaderboard/combined/novice/$', views.LeaderboardCombinedNovice.as_view(), name='leaderboard_combined_novice'),
    url(r'^(?P<slug>(\w+-?)+)/leaderboard/teams/$', views.LeaderboardTeams.as_view(), name='leaderboard_teams'),
    url(r'^(?P<slug>(\w+-?)+)/leaderboard/butc/$', views.LeaderboardBUTC.as_view(), name='leaderboard_butc'),
    url(r'^(?P<slug>(\w+-?)+)/leaderboard/summary/$', views.LeaderboardSummary.as_view(), name='leaderboard_summary'),
    url(r'^(?P<slug>(\w+-?)+)/leaderboard/big-screen/$', views.LeaderboardBigScreen.as_view(), name='leaderboard_big_screen'),
    url(r'^(?P<slug>(\w+-?)+)/leaderboard/big-screen/(?P<session_id>\d+)/$', views.LeaderboardBigScreenSession.as_view(), name='leaderboard_big_screen_session'),
    url(r'^(?P<slug>(\w+-?)+)/leaderboard/big-screen/(?P<session_id>\d+)/novice/$', views.LeaderboardBigScreenSessionNovice.as_view(), name='leaderboard_big_screen_session-novice'),
    url(r'^(?P<slug>(\w+-?)+)/leaderboard/big-screen/(?P<session_id>\d+)/experienced/$', views.LeaderboardBigScreenSessionExperienced.as_view(), name='leaderboard_big_screen_session-experienced'),
    (r'^(?P<slug>(\w+-?)+)/results/$', 'results'),
    (r'^(?P<slug>(\w+-?)+)/results/pdf/$', 'results_pdf'),
    (r'^(?P<slug>(\w+-?)+)/results/pdf/winners/$', 'results_pdf_winners'),
    (r'^(?P<slug>(\w+-?)+)/results/pdf/overall/$', 'results_pdf_overall'),


    url(r'^(?P<slug>[\w-]+)/new-leaderboard/(?P<mode>[\w-]+)/(?P<format>[\w-]+)/', views.NewLeaderboard.as_view(), name='new_leaderboard'),
    url(r'^(?P<slug>[\w-]+)/new-results/(?P<mode>[\w-]+)/(?P<format>[\w-]+)/', views.NewResults.as_view(), name='new_results'),
)
