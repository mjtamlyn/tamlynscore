from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('records.views',
    (r'^$', 'index'),
    (r'^competition/(?P<slug>(\w+-?)+)/$', 'competition_index'),
    (r'^add-scores/(?P<round_id>\d+)/$', 'add_scores'),
    (r'^add-arrow-values/(?P<round_id>\d+)/$', 'add_arrow_values_index'),
    (r'^add-arrow-values/(?P<round_id>\d+)/target/(?P<target_no>\d+)/doz/(?P<doz_no>\d+)/$', 'add_arrow_values'),
    (r'^new-club/$', 'new_club'),
)
