from django.conf.urls import url, include
import django.contrib.auth.views as auth_views


urlpatterns = [
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
    url(r'', include('django.contrib.auth.urls')),
]
