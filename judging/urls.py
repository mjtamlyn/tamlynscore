from django.urls import path

from . import views

urlpatterns = [
    path('<slug>/judges/', views.JudgeIndex.as_view(), name='judge_index'),
    path('login/<id>/', views.JudgeAuthenticate.as_view(), name='judge_authenticate'),
]
