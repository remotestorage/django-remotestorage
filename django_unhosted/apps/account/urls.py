#-*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django_unhosted.utils import autonamed_url


urlpatterns = patterns(
	'django_unhosted.apps.account.views',
	autonamed_url(r'^login/?$', 'login'),
	autonamed_url(r'^logout/?$', 'logout'),
	autonamed_url(r'^signup/?$', 'signup'),
	autonamed_url(r'^clients/?$', 'clients'),
)
