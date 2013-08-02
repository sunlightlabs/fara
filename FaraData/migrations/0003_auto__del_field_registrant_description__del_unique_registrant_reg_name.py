# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Client', fields ['client_name']
        #db.delete_unique(u'FaraData_client', ['client_name'])

        # Removing unique constraint on 'Registrant', fields ['reg_name']
        #db.delete_unique(u'FaraData_registrant', ['reg_name'])

        # Deleting field 'Registrant.description'
        db.delete_column(u'FaraData_registrant', 'description')

        # Adding field 'Client.description'
        db.add_column(u'FaraData_client', 'description',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Registrant.description'
        db.add_column(u'FaraData_registrant', 'description',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding unique constraint on 'Registrant', fields ['reg_name']
        db.create_unique(u'FaraData_registrant', ['reg_name'])

        # Deleting field 'Client.description'
        db.delete_column(u'FaraData_client', 'description')

        # Adding unique constraint on 'Client', fields ['client_name']
        db.create_unique(u'FaraData_client', ['client_name'])


    models = {
        u'FaraData.client': {
            'Meta': {'object_name': 'Client'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'client_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'client_type': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Location']"}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        u'FaraData.contact': {
            'Meta': {'object_name': 'Contact'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Client']", 'null': 'True'}),
            'contact_type': ('django.db.models.fields.CharField', [], {'default': "'U'", 'max_length': '1'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'lobbyist': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['FaraData.Lobbyist']", 'null': 'True', 'blank': 'True'}),
            'recipient': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['FaraData.Recipient']", 'symmetrical': 'False'}),
            'registrant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Registrant']"})
        },
        u'FaraData.contribution': {
            'Meta': {'object_name': 'Contribution'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'lobbyist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Lobbyist']", 'null': 'True', 'blank': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Recipient']"}),
            'registrant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Registrant']"})
        },
        u'FaraData.disbursement': {
            'Meta': {'object_name': 'Disbursement'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Client']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'purpose': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'registrant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Registrant']"}),
            'subcontractor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subcontractor'", 'null': 'True', 'to': u"orm['FaraData.Registrant']"})
        },
        u'FaraData.gift': {
            'Meta': {'object_name': 'Gift'},
            'client': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['FaraData.Client']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'purpose': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Recipient']", 'null': 'True', 'blank': 'True'}),
            'registrant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Registrant']"})
        },
        u'FaraData.lobbyist': {
            'Meta': {'object_name': 'Lobbyist'},
            'PAC_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lobby_id': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'lobbyist_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'})
        },
        u'FaraData.location': {
            'Meta': {'object_name': 'Location'},
            'country_grouping': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'FaraData.metadata': {
            'Meta': {'object_name': 'MetaData'},
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'form': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'is_amendment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reviewed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'upload_date': ('django.db.models.fields.DateField', [], {'null': 'True'})
        },
        u'FaraData.payment': {
            'Meta': {'object_name': 'Payment'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Client']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'fee': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'purpose': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'registrant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Registrant']"}),
            'subcontractor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'payment_subcontractor'", 'null': 'True', 'to': u"orm['FaraData.Registrant']"})
        },
        u'FaraData.recipient': {
            'Meta': {'object_name': 'Recipient'},
            'agency': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'crp_id': ('django.db.models.fields.CharField', [], {'max_length': '9', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True'}),
            'office_detail': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'state_local': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'})
        },
        u'FaraData.registrant': {
            'Meta': {'object_name': 'Registrant'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'clients': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['FaraData.Client']", 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'lobbyists': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['FaraData.Lobbyist']", 'null': 'True', 'blank': 'True'}),
            'reg_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'reg_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'terminated_clients': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'terminated_clients'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['FaraData.Client']"}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['FaraData']