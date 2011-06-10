from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('records.views',
    (r'^$', 'index'),
    (r'^competition/(?P<competition_id>\d+)/$', 'competition_index'),
)
