# encoding=utf-8
# maintainer: katembu

import os


from django.shortcuts import render, get_object_or_404

from django.template import Template, Context, loader
from django.contrib.auth.decorators import login_required, permission_required
from django import forms
from django.db import IntegrityError

from hid.decorators import site_required
from hid.models import Site, Identifier, IssuedIdentifier


class UploadHealthIDFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()

@site_required
@login_required
def upload_file(request):
    site = request.session.get('assigned_site')
    site = Site.objects.get(slug=site)
    ctx = {}
    if request.method == 'POST':
        form = UploadHealthIDFileForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            fn = title.strip().replace(' ', '_') + '.txt'
            fn = handle_uploaded_file(request.FILES['file'], fn)
            message = u"Succesfully uploaded health id file."
            c = load_healthids(fn, site)
            message += " %(count)s health ids added." % {'count': c}
            ctx = {'message': message}
        else:
            ctx = {'message': u"Invalid form Input", 'form': form}
    else:
        form = UploadHealthIDFileForm()
        ctx = {'form': form}
    return render(request, 'upload.html', ctx)


def handle_uploaded_file(f, filename):
    fn = os.path.join(os.path.dirname(__file__), 'static', filename)
    destination = open(fn, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return fn


def load_healthids(filename, site):
    c = 0
    hid = False
    if filename:
        with open(filename) as f:
            for line in f:
                line = line.strip()
                try:
                    hid = Identifier.objects.get_or_create(identifier=line)
                    c += 1
                except IntegrityError:
                    print line
                    pass

                if hid:
                    hhid = Identifier.objects.get(identifier=line)
                    try:
                        IssuedIdentifier.objects.create(identifier=hhid,
                                                        site=site)
                    except IntegrityError:
                        print "error"
                        pass
    return c
