# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from urlparse import urlparse
from django.db import models
from json import dumps as json_dump
from django.core.cache import get_cache
from random import choice
from django.dispatch import receiver
from os import linesep
import re

# SOURCE
class Source(models.Model):
    title = models.TextField(
        verbose_name=u'Название источника'
    )
    url = models.URLField(
        verbose_name=u'Ссылка'
    )
    sync_url = models.URLField(
        verbose_name=u'URL синхронизации'
    )
    sync_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=u'Дата последней синхронизации'
    )
    parser_pattern = re.compile('[.-]')

    def __unicode__(self):
        return self.title

    def parser(self):
        return self.parser_pattern.sub('_', self.title)

    class Meta:
        verbose_name = 'Источник'
        verbose_name_plural = 'Источники'


# PASTY
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
    text = models.TextField(
        verbose_name=u'Текст'
    )
    date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=u'Дата публикации',
    )
    source = models.ForeignKey(
        to=Source,
        db_index=True,
        related_name='pasties',
        verbose_name='Источник'
    )
    votes = models.IntegerField(
        default=0,
        null=True,
        verbose_name=u'Голосов',
    )
    # FIXME Зачем тут вообще был source_pattern?

    objects = PastiesManager()

    # FIXME просто нет особого смысла
    # def short_text(self):
    #     return self.text[:37].replace(linesep, ' \ ') + '...'

    def html(self):
        return self.text.replace(linesep, '</br>')

    @property
    def source_title(self):
        return urlparse(self.source.url).hostname

    def __unicode__(self):
        return self.text

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

    class Meta:
        verbose_name = 'Пирожок'
        verbose_name_plural = 'Пирожки'

@receiver(models.signals.post_delete, sender=Pasty)
@receiver(models.signals.post_save, sender=Pasty)
def reset_pasties_index_cache_on_signal(sender, **kwargs):
    if kwargs.get('created', True):
        _reset_pasties_index_cache(Pasty.objects)
