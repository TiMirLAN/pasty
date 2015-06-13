# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Source.parser_name'
        db.add_column(u'core_source', 'parser_name',
                      self.gf('django.db.models.fields.CharField')(default=u'rss', max_length=20),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Source.parser_name'
        db.delete_column(u'core_source', 'parser_name')


    models = {
        u'core.pasty': {
            'Meta': {'object_name': 'Pasty'},
            'date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pasties'", 'to': u"orm['core.Source']"}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'votes': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'})
        },
        u'core.source': {
            'Meta': {'object_name': 'Source'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parser_name': ('django.db.models.fields.CharField', [], {'default': "u'rss'", 'max_length': '20'}),
            'sync_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sync_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'title': ('django.db.models.fields.TextField', [], {}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['core']