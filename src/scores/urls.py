from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('scores.views',
    (r'^(?P<slug>(\w+-?)+)/input-scores/$', 'input_scores'),
    (r'^(?P<slug>(\w+-?)+)/input-arrows/(?P<round_id>\d+)/doz(?P<dozen>\d+)/boss(?P<boss>\d+)/$', 'input_arrows'),
)
