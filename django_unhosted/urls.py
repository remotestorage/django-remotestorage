#-*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include
from django.conf import settings
from .utils import autons_include

## This module cannot be imported with just "include('django_unhosted.urls')"
##
## Use following code instead:
##   from django_unhosted.urls import unhosted_patterns
##   ...
##   include(unhosted_patterns)

# Reason for that is that include('module.path') doesn't let
#  included module specify app_name and namespace

urlconf_patterns = [
	('webfinger', url( r'',
		autons_include('django_unhosted.apps.webfinger.urls') )),
	('account', url( r'^account/',
		autons_include('django_unhosted.apps.account.urls') )),
	('oauth2', url( r'^oauth2/',
		autons_include('django_unhosted.apps.oauth2.urls') )),
	('api', url( r'^api/',
		autons_include('django_unhosted.apps.api.urls') )),
	('demo', url( r'',
		autons_include('django_unhosted.apps.demo.urls') )) ]

urlconf_enabled = getattr( settings,
	'UNHOSTED_COMPONENTS', None )
if urlconf_enabled is None: urlconf_enabled = dict(urlconf_patterns)

urlconf_patterns = patterns( '',
	*(url for name, url in urlconf_patterns if name in urlconf_enabled) )

# "unhosted" app_name is used in reverse()'ing links,
#  so make sure to include that in any custom non-derived urlconf.
unhosted_patterns = urlconf_patterns, 'unhosted', 'unhosted'
