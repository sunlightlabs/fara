# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Document'
        db.create_table(u'fara_feed_document', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('reg_id', self.gf('django.db.models.fields.IntegerField')(max_length=5)),
            ('doc_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True)),
            ('stamp_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('processed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'fara_feed', ['Document'])


    def backwards(self, orm):
        # Deleting model 'Document'
        db.delete_table(u'fara_feed_document')


    models = {
        u'fara_feed.document': {
            'Meta': {'object_name': 'Document'},
            'doc_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reg_id': ('django.db.models.fields.IntegerField', [], {'max_length': '5'}),
            'stamp_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['fara_feed']