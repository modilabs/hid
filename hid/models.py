# encoding=utf-8
# maintainer: katembu

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _, ugettext
from django.db.models.signals import post_save, pre_save

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

    identifier = models.CharField(_(u"Identifier"), max_length=10, unique=True)
    generated_on = models.DateTimeField(_(u"Generated on"), auto_now_add=True)

    def __unicode__(self):
        return u"%s" % self.identifier

reversion.register(Identifier)


class IssuedIdentifier(models.Model):
    '''
    Childcount HealthIDS already generated
    This are all IDS issued to various MVP sites. The reason for this is
    to prevent double issuance of IDs for the same location
    '''
    class Meta:
        app_label = 'hid'
        verbose_name = _(u"CC+ HID Issued")
        verbose_name_plural = _(u"CC+ HID Issued to sites")
        unique_together = ('identifier', 'site')

    STATUS_GENERATED = 'G'
    STATUS_PRINTED = 'P'
    STATUS_ISSUED = 'I'
    STATUS_REVOKED = 'R'

    STATUS_CHOICES = (
        (STATUS_GENERATED, _(u"Generated")),
        (STATUS_PRINTED, _(u"Printed")),
        (STATUS_ISSUED, _(u"Issued")),
        (STATUS_REVOKED, _(u"Revoked")))

    identifier = models.ForeignKey(Identifier, max_length=10, unique=False)
    site = models.ForeignKey(Site, related_name="assigned_sites",
                             verbose_name=_(u"Assigned Site"))
    printed_on = models.DateTimeField(_(u"Printed on"), blank=True, null=True)
    issued_on = models.DateTimeField(_(u"Issued on"), blank=True, null=True)
    revoked_on = models.DateTimeField(_(u"Revoked on"), blank=True, null=True)
    status = models.CharField(_(u"Status"), choices=STATUS_CHOICES,
                              max_length=1, default=STATUS_GENERATED)

    def __unicode__(self):
        return u"%s " % self.identifier


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
    total_requested = models.IntegerField(max_length=11,
                                          verbose_name=_(u"Total Requested"))
    description = models.TextField(blank=True, null=True,
                                   verbose_name=_(u"description"))
    task_progress = models.PositiveSmallIntegerField(_("Progress"), blank=False,
                                null=False, unique=False, default=0)

    def __unicode__(self):
        return u'%s >> %s' % (self.site.name, self.total_requested)

reversion.register(IdentifierRequest)


class IdentifierPrinted(models.Model):

    class Meta:
        app_label = "hid"
        verbose_name = _(u"Identifier Batches")
        verbose_name_plural = _(u"Identifier Printed Batches")

    identifier = models.ForeignKey(Identifier)
    batch = models.ForeignKey(IdentifierRequest)

reversion.register(IdentifierPrinted)


class SitesUser(models.Model):
    class Meta:
        app_label = "hid"
        verbose_name = _(u"User Assigned Site")
        verbose_name_plural = _(u"User Assigned Sites")
        unique_together = ('site', 'user')

    site = models.ForeignKey(Site, verbose_name=_(u"Assigned Site"))
    user = models.ForeignKey(User, verbose_name=_(u"User"))

    def __unicode__(self):
        return u'%s >> %s' % (self.user.username, self.site.name)


class Cases(models.Model):
    class Meta:
        app_label = "hid"
        verbose_name = _(u"Case")
        verbose_name_plural = _(u"Cases")
        unique_together = ('site', 'case')

    TYPE_HOUSEHOLD = 'H'
    TYPE_CHILD = 'C'
    TYPE_PREGNANCY = 'P'
    TYPE_OTHER = 'O'

    TYPE_CHOICES = (
        (TYPE_HOUSEHOLD, _(u"Household")),
        (TYPE_CHILD, _(u"Child")),
        (TYPE_OTHER, _(u"Other")),
        (TYPE_PREGNANCY, _(u"Pregnancy")))

    case = models.CharField(max_length=200, verbose_name=_(u"Case ID"))
    issued_id = models.ForeignKey(IssuedIdentifier, max_length=10, blank=True, null=True, unique=False)
    case_type = models.CharField(_(u"Case Type"), choices=TYPE_CHOICES,
                              max_length=1, blank=True, null=True)
    text = models.TextField(_(u"More Information"), blank=True, null=True)
