# encoding=utf-8
# maintainer: katembu

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _, ugettext
from django.db.models.signals import post_save, pre_save
from hid.utils import *

import reversion


class Site(models.Model):

	class Meta:
		app_label = "hid"
        verbose_name = _(u"MVP Site")
        verbose_name_plural = _(u"MVP Sites")

	slug = models.SlugField(max_length=30, primary_key=True)
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True, null=True,
                                   verbose_name=_(u"description"),
                                   help_text=_(u"Site"))

	def __unicode__(self):
		return self.name


class Identifier(models.Model):

    class Meta:
        app_label = 'hid'
        verbose_name = _(u"Identifier")
        verbose_name_plural = _(u"Identifiers")

    STATUS_GENERATED = 'G'
    STATUS_PRINTED = 'P'
    STATUS_ISSUED = 'I'
    STATUS_REVOKED = 'R'

    STATUS_CHOICES = (
        (STATUS_GENERATED, _(u"Generated")),
        (STATUS_PRINTED, _(u"Printed")),
        (STATUS_ISSUED, _(u"Issued")),
        (STATUS_REVOKED, _(u"Revoked")))

    identifier = models.CharField(_(u"Identifier"), max_length=10, unique=True)
    generated_on = models.DateTimeField(_(u"Generated on"), auto_now_add=True)
    printed_on = models.DateTimeField(_(u"Printed on"), blank=True, null=True)
    issued_on = models.DateTimeField(_(u"Issued on"), blank=True, null=True)
    revoked_on = models.DateTimeField(_(u"Revoked on"), blank=True, null=True)
    status = models.CharField(_(u"Status"), choices=STATUS_CHOICES, \
                              max_length=1, default=STATUS_GENERATED)

    def __unicode__(self):
        return u"%s" % self.identifier

    
    @classmethod
    def unusedIdentifiers(cls):
        return cls.objects.filter(status=cls.STATUS_GENERATED)

    
    @classmethod
    def issuedIdentifiers(cls):
        return cls.objects.filter(status=cls.STATUS_ISSUED)

reversion.register(Identifier)
