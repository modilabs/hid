#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
# maintainer: katembu

'''
Defines the LoggedMessage model and two custom managers, (OutgoingManager and
IncomingManager
'''

from django.db import models
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.db.models.signals import post_save, pre_save
from hid.models import Site
from hid.utils import get_caseid


class OutgoingManager(models.Manager):
    '''
    A custom manager for LoggedMessage that limits query sets to
    outgoing messages only.
    '''

    def get_query_set(self):
        return super(OugoingManager, self).get_query_set()\
            .filter(direction=LoggedMessage.DIRECTION_OUTGOING)


class IncomingManager(models.Manager):
    '''
    A custom manager for LoggedMessage that limits query sets to
    incoming messages only.
    '''

    def get_query_set(self):
        return super(IncomingManager, self).get_query_set() \
            .filter(direction=LoggedMessage.DIRECTION_INCOMING)


class LoggedMessage(models.Model):
    '''
    LoggedMessage model with the following fields:
        date        - date of the message
        direction   - DIRECTION_INCOMING or DIRECTION_OUTGOING
        text        - text of the message
        site        - MVP Site
        status      - stores message status, (success, error, parse_error, etc)
        response_to - recursive foreignkey to self. Only used for outgoing
                      messages. Points to the LoggedMessage to which the
                      outgoing message is a response.

    Besides the default manager (objects) this model has to custom managers
    for your convenience:
        LoggedMessage.incoming.all()
        LoggedMessage.outgoing.all()
    '''

    class Meta:
        '''
        Django Meta class to set the translatable verbose_names and to create
        permissions. The can_view permission is used by rapidsms to determine
        whether a user can see the tab. can_respond determines if a user
        can respond to a message from the log view.
        '''
        verbose_name = _(u"logged message")
        verbose_name = _(u"logged messages")
        ordering = ['-date', 'direction']
        permissions = (
            ("can_view", _(u"Can view")),
            ("can_respond", _(u"Can respond")),
        )

    DIRECTION_INCOMING = 'I'
    DIRECTION_OUTGOING = 'O'

    DIRECTION_CHOICES = (
        (DIRECTION_INCOMING, _(u"Incoming")),
        (DIRECTION_OUTGOING, _(u"Outgoing")))

    #STATUS types:
    STATUS_SUCCESS = 'success'
    STATUS_ERROR = 'error'
    STATUS_INFO = 'info'
    STATUS_SYSTEM_ERROR = 'system_error'

    STATUS_CHOICES = (
        (STATUS_SUCCESS, _(u"Success")),
        (STATUS_ERROR, _(u"Error")),
        (STATUS_INFO, _(u"Info")),
        (STATUS_SYSTEM_ERROR, _(u"System error")))

    date = models.DateTimeField(_(u"date"), auto_now_add=True)
    direction = models.CharField(_(u"type"), max_length=1,
                                 choices=DIRECTION_CHOICES,
                                 default=DIRECTION_OUTGOING)
    text = models.TextField(_(u"text"))
    site = models.ForeignKey(Site)
    status = models.CharField(_(u"status"), max_length=32,
                              choices=STATUS_CHOICES, blank=True, null=True)
    response_to = models.ForeignKey('self', verbose_name=_(u"response to"),
                                    related_name='response', blank=True,
                                    null=True)

    #Setup a default manager
    objects = models.Manager()

    # Setup custom managers.  These allow you to do:
    #    LoggedMessage.incoming.all()
    # or
    #    LoggedMessage.outgoing.all()
    incoming = IncomingManager()
    outgoing = OutgoingManager()

    def is_incoming(self):
        '''
        Returns true if this is the log of an incoming message, else false
        '''
        return self.direction == self.DIRECTION_INCOMING

    def to_dict(self):
        '''
        returns dict version of the message and all its responses
        '''
        return {'id': self.id, 'message': self.text,
                'status': self.status,
                'dateStr': self.date.strftime("%d-%b-%Y @ %H:%M:%S"),
                'name': self.site.name,
                'responses': [r.text for r in self.response.all()]}

    def to_json(self):
        return simplejson.dumps(self.to_dict())

    def __unicode__(self):
        return  u"%(direction)s - %(site)s - %(text)s" % \
                {'direction': self.get_direction_display(),
                 'site': self.site.name,
                 'text': self.text}


from hid.tasks import advanced_injector
def apply_hid(sender, **kwargs):
    # the object which is saved can be accessed via kwargs 'instance' key.
    obj = kwargs['instance']
    print obj.direction
    if obj.direction == LoggedMessage.DIRECTION_INCOMING:
        advanced_injector.apply_async((), {'obj': obj})


def validate(sender, **kwargs):
    # the object which is saved can be accessed via kwargs 'instance' key.
    obj = kwargs['instance']
    status = get_caseid(obj.text)
    site = obj.site
    print status
    if status:
        try:
            Cases.objects.get(case=status, site__pk=site)
            m = True
        except Cases.DoesNotExist:
            m = False

        if not m:
            obj.save()
        else:
            pass
    else:
        pass

# here we connect a post_save signal for MyModel
# in other terms whenever an instance of MyModel is saved
# the 'do_something' function will be called.
#pre_save.connect(validate, sender=LoggedMessage)
post_save.connect(apply_hid, sender=LoggedMessage)
