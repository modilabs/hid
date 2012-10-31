# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LoggedMessage'
        db.create_table('logger_ng_loggedmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('direction', self.gf('django.db.models.fields.CharField')(default='O', max_length=1)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hid.Site'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
            ('response_to', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='response', null=True, to=orm['logger_ng.LoggedMessage'])),
        ))
        db.send_create_signal('logger_ng', ['LoggedMessage'])


    def backwards(self, orm):
        # Deleting model 'LoggedMessage'
        db.delete_table('logger_ng_loggedmessage')


    models = {
        'hid.site': {
            'Meta': {'object_name': 'Site'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '30', 'primary_key': 'True'})
        },
        'logger_ng.loggedmessage': {
            'Meta': {'ordering': "['-date', 'direction']", 'object_name': 'LoggedMessage'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'direction': ('django.db.models.fields.CharField', [], {'default': "'O'", 'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'response_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'response'", 'null': 'True', 'to': "orm['logger_ng.LoggedMessage']"}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hid.Site']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['logger_ng']