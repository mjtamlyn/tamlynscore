from django.conf.urls import patterns, url

import views

urlpatterns = patterns('core.views',
    url(r'^$', views.Index.as_view(), name='index'),
    url(r'^clubs/$', views.ClubList.as_view(), name='club_list'),
    url(r'^clubs/(?P<slug>[\w-]+)/$', views.ClubDetail.as_view(), name='club_detail'),
    url(r'^archer/(?P<pk>\d+)/$', views.ArcherUpdate.as_view(), name='archer_update'),
)
