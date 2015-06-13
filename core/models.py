# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from urlparse import urlparse
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from json import dumps as json_dump
from django.core.cache import get_cache
from random import choice
from django.dispatch import receiver
from os import linesep
from django.template.defaultfilters import striptags
from .parsers import rss, perashki_ru, stishkipirozhki_ru

# PASTY
cache = get_cache('default')
PASTIES_INDEX_CACHE_KEY = 'pasties_index'
PASTIES_BLOCKS_CACHE_KEY = 'pasties_blocks'

def _reset_pasties_index_cache(queryset):
    data = queryset.only('id', 'votes').order_by('votes').values_list('id', 'votes')
    if data:
        index, votes = zip(*data)
        blocks_offset, max_votes, length = [0], votes[0], len(votes)
        for idx,  vts in enumerate(votes):
            if vts > max_votes:
                max_votes = vts
                blocks_offset.append(idx-length)
    else:
        index, blocks_offset = [], []
    cache.set(PASTIES_INDEX_CACHE_KEY, index)
    cache.set(PASTIES_BLOCKS_CACHE_KEY, blocks_offset)
    return index, blocks_offset

class PastiesManager(models.Manager):
    def get_random(self):
        index = cache.get(PASTIES_INDEX_CACHE_KEY)
        offsets = cache.get(PASTIES_BLOCKS_CACHE_KEY)
        if not index:
            index, offsets = _reset_pasties_index_cache(self.get_query_set())
        ids_block = index[choice(offsets):]
        return self.get_query_set().select_related('source').get(id=choice(ids_block))

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
        to='Source',
        db_index=True,
        related_name='pasties',
        verbose_name='Источник'
    )
    votes = models.IntegerField(
        default=0,
        null=True,
        verbose_name=u'Голосов',
    )

    objects = PastiesManager()

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

    class Meta:
        verbose_name = 'Пирожок'
        verbose_name_plural = 'Пирожки'

@receiver(models.signals.post_delete, sender=Pasty)
@receiver(models.signals.post_save, sender=Pasty)
def reset_pasties_index_cache_on_signal(sender, **kwargs):
    if kwargs.get('created', True):
        _reset_pasties_index_cache(Pasty.objects)

# SOURCE
PARSERS = dict((f.func_name, f) for f in [rss, stishkipirozhki_ru, perashki_ru])

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
    parser_name = models.CharField(
        max_length=20,
        default=PARSERS.keys()[0],
        choices=tuple((k, k) for k in PARSERS.keys()),
        verbose_name='Парсер'
    )
    STATES = 'Ошибка', 'Синхронизация', 'Готов'
    state_code = models.SmallIntegerField(
        default=2,
        editable=False,
        choices=tuple(s for s in enumerate(STATES)),
        verbose_name='Состояние'
    )

    def __unicode__(self):
        return self.title

    @property
    def parser(self):
        return PARSERS[self.parser_name]

    @staticmethod
    def _make_text(html):
        return striptags(html.replace('<br />', '\n'))

    def _set_state_code(self, code):
        self.state_code = code
        self.save()

    def sync(self):
        self._set_state_code(1)
        try:
            newer_then = self.pasties.only('date').latest('date').date
        except ObjectDoesNotExist:
            newer_then = None
        try:
            entries = self.parser(self.sync_url, newer_then)
            pasties = [Pasty(
                text=self._make_text(entry['html']),
                date=entry['published'],
                source=self
            ) for entry in entries]
            # TODO нужно что-то более умное для фильтра.
            self.pasties.bulk_create([p for p in pasties if len(p.text.split('\n')) == 4])
            self._set_state_code(2)
        except Exception as e:
            self._set_state_code(0)
            raise e

    class Meta:
        verbose_name = 'Источник'
        verbose_name_plural = 'Источники'

