from django.conf.urls.defaults import *

urlpatterns = patterns('core.views',

    url(r'^$', 'index', name='index'),
    url(r'^clubs/$', 'club_list', name='club_list'),
    url(r'^clubs/(?P<slug>[\w-]+)/$', 'club_detail', name='club_detail'),

)
