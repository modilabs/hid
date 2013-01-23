# encoding=utf-8
# maintainer: katembu

from hid.models import Identifier, IssuedIdentifier, Site
from hid.utils import generateIdentifier

from celery import task
from celery.task.schedules import crontab
from celery.task import periodic_task


@task
def generate_id(size):
    for x in range(size):
        ident = generateIdentifier()
        try:
            m = Identifier(identifier=ident)
            m.save()
        except:
            pass


'''
@periodic_task(run_every=crontab())
def add():
    print "Hurray"


This need to be changed to a task or service
z = Site.objects.all()[0]

for x in range(100000):
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
