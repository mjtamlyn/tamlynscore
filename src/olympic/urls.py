from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('olympic.views',
    (r'^(?P<slug>[\w-]+)/$', 'olympic_index'),
)
