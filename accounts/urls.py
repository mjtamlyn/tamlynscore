import django.contrib.auth.views as auth_views
from django.conf.urls import url, include
from django.core.urlresolvers import reverse_lazy

from .forms import RegisterForm


urlpatterns = [
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout_then_login, name='logout'),
    url(r'^accounts/register/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
        auth_views.password_reset_confirm, {
            'set_password_form': RegisterForm,
            'template_name': 'registration/register.html',
            'post_reset_redirect': reverse_lazy('index'),
        }, name='register'),
    url(r'', include('django.contrib.auth.urls')),
]
