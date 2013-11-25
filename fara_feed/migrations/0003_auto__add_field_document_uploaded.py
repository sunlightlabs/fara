# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Document.uploaded'
        db.add_column(u'fara_feed_document', 'uploaded',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Document.uploaded'
        db.delete_column(u'fara_feed_document', 'uploaded')


    models = {
        u'fara_feed.document': {
            'Meta': {'object_name': 'Document'},
            'doc_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reg_id': ('django.db.models.fields.IntegerField', [], {'max_length': '5'}),
            'stamp_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'uploaded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'db_index': 'True'})
        }
    }

    complete_apps = ['fara_feed']