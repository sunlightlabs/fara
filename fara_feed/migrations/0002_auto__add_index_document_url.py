# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'Document', fields ['url']
        db.create_index(u'fara_feed_document', ['url'])


    def backwards(self, orm):
        # Removing index on 'Document', fields ['url']
        db.delete_index(u'fara_feed_document', ['url'])


    models = {
        u'fara_feed.document': {
            'Meta': {'object_name': 'Document'},
            'doc_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reg_id': ('django.db.models.fields.IntegerField', [], {'max_length': '5'}),
            'stamp_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'db_index': 'True'})
        }
    }

    complete_apps = ['fara_feed']