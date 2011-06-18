from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

from records.views import *

urlpatterns = patterns('records.views',
    (r'^$', 'index'),
    (r'^competition/(?P<competition_id>\d+)/$', 'competition_index'),
    (r'^add-scores/(?P<round_id>\d+)/$', AddScoresView.as_view()),
    (r'^new-club/$', NewClubView.as_view()),
)
