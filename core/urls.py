from django.conf.urls.defaults import *

import views

urlpatterns = patterns('core.views',
    url(r'^$', views.Index.as_view(), name='index'),
    url(r'^clubs/$', 'club_list', name='club_list'),
    url(r'^clubs/(?P<slug>[\w-]+)/$', 'club_detail', name='club_detail'),
)
