from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^(?P<slug>[\w-]+)/$', views.OlympicIndex.as_view(), name='olympic_index'),
    url(r'^(?P<slug>[\w-]+)/setup/$', views.OlympicSetup.as_view(), name='olympic_setup'),
    url(r'^(?P<slug>[\w-]+)/(?P<round_id>\d+)/$', views.OlympicInputIndex.as_view(), name='olympic_input_index'),
    url(r'^(?P<slug>[\w-]+)/input/(?P<seed_pk>\d+)/$', views.OlympicInput.as_view(), name='olympic_input'),
    url(r'^(?P<slug>[\w-]+)/score-sheets/(?P<round_id>\d+)/$', views.OlympicScoreSheet.as_view(), name='olympic_score_sheet'),
    url(r'^(?P<slug>[\w-]+)/results/$', views.OlympicResults.as_view(), name='olympic_results'),
    url(r'^(?P<slug>[\w-]+)/tree/$', views.OlympicTree.as_view(), name='olympic_tree'),
    url(r'^(?P<slug>[\w-]+)/field-plan/$', views.FieldPlan.as_view(), name='olympic_field_plan'),
]
