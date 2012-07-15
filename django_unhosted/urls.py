#-*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include

from .utils import autons_include


urlpatterns = patterns( '',
	url(r'', autons_include('django_unhosted.apps.webfinger.urls')),

	url(r'^account/', autons_include('django_unhosted.apps.account.urls')),
	url(r'^oauth2/', autons_include('django_unhosted.apps.oauth2.urls')),
	url(r'^api/', autons_include('django_unhosted.apps.api.urls')),

	url(r'', autons_include('django_unhosted.apps.demo.urls')),
)
