#-*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django_remotestorage.utils import autonamed_url

urlpatterns = patterns(
	'django_remotestorage.apps.demo.views',
	autonamed_url(r'^/?$', 'storage_client'),
	autonamed_url(r'^receive_token(/|\.html)?$', 'storage_token'),
)
