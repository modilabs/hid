# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Site'
        db.create_table('hid_site', (
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=30, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('hid', ['Site'])

        # Adding model 'Identifier'
        db.create_table('hid_identifier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('identifier', self.gf('django.db.models.fields.CharField')(unique=True, max_length=10)),
            ('generated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('hid', ['Identifier'])

        # Adding model 'IssuedIdentifier'
        db.create_table('hid_issuedidentifier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('identifier', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hid.Identifier'], max_length=10)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(related_name='assigned_sites', to=orm['hid.Site'])),
            ('printed_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('issued_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('revoked_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='G', max_length=1)),
        ))
        db.send_create_signal('hid', ['IssuedIdentifier'])

        # Adding model 'IdentifierRequest'
        db.create_table('hid_identifierrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hid.Site'])),
            ('total_requested', self.gf('django.db.models.fields.IntegerField')(max_length=11)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('hid', ['IdentifierRequest'])

        # Adding model 'IdentifierPrinted'
        db.create_table('hid_identifierprinted', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('identifier', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hid.Identifier'])),
            ('batch', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hid.IdentifierRequest'])),
        ))
        db.send_create_signal('hid', ['IdentifierPrinted'])

        # Adding model 'SitesUser'
        db.create_table('hid_sitesuser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hid.Site'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('hid', ['SitesUser'])

        # Adding unique constraint on 'SitesUser', fields ['site', 'user']
        db.create_unique('hid_sitesuser', ['site_id', 'user_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'SitesUser', fields ['site', 'user']
        db.delete_unique('hid_sitesuser', ['site_id', 'user_id'])

        # Deleting model 'Site'
        db.delete_table('hid_site')

        # Deleting model 'Identifier'
        db.delete_table('hid_identifier')

        # Deleting model 'IssuedIdentifier'
        db.delete_table('hid_issuedidentifier')

        # Deleting model 'IdentifierRequest'
        db.delete_table('hid_identifierrequest')

        # Deleting model 'IdentifierPrinted'
        db.delete_table('hid_identifierprinted')

        # Deleting model 'SitesUser'
        db.delete_table('hid_sitesuser')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'hid.identifier': {
            'Meta': {'object_name': 'Identifier'},
            'generated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'})
        },
        'hid.identifierprinted': {
            'Meta': {'object_name': 'IdentifierPrinted'},
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hid.IdentifierRequest']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hid.Identifier']"})
        },
        'hid.identifierrequest': {
            'Meta': {'ordering': "['-pk']", 'object_name': 'IdentifierRequest'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hid.Site']"}),
            'total_requested': ('django.db.models.fields.IntegerField', [], {'max_length': '11'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'hid.issuedidentifier': {
            'Meta': {'object_name': 'IssuedIdentifier'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hid.Identifier']", 'max_length': '10'}),
            'issued_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'printed_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'revoked_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assigned_sites'", 'to': "orm['hid.Site']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'G'", 'max_length': '1'})
        },
        'hid.site': {
            'Meta': {'object_name': 'Site'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '30', 'primary_key': 'True'})
        },
        'hid.sitesuser': {
            'Meta': {'unique_together': "(('site', 'user'),)", 'object_name': 'SitesUser'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hid.Site']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['hid']