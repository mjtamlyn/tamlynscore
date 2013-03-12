from django.conf import settings
from django.conf.urls import *
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('',
    (r'', include('core.urls')),
    (r'^tournaments/', include('entries.urls')),
    (r'^tournaments/', include('scores.urls')),
    (r'^tournaments/', include('olympic.urls')),
    (r'^accounts/', include('accounts.urls')),
    (r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
