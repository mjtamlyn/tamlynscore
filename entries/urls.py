from django.urls import path

from entries import views

urlpatterns = [
    path('', views.CompetitionList.as_view(), name='tournaments_list'),
    path('add/', views.CompetitionCreate.as_view(), name='competition_create'),
    path('<slug:slug>/', views.CompetitionDetail.as_view(), name='competition_detail'),
    path('<slug:slug>/edit/', views.CompetitionUpdate.as_view(), name='competition_update'),
    path('<slug:slug>/entries/', views.EntryList.as_view(), name='entry_list'),
    path('<slug:slug>/entries/batch/', views.BatchEntryStart.as_view(), name='batch_entry_start'),
    path('<slug:slug>/entries/search/', views.ArcherSearch.as_view(), name='archer_search'),
    path('<slug:slug>/entries/add/<int:archer_id>/', views.EntryAdd.as_view(), name='entry_add'),
    path('<slug:slug>/entries/edit/<int:entry_id>/', views.EntryUpdate.as_view(), name='entry_update'),
    path('<slug:slug>/entries/delete/<int:entry_id>/', views.EntryDelete.as_view(), name='entry_delete'),
    path('<slug:slug>/target-list/', views.TargetList.as_view(), name='target_list'),
    path('<slug:slug>/target-list/edit/', views.TargetListEdit.as_view(), name='target_list_edit'),
    path('<slug:slug>/target-list/pdf/', views.TargetListPdf.as_view(), name='target_list_pdf'),
    path('<slug:slug>/target-list/lunch/', views.TargetListLunch.as_view()),
    path('<slug:slug>/score-sheets/', views.ScoreSheets.as_view(), name='score_sheets'),
    path('<slug:slug>/score-sheets/<int:round_id>/', views.ScoreSheetsPdf.as_view(), name='score_sheets_pdf'),
    path('<slug:slug>/score-sheets/session/<int:session_id>/', views.SessionScoreSheetsPdf.as_view(), name='session_score_sheets_pdf'),
    path('<slug:slug>/running-slips/<int:round_id>/', views.RunningSlipsPdf.as_view(), name='running_slips_pdf'),

    path('<slug:slug>/registration/', views.Registration.as_view(), name='registration'),
]
