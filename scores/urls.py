from django.urls import path

from scores import redirects, views

urlpatterns = [
    path('<slug:slug>/input-scores/', views.InputScores.as_view(), name='input_scores'),
    path('<slug:slug>/input-arrows/<int:session_id>/doz<int:dozen>/boss<int:boss>/', views.InputArrowsView.as_view(), name='input_arrows'),
    path('<slug:slug>/input-dozens/<int:session_id>/doz<int:dozen>/boss<int:boss>/', views.InputDozens.as_view(), name='input_dozens'),
    path('<slug:slug>/leaderboard/<slug:mode>/<slug:format>/', views.Leaderboard.as_view(), name='leaderboard'),
    path('<slug:slug>/score-sheet/<int:score_id>/', views.ScoreSheet.as_view(), name='score_sheet'),
    path('<slug:slug>/results/<slug:mode>/<slug:format>/', views.Results.as_view(), name='results'),
    path('<slug:slug>/rankings-export.csv', views.RankingsExport.as_view(), name='rankings_export'),

    # Redirects
    path('<slug:slug>/input-arrows/archer/<int:score_id>/', redirects.input_arrows_archer),
]

archer_urlpatterns = [
    path('', views.TargetInput.as_view(), name='target-input'),
    path('auth/<uuid:id>/', views.EntryAuthenticate.as_view(), name='entry-authenticate'),
    path('api/', views.TargetAPIRoot.as_view(), name='target-api-root'),
    path('api/<int:session>/', views.TargetAPISession.as_view(), name='target-api-session'),
]
