# encoding=utf-8
# maintainer: katembu
import requests
import json

from requests.exceptions import ConnectionError
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponse, \
    HttpResponseRedirect
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.utils.translation import ugettext as _
from hid.barcode import b64_qrcode


from hid.models import Identifier, Site
from hid.forms import *


@login_required
def index(request):
    '''Landing page '''
    context = RequestContext(request)

    total = Identifier.objects.all().count()
    issued = Identifier.issuedIdentifiers().count()
    unused = Identifier.unusedIdentifiers().count()
    printed = total - issued - unused

    context.update({'total': total,
                    'issued': issued,
                    'printed': printed,
                    'unused': unused})

    context.home_reports = ""
    context.title = _(u"Identifier Dashboard")
    return render(request, "home.html", context_instance=context)


def login_greeter(request):

    from django.contrib.auth.views import login
    context = ''

    return login(request, template_name='login.html', extra_context=context)


@login_required
def request_identifier(request):
    context = RequestContext(request)
    form = IdentifierForm()
    if request.POST:
        form = IdentifierForm(request.POST)
        if form.is_valid():
            requested_id = form.cleaned_data['total_requsted']
            unused = Identifier.unusedIdentifiers().count()
            if requested_id > unused:
                context.error = _(u"Only %d Identifiers are available. \
                                    Please request less Identifiers") % unused
            rsite = form.cleaned_data['site']
            print rsite
            site = Site.objects.get(slug=rsite)
            c = IdentifierRequest()
            c.site = site
            c.total_requsted = requested_id
            c.save()

            if c:
                #context.error = _(u"Thank you")
                return HttpResponseRedirect("/print_batch/%s" % c.pk)

    context.form = form
    return render(request, "request-form.html", context_instance=context)


@login_required
def print_identifier(request, batchid):
    context = RequestContext(request)
    try:
        batch = IdentifierRequest.objects.get(pk=batchid)
        id_list = IdentifierPrinted.objects.filter(batch__pk=batch.pk)
    except IdentifierRequest.DoesNotExist:
        return HttpResponse(_(u"Batch not available"))

    all_ids = []

    for idgen in id_list:
        # this is a tuple of (ID, B64_QRPNG)
        all_ids.append((idgen.identifier.identifier,
                       b64_qrcode(idgen.identifier.identifier, scale=1.8)))

    context.update({'generated_ids': all_ids})

    context.title = _(u"Identifier Dashboard")
    return render(request, "printer.html", context_instance=context)


@login_required
def batch_list(request):
    context = RequestContext(request)
    batch_list = IdentifierRequest.objects.all()

    context.update({'batch_list': batch_list})

    return render(request, "report.html", context_instance=context)


@csrf_exempt
@require_POST
def getid(request, mvp_site):
    '''Get requests from Commcare check if they have HID and resubmit again '''
    try:
        batch = Site.objects.get(slug=mvp_site)
    except Site.DoesNotExist:
        return HttpResponse(_(u"Site %s is not configured") % mvp_site)
        
    data = request.raw_post_data
    print data
    ''' Check if HID field is not blank '''
