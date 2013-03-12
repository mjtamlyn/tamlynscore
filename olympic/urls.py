from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns('olympic.views',
    (r'^(?P<slug>[\w-]+)/$', 'olympic_index'),
    url(r'^(?P<slug>[\w-]+)/input/(?P<seed_pk>\d+)/$', views.OlympicInput.as_view(), name='olympic_input'),
    (r'^(?P<slug>[\w-]+)/score-sheets/(?P<round_id>\d+)/$', 'olympic_score_sheet'),
    (r'^(?P<slug>[\w-]+)/results/$', 'olympic_results'),
    (r'^(?P<slug>[\w-]+)/tree/$', 'olympic_tree'),
)
