#-*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django_remotestorage.utils import autonamed_url

host_meta_patterns = patterns(
	'django_remotestorage.apps.webfinger.views',
	autonamed_url(r'^.well-known/host-meta(/|\.xml)?$', 'host_meta'),
	autonamed_url(r'^.well-known/host-meta.json/?$', 'host_meta', kwargs=dict(fmt='json')) )

webfinger_patterns = patterns(
	'django_remotestorage.apps.webfinger.views',
	autonamed_url(r'^webfinger(/|\.xml)$', 'webfinger'),
	autonamed_url(r'^webfinger.json/?$', 'webfinger', kwargs=dict(fmt='json')),
	# For clean reverse-urls only
	autonamed_url(r'^webfinger$', 'webfinger', kwargs=dict(fmt='xml')),
	autonamed_url(r'^.well-known/host-meta$', 'host_meta', kwargs=dict(fmt='xml')) )

urlpatterns = patterns('',
	url('', include(host_meta_patterns)),
	url('', include(webfinger_patterns)) )
