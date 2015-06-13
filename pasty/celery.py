# coding=utf-8
from __future__ import unicode_literals, absolute_import
from django.conf import settings
from celery import Celery
from os import environ

environ.setdefault('DJANGO_SETTINGS_MODULE', 'pasty.settings')

app = Celery('pasty')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
