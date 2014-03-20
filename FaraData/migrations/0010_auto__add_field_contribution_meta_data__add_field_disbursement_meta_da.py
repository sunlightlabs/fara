# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Contribution.meta_data'
        db.add_column(u'FaraData_contribution', 'meta_data',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['FaraData.MetaData'], null=True, blank=True),
                      keep_default=False)

        # Removing M2M table for field meta_data on 'Contribution'
        db.delete_table(db.shorten_name(u'FaraData_contribution_meta_data'))

        # Adding field 'Disbursement.meta_data'
        db.add_column(u'FaraData_disbursement', 'meta_data',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['FaraData.MetaData'], null=True, blank=True),
                      keep_default=False)

        # Removing M2M table for field meta_data on 'Disbursement'
        db.delete_table(db.shorten_name(u'FaraData_disbursement_meta_data'))

        # Adding field 'Contact.meta_data'
        db.add_column(u'FaraData_contact', 'meta_data',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['FaraData.MetaData'], null=True, blank=True),
                      keep_default=False)

        # Removing M2M table for field meta_data on 'Contact'
        db.delete_table(db.shorten_name(u'FaraData_contact_meta_data'))

        # Adding field 'Gift.meta_data'
        db.add_column(u'FaraData_gift', 'meta_data',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['FaraData.MetaData'], null=True, blank=True),
                      keep_default=False)

        # Removing M2M table for field meta_data on 'Gift'
        db.delete_table(db.shorten_name(u'FaraData_gift_meta_data'))

        # Adding field 'Payment.meta_data'
        db.add_column(u'FaraData_payment', 'meta_data',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['FaraData.MetaData'], null=True, blank=True),
                      keep_default=False)

        # Removing M2M table for field meta_data on 'Payment'
        db.delete_table(db.shorten_name(u'FaraData_payment_meta_data'))


    def backwards(self, orm):
        # Deleting field 'Contribution.meta_data'
        db.delete_column(u'FaraData_contribution', 'meta_data_id')

        # Adding M2M table for field meta_data on 'Contribution'
        m2m_table_name = db.shorten_name(u'FaraData_contribution_meta_data')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contribution', models.ForeignKey(orm[u'FaraData.contribution'], null=False)),
            ('metadata', models.ForeignKey(orm[u'FaraData.metadata'], null=False))
        ))
        db.create_unique(m2m_table_name, ['contribution_id', 'metadata_id'])

        # Deleting field 'Disbursement.meta_data'
        db.delete_column(u'FaraData_disbursement', 'meta_data_id')

        # Adding M2M table for field meta_data on 'Disbursement'
        m2m_table_name = db.shorten_name(u'FaraData_disbursement_meta_data')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('disbursement', models.ForeignKey(orm[u'FaraData.disbursement'], null=False)),
            ('metadata', models.ForeignKey(orm[u'FaraData.metadata'], null=False))
        ))
        db.create_unique(m2m_table_name, ['disbursement_id', 'metadata_id'])

        # Deleting field 'Contact.meta_data'
        db.delete_column(u'FaraData_contact', 'meta_data_id')

        # Adding M2M table for field meta_data on 'Contact'
        m2m_table_name = db.shorten_name(u'FaraData_contact_meta_data')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contact', models.ForeignKey(orm[u'FaraData.contact'], null=False)),
            ('metadata', models.ForeignKey(orm[u'FaraData.metadata'], null=False))
        ))
        db.create_unique(m2m_table_name, ['contact_id', 'metadata_id'])

        # Deleting field 'Gift.meta_data'
        db.delete_column(u'FaraData_gift', 'meta_data_id')

        # Adding M2M table for field meta_data on 'Gift'
        m2m_table_name = db.shorten_name(u'FaraData_gift_meta_data')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gift', models.ForeignKey(orm[u'FaraData.gift'], null=False)),
            ('metadata', models.ForeignKey(orm[u'FaraData.metadata'], null=False))
        ))
        db.create_unique(m2m_table_name, ['gift_id', 'metadata_id'])

        # Deleting field 'Payment.meta_data'
        db.delete_column(u'FaraData_payment', 'meta_data_id')

        # Adding M2M table for field meta_data on 'Payment'
        m2m_table_name = db.shorten_name(u'FaraData_payment_meta_data')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('payment', models.ForeignKey(orm[u'FaraData.payment'], null=False)),
            ('metadata', models.ForeignKey(orm[u'FaraData.metadata'], null=False))
        ))
        db.create_unique(m2m_table_name, ['payment_id', 'metadata_id'])


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
            'meta_data': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['FaraData.MetaData']", 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        u'FaraData.clientreg': {
            'Meta': {'object_name': 'ClientReg'},
            'client_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Client']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'meta_data': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['FaraData.MetaData']", 'null': 'True', 'blank': 'True'}),
            'primary_contractor_id': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'primary_contractor'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['FaraData.Registrant']"}),
            'reg_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Registrant']"})
        },
        u'FaraData.contact': {
            'Meta': {'object_name': 'Contact'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Client']", 'null': 'True'}),
            'contact_type': ('django.db.models.fields.CharField', [], {'default': "'U'", 'max_length': '1'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'lobbyist': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['FaraData.Lobbyist']", 'null': 'True', 'blank': 'True'}),
            'meta_data': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.MetaData']", 'null': 'True', 'blank': 'True'}),
            'recipient': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['FaraData.Recipient']", 'symmetrical': 'False'}),
            'registrant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Registrant']"})
        },
        u'FaraData.contribution': {
            'Meta': {'object_name': 'Contribution'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '8', 'decimal_places': '2'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'lobbyist': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Lobbyist']", 'null': 'True', 'blank': 'True'}),
            'meta_data': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.MetaData']", 'null': 'True', 'blank': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Recipient']"}),
            'registrant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Registrant']"})
        },
        u'FaraData.disbursement': {
            'Meta': {'object_name': 'Disbursement'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '2'}),
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Client']"}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'meta_data': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.MetaData']", 'null': 'True', 'blank': 'True'}),
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
            'link': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'meta_data': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.MetaData']", 'null': 'True', 'blank': 'True'}),
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
            'link': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True', 'db_index': 'True'}),
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
            'link': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'meta_data': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.MetaData']", 'null': 'True', 'blank': 'True'}),
            'purpose': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'registrant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['FaraData.Registrant']"}),
            'sort_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'subcontractor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'payment_subcontractor'", 'null': 'True', 'to': u"orm['FaraData.Registrant']"})
        },
        u'FaraData.recipient': {
            'Meta': {'object_name': 'Recipient'},
            'agency': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'bioguide_id': ('django.db.models.fields.CharField', [], {'max_length': '7', 'null': 'True', 'blank': 'True'}),
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
            'meta_data': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['FaraData.MetaData']", 'null': 'True', 'blank': 'True'}),
            'reg_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'reg_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'terminated_clients': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'terminated_clients'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['FaraData.Client']"}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['FaraData']