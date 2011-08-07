from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('olympic.views',
    (r'^(?P<slug>[\w-]+)/$', 'olympic_index'),
    (r'^(?P<slug>[\w-]+)/score-sheets/(?P<round_id>\d+)/$', 'olympic_score_sheet'),
    (r'^(?P<slug>[\w-]+)/results/$', 'olympic_results'),
)
