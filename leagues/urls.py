from django.urls import path

from . import views

urlpatterns = [
    path('organiser/<slug:league_slug>/create/', views.LegCreateView.as_view(), name='leg-create'),
    path('organiser/<slug:league_slug>/<slug:season_slug>/<slug:leg_slug>/edit/', views.LegUpdateView.as_view(), name='leg-update'),

    path('', views.LeagueList.as_view(), name='league-list'),
    path('<slug:league_slug>/', views.LeagueDetail.as_view(), name='league-detail'),
    path('<slug:league_slug>/<slug:season_slug>/', views.SeasonDetail.as_view(), name='season-detail'),
    path('<slug:league_slug>/<slug:season_slug>/<slug:leg_slug>/<slug:mode>/<slug:format>/', views.Results.as_view(), name='leg-results'),
]
