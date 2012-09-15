#-*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django_remotestorage.utils import autonamed_url


urlpatterns_auth = [
	autonamed_url( r'^login/?$',
		'django_remotestorage.apps.account.views.login' ),
	autonamed_url( r'^logout/?$',
		'django_remotestorage.apps.account.views.logout' ) ]

urlpatterns_auth_management = [
	autonamed_url( r'^signup/?$',
		'django_remotestorage.apps.account.views.signup' ) ]

urlpatterns_client_management = [
	autonamed_url( r'^clients/?$',
		'django_remotestorage.apps.account.views.clients' ),
	autonamed_url( r'^client/(?P<client_id>\d+)/?$',
		'django_remotestorage.apps.account.views.client' ),

	url( r'^client/(?P<client_id>\d+)'
			r'/action/(?P<action>\w+)/?$',
		'django_remotestorage.apps.account.views.client_action',
		name='client_action' ),
	url( r'^client/(?P<client_id>\d+)/range/'
			r'(?P<cap>[^/]+)/action/(?P<action>\w+)/?$',
		'django_remotestorage.apps.account.views.client_action',
		name='client_cap_action' ) ]

urlpatterns = patterns( '',
	*( urlpatterns_auth
		+ urlpatterns_auth_management
		+ urlpatterns_client_management ) )
