#-*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django_unhosted.utils import autonamed_url


urlpatterns = patterns(
	'django_unhosted.apps.webfinger.views',
	autonamed_url(r'^webfinger/?$', 'webfinger'),
	autonamed_url(r'^.well-known/host-meta/?$', 'host_meta')
)
