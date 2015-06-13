# coding=utf-8
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('core.views',
    url(r'^$', 'index', name='home'),
    url(r'^one/$', 'one', name='one'),

    url(r'^admin/', include(admin.site.urls)),
)
