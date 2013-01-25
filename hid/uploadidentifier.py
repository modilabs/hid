# encoding=utf-8
# maintainer: katembu

import os


from django.shortcuts import render, get_object_or_404

from django.template import Template, Context, loader
from django.contrib.auth.decorators import login_required, permission_required
from django import forms

from hid.decorators import site_required
from hid.models import Site, Identifier, IssuedIdentifier
from hid.tasks import upload_identifier


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
            c = upload_identifier(fn, site)
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
