#-*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django_remotestorage.utils import autonamed_url


urlpatterns = patterns(
	'django_remotestorage.apps.api.views',
	autonamed_url(r'^storage/(?P<acct>[^/]+)/?(?P<path>.*)$', 'storage'),
)
