from django.conf.urls import url

from . import views


urlpatterns = [
    url('^$', views.LeagueList.as_view(), name='league-list'),
]
