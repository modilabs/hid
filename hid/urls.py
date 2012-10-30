# encoding=utf-8
# maintainer: katembu

from django.conf.urls import patterns, include, url
from django.contrib import admin
from hid import views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='dashboard'),

    url(r'^login/$', 'hid.views.login_greeter', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'template_name': 'logout.html', 'next_page': '/'}, name='logout'),

    url(r'^request-id/?$', 'hid.views.request_identifier',
        name='request-id'),
    url(r'^report/?$', 'hid.views.batch_list',
        name='report'),
    url(r'^print_batch/(?P<batchid>[^/]+)$',
        'hid.views.print_identifier', name='printbatch'),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
