from django.urls import path

from scores import views


urlpatterns = [
    path('<slug:slug>/input-scores/', views.InputScores.as_view(), name='input_scores'),
    path('<slug:slug>/input-scores/mobile/', views.InputScoresMobile.as_view(), name='input_scores_mobile'),
    path('<slug:slug>/input-arrows/<int:session_id>/doz<int:dozen>/boss<int:boss>/', views.InputArrowsView.as_view(), name='input_arrows'),
    path('<slug:slug>/input-arrows/archer/<int:score_id>/', views.InputArrowsArcher.as_view(), name='input_arrows_archer'),
    path('<slug:slug>/input-scores/team/<int:team_id>/doz<int:dozen>/', views.InputDozensTeam.as_view(), name='input_dozens_team'),
    path('<slug:slug>/input-dozens/<int:session_id>/doz<int:dozen>/boss<int:boss>/', views.InputDozens.as_view(), name='input_dozens'),
    path('<slug:slug>/input-arrows/<int:session_id>/doz<int:dozen>/boss<int:boss>mobile/', views.InputArrowsViewMobile.as_view(), name='input_arrows_mobile'),
    path('<slug:slug>/leaderboard/<slug:mode>/<slug:format>/', views.Leaderboard.as_view(), name='leaderboard'),
    path('<slug:slug>/results/<slug:mode>/<slug:format>/', views.Results.as_view(), name='results'),
    path('<slug:slug>/rankings-export.csv', views.RankingsExport.as_view(), name='rankings_export'),
]
