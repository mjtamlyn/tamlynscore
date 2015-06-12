from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from scores import views


urlpatterns = [
    url(r'(?P<mode>[\w-]+)/', views.ResultsFromCache.as_view()),
]

urlpatterns += staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
