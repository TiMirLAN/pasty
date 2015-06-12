# coding=utf-8
from __future__ import unicode_literals
from feedparser import parse as _rss_parse
from django.utils.timezone import datetime as tz_dt
from time import mktime

__author__ = 'timirlan'

def rss(source_url, newer_then=None):
    rss_data = _rss_parse(source_url)
    entries = [dict(
        html=entry.summary,
        published=tz_dt.fromtimestamp(mktime(entry.published_parsed))
    ) for entry in rss_data.entries]
    if newer_then:
        return [entry for entry in entries if entry['published'] > newer_then]
    return entries

def stishkipirozhki_ru(source_url, newer_then=None):
    """
    Парсер HTML на BeautifulSoup для вытягивания оценок с сайта
    """
    return []

def perashki_ru(source_url, newer_then=None):
    """
    Парсер HTML на BeautifulSoup для вытягивания оценок с сайта
    """
    return []
