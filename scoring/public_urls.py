from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from scores import views


urlpatterns = [
    url('^$', views.ResultsSummaryFromCache.as_view(), name='summary'),
    url('^(?P<mode>by-round|team|seedings)/$', views.ResultsFromCache.as_view(), name='mode-detail'),
]

urlpatterns += staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
