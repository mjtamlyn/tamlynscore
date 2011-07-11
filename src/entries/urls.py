from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('entries.views',
    (r'^$', 'tournaments'),
    (r'^(?P<slug>[\w-]+)/$', 'competition_index'),
    (r'^(?P<slug>[\w-]+)/entries/$', 'entries'),
    (r'^(?P<slug>[\w-]+)/target-list/$', 'target_list'),
    (r'^(?P<slug>[\w-]+)/target-list/pdf/$', 'target_list_pdf'),
)
