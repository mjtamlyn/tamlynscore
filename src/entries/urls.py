from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('entries.views',
    (r'^$', 'tournaments'),
    (r'^(?P<slug>[\w-]+)/$', 'competition_index'),
)
