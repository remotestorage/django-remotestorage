#-*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include
from django.conf import settings

from .apps.account import urls as urls_account
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
	('oauth2', url( r'^oauth2/',
		autons_include('django_unhosted.apps.oauth2.urls') )),
	('api', url( r'^api/',
		autons_include('django_unhosted.apps.api.urls') )),
	('demo', url( r'',
		autons_include('django_unhosted.apps.demo.urls') )) ]

urlconf_enabled = set(getattr( settings,
	'UNHOSTED_COMPONENTS',
	['webfinger', 'oauth2', 'api', 'demo', 'account'] ) or list())

urlconf_patterns = list( url for name, url
	in urlconf_patterns if name in urlconf_enabled )

if 'account' in urlconf_enabled:
	urlconf_patterns.append(url( r'^account/',
		autons_include('django_unhosted.apps.account.urls') ))

else:
	account_patterns = list()
	for k in 'auth', 'auth_management', 'client_management':
		if 'account_{}'.format(k) not in urlconf_enabled: continue
		account_patterns.extend(
			getattr(urls_account, 'urlpatterns_{}'.format(k)) )
	urlconf_patterns.append(url( r'^account/',
		include(patterns('', *account_patterns), 'account', 'account') ))

urlconf_patterns = patterns('', *urlconf_patterns)

# "unhosted" app_name is used in reverse()'ing links,
#  so make sure to include that in any custom non-derived urlconf.
unhosted_patterns = urlconf_patterns, 'unhosted', 'unhosted'
