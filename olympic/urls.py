from django.urls import path

from . import views

urlpatterns = [
    path('<slug:slug>/', views.OlympicIndex.as_view(), name='olympic_index'),
    path('<slug:slug>/setup/', views.OlympicSetup.as_view(), name='olympic_setup'),
    path('<slug:slug>/<int:round_id>/', views.OlympicInputIndex.as_view(), name='olympic_input_index'),
    path('<slug:slug>/input/<int:seed_pk>/', views.OlympicInput.as_view(), name='olympic_input'),
    path('<slug:slug>/score-sheets/<int:round_id>/', views.OlympicScoreSheet.as_view(), name='olympic_score_sheet'),
    path('<slug:slug>/results/', views.OlympicResults.as_view(), name='olympic_results'),
    path('<slug:slug>/tree/', views.OlympicTree.as_view(), name='olympic_tree'),
    path('<slug:slug>/tree/pdf/', views.OlympicTreePdf.as_view(), name='olympic_tree_pdf'),
    path('<slug:slug>/field-plan/', views.FieldPlan.as_view(), name='olympic_field_plan'),
]
