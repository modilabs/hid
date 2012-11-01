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
        return self.slug


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
    status = models.CharField(_(u"Status"), choices=STATUS_CHOICES,
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


class IdentifierRequest(models.Model):

    class Meta:
        app_label = "hid"
        verbose_name = _(u"Identifier Request")
        verbose_name_plural = _(u"Identifier Request")
        ordering = ['-pk']

    created_on = models.DateTimeField(_(u"Created on"), auto_now_add=True,
                                      db_index=True)
    updated_on = models.DateTimeField(auto_now=True)
    site = models.ForeignKey(Site)
    total_requsted = models.IntegerField(max_length=11,
                                         verbose_name=_(u"Total Requested"))
    description = models.TextField(blank=True, null=True,
                                   verbose_name=_(u"description"))

    def __unicode__(self):
        return u'%s >> %s' % (self.site.name, self.total_requsted)

    def used(self):
        return self.identifierprinted_set.filter(identifier__status=Identifier.STATUS_ISSUED)

reversion.register(IdentifierRequest)


class IdentifierPrinted(models.Model):

    class Meta:
        app_label = "hid"
        verbose_name = _(u"Identifier Batches")
        verbose_name_plural = _(u"Identifier Printed Batches")

    identifier = models.ForeignKey(Identifier)
    batch = models.ForeignKey(IdentifierRequest)

reversion.register(IdentifierPrinted)


def print_identifiers(sender, **kwargs):
    obj = kwargs['instance']
    requested_id = obj.total_requsted
    _all = Identifier.unusedIdentifiers()[:requested_id]
    for j in _all:
        j.status = Identifier.STATUS_PRINTED
        j.save()
        q = IdentifierPrinted()
        q.batch = obj
        q.identifier = j
        q.save()

post_save.connect(print_identifiers, sender=IdentifierRequest)
