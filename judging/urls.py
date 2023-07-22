from django.urls import path

from . import views

urlpatterns = [
    path('<slug>/judges/', views.JudgeIndex.as_view(), name='judge_index'),
    path('<slug>/judges/inspection/', views.JudgeInspection.as_view(), name='judge_inspection'),
    path('login/<id>/', views.JudgeAuthenticate.as_view(), name='judge_authenticate'),
]
