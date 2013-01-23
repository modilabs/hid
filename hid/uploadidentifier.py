# encoding=utf-8
# maintainer: katembu

import os


from django.shortcuts import render, get_object_or_404

from django.template import Template, Context, loader
from django.contrib.auth.decorators import login_required, permission_required
from django import forms
from django.db import IntegrityError

from hid.models import IdentifierRequest, Identifier, IssuedIdentifier

class UploadHealthIDFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file  = forms.FileField()


@login_required
def upload_file(request):
    ctx = {}
    if request.method == 'POST':
        form = UploadHealthIDFileForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            fn = title.strip().replace(' ', '_') + '.txt'
            fn = handle_uploaded_file(request.FILES['file'], fn)
            message = u"Succesfully uploaded health id file."
            c = load_healthids(fn)
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

def load_healthids(filename):
    c = 0
    if filename:
        with open(filename) as f:
            for line in f:
                line = line.strip()
                print line
                '''
                try:
                    hid = HealthId.objects.create(
                        health_id = line,
                        status = HealthId.STATUS_GENERATED)
                    c += 1
                except IntegrityError:
                    pass

                if hid:
                    try:
                        CHWHealthId.objects.create(health_id=hid)
                    except:
                        pass
                '''
    return c
