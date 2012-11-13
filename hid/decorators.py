import urlparse

from functools import wraps
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from hid.models import SitesUser


def site_required(view):
    @wraps(view)
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request, 'user'):
            protocol = "https" if request.is_secure() else "http"
            if request.session.get('has_assigned_site', False):
                return view(request, *args, **kwargs)
            
            user = User.objects.get(username=request.user)
            try:
                site = SitesUser.objects.filter(user=user) 
            except:
                return HttpResponse("You're assigned any site")
            else:
                if site.count() > 1:
                    request.session['has_assigned_site'] = False
                    return HttpResponseRedirect(
                        "%s://%s/mysite" % (protocol, request.get_host()))
                elif site.count():
                    s = site[0]
                    request.session['assigned_site'] = s.site.slug
                    request.session['has_assigned_site'] = True

        return view(request, *args, **kwargs)
    return _wrapped_view

