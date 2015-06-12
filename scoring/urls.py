from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    url(r'', include('core.urls')),
    url(r'^tournaments/', include('entries.urls')),
    url(r'^tournaments/', include('scores.urls')),
    url(r'^tournaments/olympic/', include('olympic.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^admin/', include(admin.site.urls)),
]

urlpatterns += staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
