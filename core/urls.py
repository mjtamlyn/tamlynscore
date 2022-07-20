from django.urls import path

from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('clubs/', views.ClubList.as_view(), name='club_list'),
    path('clubs/add/', views.ClubCreate.as_view(), name='club_create'),
    path('clubs/<slug:club_slug>/', views.ClubDetail.as_view(), name='club_detail'),
    path('clubs/<slug:club_slug>/edit/', views.ClubUpdate.as_view(), name='club_update'),
    path('clubs/<slug:club_slug>/archers/add/', views.ClubArcherCreate.as_view(), name='club_archer_create'),
    path('clubs/<slug:club_slug>/archived/', views.ArchiveArcherList.as_view(), name='archive_archer_list'),
    path('counties/add/', views.CountyCreate.as_view(), name='county_create'),
    path('archer/add/', views.ArcherCreate.as_view(), name='archer_create'),
    path('archer/<int:pk>)/', views.ArcherDetail.as_view(), name='archer_detail'),
    path('archer/<int:pk>/edit/', views.ArcherUpdate.as_view(), name='archer_update'),
    path('archer/<int:pk>)/archive/', views.ArcherArchive.as_view(), name='archer_archive'),
]
