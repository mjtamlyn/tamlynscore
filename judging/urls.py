from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path('<slug>/judges/', views.JudgeIndex.as_view(), name='judge_index'),
    path('<slug>/judges/inspection/', csrf_exempt(views.JudgeInspection.as_view()), name='judge_inspection'),
    path('<slug>/judges/matches/', views.JudgeMatches.as_view(), name='judge_matches'),
    path('login/<id>/', views.JudgeAuthenticate.as_view(), name='judge_authenticate'),
]
