# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'IdentifierRequest'
        db.create_table('hid_identifierrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('updated_on', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hid.Site'])),
            ('total_requsted', self.gf('django.db.models.fields.IntegerField')(max_length=11)),
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


    def backwards(self, orm):
        # Deleting model 'IdentifierRequest'
        db.delete_table('hid_identifierrequest')

        # Deleting model 'IdentifierPrinted'
        db.delete_table('hid_identifierprinted')


    models = {
        'hid.identifier': {
            'Meta': {'object_name': 'Identifier'},
            'generated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'issued_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'printed_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'revoked_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'G'", 'max_length': '1'})
        },
        'hid.identifierprinted': {
            'Meta': {'object_name': 'IdentifierPrinted'},
            'batch': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hid.IdentifierRequest']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hid.Identifier']"})
        },
        'hid.identifierrequest': {
            'Meta': {'object_name': 'IdentifierRequest'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hid.Site']"}),
            'total_requsted': ('django.db.models.fields.IntegerField', [], {'max_length': '11'}),
            'updated_on': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'hid.site': {
            'Meta': {'object_name': 'Site'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '30', 'primary_key': 'True'})
        }
    }

    complete_apps = ['hid']