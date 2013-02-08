# encoding=utf-8
# maintainer: katembu

import sys, os

from django.db import IntegrityError
from django.db.models import Q
from django.conf import settings

from hid.models import Identifier, IssuedIdentifier, Site, IdentifierPrinted
from hid.utils import generateIdentifier, validateCheckDigit

from celery import task
from celery.task.schedules import crontab
from celery.task import periodic_task


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


'''
@periodic_task(run_every=crontab())
def add():
    print "Hurray"

for x in range(1000000):
    ident = generateIdentifier()
    print ident
    print x
    print "+++++++============================++++++++++++++"
    try:
        m = Identifier(identifier=ident)
        m.save()
    except:
        pass
'''
