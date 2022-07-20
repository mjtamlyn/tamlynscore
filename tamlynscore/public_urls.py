from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from scores import views

urlpatterns = [
    path('', views.ResultsSummaryFromCache.as_view(), name='summary'),
    path('<slug:mode>', views.ResultsFromCache.as_view(), name='mode-detail'),
]

urlpatterns += staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
