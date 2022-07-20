from django.conf.urls import url

from . import views


urlpatterns = [
    url('^$', views.LeagueList.as_view(), name='league-list'),
    url(r'^(?P<league_slug>[\w-]+)/$', views.LeagueDetail.as_view(), name='league-detail'),
    url(r'^(?P<league_slug>[\w-]+)/(?P<season_slug>[\w-]+)/$', views.SeasonDetail.as_view(), name='season-detail'),
    url(r'^(?P<league_slug>[\w-]+)/(?P<season_slug>[\w-]+)/(?P<leg_index>\d+)/(?P<mode>[\w-]+)/(?P<format>[\w-]+)/', views.Results.as_view(), name='leg-results'),
]
