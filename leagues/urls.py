from django.conf.urls import url

from . import views


urlpatterns = [
    url('^$', views.LeagueList.as_view(), name='league-list'),
    url('^(?P<league_slug>[\w-]+)/$', views.LeagueDetail.as_view(), name='league-detail'),
    url('^(?P<league_slug>[\w-]+)/(?P<season_slug>[\w-]+)/$', views.SeasonDetail.as_view(), name='season-detail'),
]
