# encoding=utf-8
# maintainer: katembu

from django.contrib import admin
from django.contrib.auth.models import User

from hid.models import Site, Identifier

admin.site.register(Site)
admin.site.register(Identifier)
