# encoding=utf-8
# maintainer: katembu

import sys, os

from django.db import IntegrityError
from django.conf import settings
from bs4 import BeautifulSoup as Soup

from hid.utils import *
from logger_ng.models import LoggedMessage

from celery import task
from celery.task.schedules import crontab
from celery.task import periodic_task

SUBMIT_TO_COMMCARE = True
COMMCARE_LINK = "https://www.commcarehq.org/a/%s/receiver/"


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
    _all = Identifier.objects.exclude(pk__in=z.values('identifier_id'))
    loc = str(settings.DOWNLOADS_URL + str(obj.pk) + '_identifier.txt')
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
        k = str(j.identifier) + ' \n'
        f.write(k)

        #Add total
        current += 1
        obj.task_progress = int(100.0 * current / requested_id)
        obj.save()
    f.close()


@task()
def advanced_injector(obj):
    try:
        z = LoggedMessage.objects.get(pk=obj.pk)
    except LoggedMessage.DoesNotExist:
        z = False

    if z:
        pstatus = get_caseid(z.text)
        if pstatus:
            site = z.site
            try:
                Cases.objects.get(case=pstatus, site__pk=site)
                m = True
            except Cases.DoesNotExist:
                m = False

            if not m:
                c = Cases.objects.create(case=pstatus, site=site)
                c.save()
                p = sanitise_case(z.site, z.text)
                if not p['status']:
                    soup = Soup(z.text, 'xml')
                    #GET HID
                    k = IssuedIdentifier.objects.filter(site=z.site)
                    _all = Identifier.objects.exclude(pk__in=k.values('identifier_id'))
                    hid = _all[0]
                    print p
                    case_ = "household_head_health_id" if p['household'] else "health_id"
                    case_type = p['form_type']
                    c = soup.find(case_)
                    mm = "<%s>%s</%s>" % (case_, hid.identifier, case_)
                    c = str(c)
                    soup = str(soup)
                    soup = soup.replace(c, mm)

                    soup = soup.replace("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n", "")
                    y = "<%s> %s </%s>" % (case_type, soup, case_type)

                    COMMCARE_URL = COMMCARE_LINK % z.site
                    print "HID: %s \n" % hid.identifier
                    print "COMMCARE_URL: %s \n" % COMMCARE_URL
                    print y
                    print "============================================================"
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
                    else:
                        s = LoggedMessage()
                        s.text = y
                        s.direction = s.DIRECTION_OUTGOING
                        s.response_to = z
                        s.site = z.site
                        s.save()

                        z.status = s.STATUS_ERROR
                        z.save()
                        return "HURRAY WRONG "
                else:
                    return "Wrong xml "
            else:
                return "Already Case exist"
        else:
            return "Wrong xml. No case ID"


@task()
def injectid(obj):
    z = LoggedMessage.objects.get(pk=obj.pk)

    p = sanitise_case(z.site, z.text)
    if not p['status']:
        soup = Soup(z.text, 'xml')
        #GET HID
        k = IssuedIdentifier.objects.filter(site=z.site)
        _all = Identifier.objects.exclude(pk__in=k.values('identifier_id'))
        hid = _all[0]
        print p
        case_ = "household_head_health_id" if p['household'] else "health_id"
        case_type = p['form_type']
        c = soup.find(case_)
        mm = "<%s>%s</%s>" % (case_, hid.identifier, case_)
        c = str(c)
        soup = str(soup)
        soup = soup.replace(c, mm)

        soup = soup.replace("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n", "")
        y = "<%s> %s </%s>" % (case_type, soup, case_type)

        COMMCARE_URL = COMMCARE_LINK % z.site
        print "HID: %s \n" % hid.identifier
        print "COMMCARE_URL: %s \n" % COMMCARE_URL
        print y
        print "=========================================================="
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
        else:
            s = LoggedMessage()
            s.text = y
            s.direction = s.DIRECTION_OUTGOING
            s.response_to = z
            s.site = z.site
            s.save()

            z.status = s.STATUS_ERROR
            z.save()


#@periodic_task(run_every=crontab(minute="*/30"))
def injectid_crontab():
    site = 'mvp-mwandama'
    msm = LoggedMessage.objects.filter(site__pk=site, status__isnull=True, )
    msgs = msm.exclude(direction=LoggedMessage.DIRECTION_OUTGOING,
                       response_to__isnull=False)

    for z in msgs:
        pstatus = get_caseid(z.text)
        if pstatus:
            site = z.site
            try:
                Cases.objects.get(case=pstatus, site__pk=site)
                m = True
            except Cases.DoesNotExist:
                m = False

            if not m:
                c = Cases.objects.create(case=pstatus, site=site)
                c.save()
                p = sanitise_case(z.site, z.text)
                if not p['status']:
                    soup = Soup(z.text, 'xml')
                    #GET HID
                    k = IssuedIdentifier.objects.filter(site=z.site)
                    _all = Identifier.objects.exclude(pk__in=k.values('identifier_id'))
                    hid = _all[0]
                    print p
                    case_ = "household_head_health_id" if p['household'] else "health_id"
                    case_type = p['form_type']
                    c = soup.find(case_)
                    mm = "<%s>%s</%s>" % (case_, hid.identifier, case_)
                    c = str(c)
                    soup = str(soup)
                    soup = soup.replace(c, mm)

                    soup = soup.replace("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n", "")
                    y = "<%s> %s </%s>" % (case_type, soup, case_type)

                    COMMCARE_URL = COMMCARE_LINK % z.site
                    print "HID: %s \n" % hid.identifier
                    print "COMMCARE_URL: %s \n" % COMMCARE_URL
                    print y
                    print "============================================================"
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
                    else:
                        s = LoggedMessage()
                        s.text = y
                        s.direction = s.DIRECTION_OUTGOING
                        s.response_to = z
                        s.site = z.site
                        s.save()

                        z.status = s.STATUS_ERROR
                        z.save()
                else:
                    return "Wrong xml "
            else:
                return "Already Case exist"
        else:
            return "Wrong xml. No case ID"
