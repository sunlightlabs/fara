# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ProposedSales'
        db.create_table(u'arms_sales_proposedsales', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=2, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('dsca_link', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('pdf_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('print_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'arms_sales', ['ProposedSales'])


    def backwards(self, orm):
        # Deleting model 'ProposedSales'
        db.delete_table(u'arms_sales_proposedsales')


    models = {
        u'arms_sales.proposedsales': {
            'Meta': {'object_name': 'ProposedSales'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '2', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'dsca_link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'pdf_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'print_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['arms_sales']