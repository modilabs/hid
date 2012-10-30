# encoding=utf-8
# maintainer: katembu

from hid.models import Identifier
from hid.utils import generateIdentifier

'''This need to be changed to a task or service'''
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
