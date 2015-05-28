from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^(?P<slug>[\w-]+)/$', views.olympic_index, name='olympic_index'),
    url(r'^(?P<slug>[\w-]+)/pdf/$', views.OlympicSeedingsPDF.as_view(), name='olympic_pdf'),
    url(r'^(?P<slug>[\w-]+)/input/(?P<seed_pk>\d+)/$', views.OlympicInput.as_view(), name='olympic_input'),
    url(r'^(?P<slug>[\w-]+)/score-sheets/(?P<round_id>\d+)/$', views.olympic_score_sheet),
    url(r'^(?P<slug>[\w-]+)/results/$', views.olympic_results, name='olympic_results'),
    url(r'^(?P<slug>[\w-]+)/tree/$', views.olympic_tree, name='olympic_tree'),
    url(r'^(?P<slug>[\w-]+)/field-plan/$', views.FieldPlan.as_view(), name='olympic_field_plan'),
]
