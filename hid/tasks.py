# encoding=utf-8
# maintainer: katembu

import sys, os

from django.db import IntegrityError
from django.db.models import Q
from django.conf import settings
from bs4 import BeautifulSoup as Soup

from hid.models import Identifier, IssuedIdentifier, Site, IdentifierPrinted
from hid.utils import generateIdentifier, validateCheckDigit
from logger_ng.models import LoggedMessage

from celery import task
from celery.task.schedules import crontab
from celery.task import periodic_task

SUBMIT_TO_COMMCARE = True
COMMCARE_URL = "https://www.commcarehq.org/a/%s/receiver/"


@task()
def generate_id(size):
    for x in range(size):
        ident = generateIdentifier()
        try:
            m = Identifier(identifier=ident)
            m.save()
        except:
            pass


def upload_identifier(fn, site):
    results = load_healthids.apply_async((), {'filename': fn, 'site': site})
    return results


@task()
def load_healthids(filename, site):
    c = 0
    hid = False
    if filename:
        with open(filename) as f:
            for line in f:
                line = line.strip()
                if validateCheckDigit(line):
                    try:
                        hid = Identifier.objects.get_or_create(identifier=line)
                        c += 1
                    except IntegrityError:
                        pass

                    if hid:
                        hhid = Identifier.objects.get(identifier=line)
                        try:
                            IssuedIdentifier.objects.create(identifier=hhid,
                                                            site=site)
                        except IntegrityError:
                            pass

                else:
                    print line
    return c


@task()
def printhid(obj):
    current = 0
    requested_id = obj.total_requested
    site = Site.objects.get(slug=obj.site)
    z = IssuedIdentifier.objects.filter(site=site)
    _all = Identifier.objects.filter(~Q(identifier__in=[x.identifier for x in z]))[:requested_id]
    
    loc = str(settings.DOWNLOADS_URL+str(obj.pk)+'_identifier.txt')
    file_name = os.path.abspath(loc)
    f = open(file_name, 'w+')
    for j in _all:
        q = IdentifierPrinted()
        q.batch = obj
        q.identifier = j
        q.save()
        p = IssuedIdentifier()
        
        p.status = IssuedIdentifier.STATUS_PRINTED
        p.identifier = j
        p.site = site
        p.save()
        
        #write identifier
        k = str(j.identifier)+' \n'
        f.write(k)

        #Add total
        current += 1
        obj.task_progress = int(100.0*current/requested_id)
        obj.save()
    f.close()


@periodic_task(run_every=crontab(minute='*/2'))
def injectidentifier():
    cases = LoggedMessage.objects.filter(site__slug="test").exclude(
                        direction=LoggedMessage.DIRECTION_OUTGOING,
                        status=LoggedMessage.STATUS_SUCCESS
                        response_to__isnull=False)

    for z in cases:
        p = sanitise_case(z.site, z.text)
        if not p['status']:
            soup = Soup(z.text, 'xml')
            #GET HID
            k = IssuedIdentifier.objects.filter(site=z.site)
            _all = Identifier.objects.filter(~Q(identifier__in=[x.identifier for x in k]))[:1]
            hid = _all[0]
            if not p['household']:
                case_type = p['form_type']
                c = soup.find('health_id')
                c.contents[0].replaceWith(hid.identifier)print c
                y = "<%s> %s </%s>" % (case_type, soup, case_type)
                COMMCARE_URL = COMMCARE_URL % z.site
                print COMMCARE_URL
                print y
                form = {'data': y,
                        'SUBMIT_TO_COMMCARE': SUBMIT_TO_COMMCARE,
                        'COMMCARE_URL': COMMCARE_URL}
                if transmit_form(form):
                    s = LoggedMessage()
                    s.text = y
                    s.direction = s.DIRECTION_OUTGOING
                    s.response_to = z
                    s.site = z.site
                    s.save()

                    z.status = s.STATUS_SUCCESS
                    z.save()

                    p = IssuedIdentifier()
                    p.status = IssuedIdentifier.STATUS_ISSUED
                    p.identifier = hid
                    p.site = z.site
                    p.save()
