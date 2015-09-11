from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.Index.as_view(), name='index'),
    url(r'^clubs/$', views.ClubList.as_view(), name='club_list'),
    url(r'^clubs/add/$', views.ClubCreate.as_view(), name='club_create'),
    url(r'^clubs/(?P<club_slug>[\w-]+)/$', views.ClubDetail.as_view(), name='club_detail'),
    url(r'^clubs/(?P<club_slug>[\w-]+)/edit/$', views.ClubUpdate.as_view(), name='club_update'),
    url(r'^clubs/(?P<club_slug>[\w-]+)/archived/$', views.ArchiveArcherList.as_view(), name='archive_archer_list'),
    url(r'^counties/add/$', views.CountyCreate.as_view(), name='county_create'),
    url(r'^archer/add/$', views.ArcherCreate.as_view(), name='archer_create'),
    url(r'^archer/(?P<pk>\d+)/$', views.ArcherDetail.as_view(), name='archer_detail'),
    url(r'^archer/(?P<pk>\d+)/edit/$', views.ArcherUpdate.as_view(), name='archer_update'),
    url(r'^archer/(?P<pk>\d+)/archive/$', views.ArcherArchive.as_view(), name='archer_archive'),
]
