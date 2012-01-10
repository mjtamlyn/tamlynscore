from django.conf.urls.defaults import *

urlpatterns = patterns('scores.views',
    (r'^(?P<slug>(\w+-?)+)/input-scores/$', 'input_scores'),
    (r'^(?P<slug>(\w+-?)+)/input-arrows/(?P<round_id>\d+)/doz(?P<dozen>\d+)/boss(?P<boss>\d+)/$', 'input_arrows'),
    (r'^(?P<slug>(\w+-?)+)/leaderboard/$', 'leaderboard'),
    (r'^(?P<slug>(\w+-?)+)/leaderboard/big-screen/$', 'leaderboard_big_screen'),
    (r'^(?P<slug>(\w+-?)+)/results/$', 'results'),
    (r'^(?P<slug>(\w+-?)+)/results/pdf/$', 'results_pdf'),
)
