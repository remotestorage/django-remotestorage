#-*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django_unhosted.utils import autonamed_url


urlpatterns = patterns(
	'django_unhosted.apps.api.views',
	autonamed_url(r'^storage/(?P<acct>[^/]+)/?$', 'storage'),
)
