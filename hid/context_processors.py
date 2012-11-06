# encoding=utf-8
# maintainer: katembu


def manage_sites(request):
    try:
        has_assigned_site = request.session['has_assigned_site']
        site = request.session['assigned_site']
    except:
        request.session['has_assigned_site'] = False
        site = False
        
    return {'has_assigned_site': has_assigned_site, 'mysite': site}
