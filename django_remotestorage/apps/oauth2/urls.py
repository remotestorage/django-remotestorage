#-*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django_remotestorage.utils import autonamed_url


urlpatterns = patterns( '',
	autonamed_url( r'^missing_redirect_uri/?$',
		'django_remotestorage.apps.oauth2.views.missing_redirect_uri' ),
	autonamed_url( r'^authorize/?$',
		'django_remotestorage.apps.oauth2.views.authorize' ),
	url(r'^token/?$', 'oauth2app.token.handler', name='token_handler') )
