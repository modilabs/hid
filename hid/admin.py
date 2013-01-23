# encoding=utf-8
# maintainer: katembu

from django.contrib import admin
from django.contrib.auth.models import User

from hid.models import Site, Identifier, IdentifierRequest, SitesUser, \
    IssuedIdentifier

admin.site.register(Site)
admin.site.register(IssuedIdentifier)
admin.site.register(Identifier)
admin.site.register(IdentifierRequest)
admin.site.register(SitesUser)
