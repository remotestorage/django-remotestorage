#-*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django_unhosted.utils import autonamed_url


urlpatterns = patterns(
	'django_unhosted.apps.account.views',

	autonamed_url(r'^login/?$', 'login'),
	autonamed_url(r'^logout/?$', 'logout'),
	autonamed_url(r'^signup/?$', 'signup'),

	autonamed_url(r'^clients/?$', 'clients'),
	autonamed_url(r'^client/(?P<client_id>\d+)/?$', 'client'),

	url( r'^client/(?P<client_id>\d+)'
			r'/action/(?P<action>\w+)/?$',
		'client_action', name='client_action' ),
	url( r'^client/(?P<client_id>\d+)/range/'
			r'(?P<cap>[^/]+)/action/(?P<action>\w+)/?$',
		'client_action', name='client_cap_action' ),

)
