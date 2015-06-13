# coding=utf-8
from __future__ import unicode_literals
from .models import Source
from pasty.celery import app


@app.task()
def sync_sources(queryset=Source.objects):
    for source in queryset.all():
        print 'Synchronizing "%s".' % source
        source.sync()
