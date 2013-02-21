# encoding=utf-8
# maintainer: katembu
import requests
import json
import simplejson

from requests.exceptions import ConnectionError
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponse, \
    HttpResponseRedirect
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.db.models import Q

from django.template import Context
from django.template import loader

from hid.barcode import b64_qrcode

from hid.models import Identifier, Site, IssuedIdentifier
from hid.forms import *

from logger_ng.models import LoggedMessage
from hid.decorators import site_required
from django.contrib.auth.decorators import login_required

from hid.utils import *
from hid.tasks import printhid


@login_required
@site_required
def index(request):
    '''Landing page '''
    context = RequestContext(request)
    
    site=request.session.get('assigned_site')
    site = Site.objects.get(slug=site)
    total = IssuedIdentifier.objects.filter(site=site).count()

    context.update({'total': total,
                    'ishome': True,
                    'issued': '',
                    'printed': '',
                    'unused': ''})

    context.home_reports = ""
    context.title = _(u"Identifier Dashboard")
    return render(request, "home.html", context_instance=context)


def login_greeter(request):
    '''Load login page '''
    from django.contrib.auth.views import login
    context = ''
    request.session['has_assigned_site'] = False
    return login(request, template_name='login.html', extra_context=context)


@login_required
@site_required
def request_identifier(request):
    context = RequestContext(request)
    site=request.session.get('assigned_site')
    site = Site.objects.get(slug=site)
    form = IdentifierForm()
    if request.POST:
        form = IdentifierForm(request.POST)
        if form.is_valid():
            requested_id = form.cleaned_data['total_requested']
            z = IssuedIdentifier.objects.filter(site=site)
            unused = Identifier.objects.filter(~Q(identifier__in=[x.identifier for x in z])).count()
            if requested_id > unused:
                context.error = _(u"Only %d Identifiers are available. \
                                    Please request less Identifiers") % unused
            c = IdentifierRequest()
            c.site = site
            c.total_requested = requested_id
            c.save()
            printhid.apply_async((), {'obj': c})

            if c:
                return HttpResponseRedirect("/report")

    context.form = form
    return render(request, "request-form.html", context_instance=context)


@login_required
@site_required
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
@site_required
def batch_list(request):
    context = RequestContext(request)
    site = request.session.get('assigned_site')
    batch_list = IdentifierRequest.objects.filter(site__pk=site)

    context.update({'batch_list': batch_list})

    return render(request, "report.html", context_instance=context)


@login_required
def mysite(request):
    '''
    Select a site you want see statistics. This happens only if user is
    assigned more than one site
    '''
    context = RequestContext(request)
    try:
        sites = SitesUser.objects.filter(user=request.user)
    except SitesUser.DoesNotExist:
        return HttpResponse(_(u"Contact Administrator to assign you site"))

    if request.method == 'POST':
        site = request.POST['for_site']
        try:
            SitesUser.objects.get(user=request.user, site__pk=site)
            request.session['assigned_site'] = site
            request.session['has_assigned_site'] = True
        except SitesUser.DoesNotExist:
            return HttpResponse(_(u"Contact Administrator to assign you a site"))

        protocol = "https" if request.is_secure() else "http"
        return HttpResponseRedirect("%s://%s" % (protocol, request.get_host()))
    else:
        form = SiteChoice(request.user.username)
        context.update({'ishome': False,
                        'form': form,
                        'sites': sites})
    context.title = _(u"Please Select Site")
    return render(request, "home.html", context_instance=context)


@csrf_exempt
@require_POST
def getid(request, mvp_site):
    '''Get request from Commcare check if they have HID and resubmit again '''
    try:
        site = Site.objects.get(slug=mvp_site)
    except Site.DoesNotExist:
        return HttpResponse(_(u"Site %s is not configured") % mvp_site)

    data = request.raw_post_data
    s = LoggedMessage()
    s.text = data
    s.direction = s.DIRECTION_INCOMING
    s.site = site
    s.save()


@login_required
def ajax_progress(request):
    site = request.session.get('assigned_site')
    reps = IdentifierRequest.objects.filter(site__pk=site)
    rows = {}
    progresses = {}
    row_template = loader.get_template("status_row.html")
    for r in reps:
        c = Context({'rep': r})
        rows[r.pk] = row_template.render(c)
        if r.task_progress:
            progresses[r.pk] = r.task_progress

    return HttpResponse(simplejson.dumps([rows,progresses]), \
                                mimetype="application/json")    
