from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

urlpatterns = [
    path('', include('core.urls')),
    path('leagues/', include('leagues.urls')),
    path('tournaments/', include('entries.urls')),
    path('tournaments/', include('scores.urls')),
    path('tournaments/olympic/', include('olympic.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
