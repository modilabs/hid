# encoding=utf-8
# maintainer: katembu

from django.contrib import admin
from django.contrib.auth.models import User

from hid.models import Site, Identifier, IdentifierRequest, SitesUser, \
    IssuedIdentifier, Cases


def site(obj):
    return obj.site.name.upper()


class IssuedIdentifierAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'status', site)
    list_filter = ['site']
    search_fields = ['identifier']


admin.site.register(IssuedIdentifier, IssuedIdentifierAdmin)
admin.site.register(Site)
admin.site.register(Cases)
admin.site.register(Identifier)
admin.site.register(IdentifierRequest)
admin.site.register(SitesUser)
