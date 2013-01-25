# encoding=utf-8
# maintainer: katembu

from django.db import IntegrityError

from hid.models import Identifier, IssuedIdentifier, Site
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
