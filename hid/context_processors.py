# encoding=utf-8
# maintainer: katembu


def manage_sites(request):
    has_assigned_site = request.session.get('has_assigned_site', False)
    site = request.session.get('assigned_site', False)
    return {'has_assigned_site': has_assigned_site, 'mysite': site}
