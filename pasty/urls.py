# coding=utf-8
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('core.views',
    url(r'^$', 'index', name='home'),
    url(r'^one/$', 'one', name='one'),
    # FIXME почему это вообще смотрит наружу
    # url(r'^sources$', 'core.views.sources', name='sources'),
    # url(r'^sync$', 'core.views.sync', name='sync'),

    url(r'^admin/', include(admin.site.urls)),
)
