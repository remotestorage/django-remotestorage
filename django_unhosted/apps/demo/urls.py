#-*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django_unhosted.utils import autonamed_url

urlpatterns = patterns(
	'django_unhosted.apps.demo.views',
	autonamed_url(r'^/?$', 'storage_client'),
	autonamed_url(r'^receive_token(/|\.html)?$', 'storage_token'),
)
