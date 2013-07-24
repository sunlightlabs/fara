# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Recipient'
        db.create_table(u'FaraData_recipient', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('crp_id', self.gf('django.db.models.fields.CharField')(max_length=9, null=True, blank=True)),
            ('agency', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('office_detail', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('state_local', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'FaraData', ['Recipient'])

        # Adding model 'Lobbyist'
        db.create_table(u'FaraData_lobbyist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('lobby_id', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('lobbyist_name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('PAC_name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
        ))
        db.send_create_signal(u'FaraData', ['Lobbyist'])

        # Adding model 'Location'
        db.create_table(u'FaraData_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('country_grouping', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('region', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal(u'FaraData', ['Location'])

        # Adding model 'Client'
        db.create_table(u'FaraData_client', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['FaraData.Location'])),
            ('client_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('address1', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('client_type', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
        ))
        db.send_create_signal(u'FaraData', ['Client'])

        # Adding model 'Registrant'
        db.create_table(u'FaraData_registrant', (
            ('reg_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('reg_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=200)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'FaraData', ['Registrant'])

        # Adding M2M table for field terminated_clients on 'Registrant'
        m2m_table_name = db.shorten_name(u'FaraData_registrant_terminated_clients')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('registrant', models.ForeignKey(orm[u'FaraData.registrant'], null=False)),
            ('client', models.ForeignKey(orm[u'FaraData.client'], null=False))
        ))
        db.create_unique(m2m_table_name, ['registrant_id', 'client_id'])

        # Adding M2M table for field clients on 'Registrant'
        m2m_table_name = db.shorten_name(u'FaraData_registrant_clients')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('registrant', models.ForeignKey(orm[u'FaraData.registrant'], null=False)),
            ('client', models.ForeignKey(orm[u'FaraData.client'], null=False))
        ))
        db.create_unique(m2m_table_name, ['registrant_id', 'client_id'])

        # Adding M2M table for field lobbyists on 'Registrant'
        m2m_table_name = db.shorten_name(u'FaraData_registrant_lobbyists')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('registrant', models.ForeignKey(orm[u'FaraData.registrant'], null=False)),
            ('lobbyist', models.ForeignKey(orm[u'FaraData.lobbyist'], null=False))
        ))
        db.create_unique(m2m_table_name, ['registrant_id', 'lobbyist_id'])

        # Adding model 'Gift'
        db.create_table(u'FaraData_gift', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('purpose', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('registrant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['FaraData.Registrant'])),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['FaraData.Recipient'], null=True, blank=True)),
        ))
        db.send_create_signal(u'FaraData', ['Gift'])

        # Adding M2M table for field client on 'Gift'
        m2m_table_name = db.shorten_name(u'FaraData_gift_client')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gift', models.ForeignKey(orm[u'FaraData.gift'], null=False)),
            ('client', models.ForeignKey(orm[u'FaraData.client'], null=False))
        ))
        db.create_unique(m2m_table_name, ['gift_id', 'client_id'])

        # Adding model 'Contact'
        db.create_table(u'FaraData_contact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['FaraData.Client'], null=True)),
            ('registrant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['FaraData.Registrant'])),
            ('contact_type', self.gf('django.db.models.fields.CharField')(default='U', max_length=1)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'FaraData', ['Contact'])

        # Adding M2M table for field recipient on 'Contact'
        m2m_table_name = db.shorten_name(u'FaraData_contact_recipient')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contact', models.ForeignKey(orm[u'FaraData.contact'], null=False)),
            ('recipient', models.ForeignKey(orm[u'FaraData.recipient'], null=False))
        ))
        db.create_unique(m2m_table_name, ['contact_id', 'recipient_id'])

        # Adding M2M table for field lobbyist on 'Contact'
        m2m_table_name = db.shorten_name(u'FaraData_contact_lobbyist')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('contact', models.ForeignKey(orm[u'FaraData.contact'], null=False)),
            ('lobbyist', models.ForeignKey(orm[u'FaraData.lobbyist'], null=False))
        ))
        db.create_unique(m2m_table_name, ['contact_id', 'lobbyist_id'])

        # Adding model 'Payment'
        db.create_table(u'FaraData_payment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['FaraData.Client'])),
            ('registrant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['FaraData.Registrant'])),
            ('fee', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=2)),
            ('purpose', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('subcontractor', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='payment_subcontractor', null=True, to=orm['FaraData.Registrant'])),
        ))
        db.send_create_signal(u'FaraData', ['Payment'])

        # Adding model 'Disbursement'
        db.create_table(u'FaraData_disbursement', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['FaraData.Client'])),
            ('registrant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['FaraData.Registrant'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=2)),
            ('purpose', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('subcontractor', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='subcontractor', null=True, to=orm['FaraData.Registrant'])),
        ))
        db.send_create_signal(u'FaraData', ['Disbursement'])

        # Adding model 'Contribution'
        db.create_table(u'FaraData_contribution', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2)),
            ('date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('registrant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['FaraData.Registrant'])),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['FaraData.Recipient'])),
            ('lobbyist', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['FaraData.Lobbyist'], null=True, blank=True)),
        ))
        db.send_create_signal(u'FaraData', ['Contribution'])

        # Adding model 'MetaData'
        db.create_table(u'FaraData_metadata', (
            ('link', self.gf('django.db.models.fields.CharField')(max_length=255, primary_key=True)),
            ('upload_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('reviewed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('processed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_amendment', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('form', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'FaraData', ['MetaData'])


    def backwards(self, orm):
        # Deleting model 'Recipient'
        db.delete_table(u'FaraData_recipient')

        # Deleting model 'Lobbyist'
        db.delete_table(u'FaraData_lobbyist')

        # Deleting model 'Location'
        db.delete_table(u'FaraData_location')

        # Deleting model 'Client'
        db.delete_table(u'FaraData_client')

        # Deleting model 'Registrant'
        db.delete_table(u'FaraData_registrant')

        # Removing M2M table for field terminated_clients on 'Registrant'
        db.delete_table(db.shorten_name(u'FaraData_registrant_terminated_clients'))

        # Removing M2M table for field clients on 'Registrant'
        db.delete_table(db.shorten_name(u'FaraData_registrant_clients'))

        # Removing M2M table for field lobbyists on 'Registrant'
        db.delete_table(db.shorten_name(u'FaraData_registrant_lobbyists'))

        # Deleting model 'Gift'
        db.delete_table(u'FaraData_gift')

        # Removing M2M table for field client on 'Gift'
        db.delete_table(db.shorten_name(u'FaraData_gift_client'))

        # Deleting model 'Contact'
        db.delete_table(u'FaraData_contact')

        # Removing M2M table for field recipient on 'Contact'
        db.delete_table(db.shorten_name(u'FaraData_contact_recipient'))

        # Removing M2M table for field lobbyist on 'Contact'
        db.delete_table(db.shorten_name(u'FaraData_contact_lobbyist'))

        # Deleting model 'Payment'
        db.delete_table(u'FaraData_payment')

        # Deleting model 'Disbursement'
        db.delete_table(u'FaraData_disbursement')

        # Deleting model 'Contribution'
        db.delete_table(u'FaraData_contribution')

        # Deleting model 'MetaData'
        db.delete_table(u'FaraData_metadata')


    models = {
        u'FaraData.client': {
            'Meta': {'object_name': 'Client'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'client_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'client_type': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
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
            'country_grouping': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
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
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'lobbyists': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['FaraData.Lobbyist']", 'null': 'True', 'blank': 'True'}),
            'reg_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'reg_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'terminated_clients': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'terminated_clients'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['FaraData.Client']"}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['FaraData']