# encoding=utf-8
# maintainer: katembu

import os
from django.conf import settings

from django.conf.urls import patterns, include, url
from django.contrib import admin
import hid.views as views
import logger_ng.views as view

from hid import uploadidentifier


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.index, name='dashboard'),
    url(r'^home/?$', views.index),

    url(r'^incoming/?$', view.index, name='loggerng-index'),
    
    url(r'^login/$', 'hid.views.login_greeter', name='login'),
    url(r'^mysite/$', 'hid.views.mysite', name='selectsite'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'template_name': 'logout.html', 'next_page': '/'}, name='logout'),

    url(r'^request-id/?$', 'hid.views.request_identifier',
        name='request-id'),
    url(r'^report/?$', 'hid.views.batch_list',
        name='report'),
    url(r'^upload',
        uploadidentifier.upload_file, name='upload-ids'),
        
    url(r'^getid/(?P<mvp_site>[^/]+)/$', 'hid.views.getid'),
    url(r'^print_batch/(?P<batchid>[^/]+)$',
        'hid.views.print_identifier', name='printbatch'),
        
    (r'^hid/ajax_progress/$', views.ajax_progress),
    
    url(r'^download/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': '%s' % os.path.abspath(settings.DOWNLOADS_URL),
                'show_indexes': False}),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
