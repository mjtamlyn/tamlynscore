from django.urls import path

from . import views

urlpatterns = [
    path('', views.LeagueList.as_view(), name='league-list'),
    path('<slug:league_slug>/', views.LeagueDetail.as_view(), name='league-detail'),
    path('<slug:league_slug>/<slug:season_slug>/', views.SeasonDetail.as_view(), name='season-detail'),
    path('<slug:league_slug>/<slug:season_slug>/<slug:leg_index>/<slug:mode>/<slug:format>/', views.Results.as_view(), name='leg-results'),
]
