from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('core.views',

    (r'^$', 'index'),
    (r'^clubs/$', 'clubs'),

    #TODO: accounts (login/logout etc)
)
