# -*- coding: utf-8 -*-

import os
import re
from urlparse import urlparse
from django.db import models
from json import dumps as json_dump
from django.core.cache import get_cache
from random import choice
from django.dispatch import receiver

cache = get_cache('default')
PASTIES_INDEX_CACHE_KEY = 'pasties_index'

def _reset_pasties_index_cache(queryset):
    index = tuple(queryset.values_list('id', flat=True))
    cache.set(PASTIES_INDEX_CACHE_KEY, index)
    return index

class PastiesManager(models.Manager):
    def get_random(self):
        index = cache.get(PASTIES_INDEX_CACHE_KEY)
        if not index:
            index = _reset_pasties_index_cache(self.get_query_set())
        return self.get_query_set().get(id=choice(index))

class Pasty(models.Model):
    text = models.TextField(u'Текст пирожка')
    date = models.DateTimeField(u'Дата публикации', blank=True, null=True)
    source = models.URLField(u'Источник', blank=True)
    votes = models.IntegerField(u'Голосов', default=0, null=True)
    source_pattern = re.compile(r'''http://(?:www\.)?(.+)''')

    objects = PastiesManager()

    def short_text(self):
        return self.text[:37].replace(os.linesep, ' \ ') + '...'

    @property
    def source_title(self):
        return urlparse(self.source).hostname

    def __unicode__(self):
        return self.short_text()

    FIELDS_TO_SERIALIZE = 'text', 'source_title'

    def json_serialize(self):
        return json_dump(dict(
            (name, getattr(self, name, '')) for name in self.FIELDS_TO_SERIALIZE
        ))

    # FIXME мог бы быть @classmethod, было бы логичней
    # FIXME два запроса это слишком, можно было бы отлавливать IndexError
    # FIXME Долгий order_by('?')
    # @staticmethod
    # def rnd():
    #     if Pasty.objects.count() == 0:
    #         return None
    #     return Pasty.objects.order_by('?')[0]

@receiver(models.signals.post_delete, sender=Pasty)
@receiver(models.signals.post_save, sender=Pasty)
def reset_pasties_index_cache_on_signal(sender, **kwargs):
    if kwargs.get('created', True):
        _reset_pasties_index_cache(Pasty.objects)



class Source(models.Model):
    title = models.TextField(u'Название источника')
    url = models.URLField(u'Ссылка')
    sync_url = models.URLField(u'URL синхронизации', blank=True)
    sync_date = models.DateTimeField(u'Дата последней синхронизации', blank=True, null=True)
    parser_pattern = re.compile('[.-]')

    def __unicode__(self):
        return self.title

    def parser(self):
        return self.parser_pattern.sub('_', self.title)
