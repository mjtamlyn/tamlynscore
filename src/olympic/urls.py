from django.conf.urls.defaults import *

urlpatterns = patterns('olympic.views',
    (r'^(?P<slug>[\w-]+)/$', 'olympic_index'),
    (r'^(?P<slug>[\w-]+)/score-sheets/(?P<round_id>\d+)/$', 'olympic_score_sheet'),
    (r'^(?P<slug>[\w-]+)/results/$', 'olympic_results'),
    (r'^(?P<slug>[\w-]+)/tree/$', 'olympic_tree'),
)
