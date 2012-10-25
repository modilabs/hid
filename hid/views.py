# encoding=utf-8
# maintainer: katembu
import requests
import json

from requests.exceptions import ConnectionError
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponse, \
    HttpResponseRedirect
from django.views.decorators.http import require_GET, require_POST
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.utils.translation import ugettext as _


@login_required
def index(request):
    '''Landing page '''
    context = RequestContext(request)
    context.home_reports = ""
    context.title = _(u"Report Dashboard")
    return render(request, "home.html", context_instance=context)
    

def login_greeter(request):

    from django.contrib.auth.views import login
    context = ''
    
    return login(request, template_name='login.html', extra_context=context)
