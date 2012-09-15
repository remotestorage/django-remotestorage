#-*- coding: utf-8 -*-


### List of updates to settings.py tuples
###  (to be applied by "update_settings" function below).

updates = dict(
	## Size of oauth2app model fields, updated only if unset.
	## See "Known Issues / OAuth2" section
	##  in README file for reasoning behind these.
	OAUTH2_CLIENT_KEY_LENGTH = 1024,
	OAUTH2_SCOPE_LENGTH = 2048,

	## Request context processor is used in auth forms
	##  and external_resources_context is used in demo views.
	TEMPLATE_CONTEXT_PROCESSORS = [
		'django.core.context_processors.csrf',
		'django.core.context_processors.request',
		'django.contrib.messages.context_processors.messages',
		'django_remotestorage.utils.external_resources_context' ],

	## Caches XML templates for host-meta and webfinger requests.
	TEMPLATE_LOADERS = [
		'django_remotestorage.apps.webfinger.xrd_gen.Loader' ],

	## CSRF middleware BREAKS WebDAV methods,
	##  see "Known Issues / WebDAV" section in README for details.
	## Messages middleware is used in interfaces extensively.
	MIDDLEWARE_CLASSES = (
		lambda cls: cls != 'django.middleware.csrf.CsrfViewMiddleware',
		['django.contrib.messages.middleware.MessageMiddleware'] ),

	INSTALLED_APPS = [
		'django.contrib.messages',
		'django_remotestorage',
		'oauth2app' ] )

## "south" app is not strictly required, unless you need migrations.
try: import south
except ImportError: pass
else: updates['INSTALLED_APPS'].append('south')



### Provide some Django-1.4 defaults, so that module
###  can be imported into DJANGO_SETTINGS_MODULE, like this:
###
###   from django_remotestorage.settings_base import *

TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader' )

TEMPLATE_CONTEXT_PROCESSORS = (
	'django.contrib.auth.context_processors.auth',
	'django.core.context_processors.debug',
	'django.core.context_processors.i18n',
	'django.core.context_processors.media',
	'django.core.context_processors.static',
	'django.core.context_processors.tz' )

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware' )

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles' )



### Optinal "smart" settings module updater.
### Use it like this (at the end of settings.py):
###
###   from django_remotestorage.settings_base import update_settings
###   update_settings(__name__)

import sys, types, functools

def _update_module(mod, updates, only=None, ignore=None):

	def _smart_extend(base, update, update_filter=None):
		if not isinstance(update, list):
			return update if base is None else base
		base = list(base or list())
		if update_filter: base = filter(update_filter, base)
		for cls in update:
			if cls not in base: base.append(cls)
		return tuple(base) # django uses tuples

	if isinstance(mod, types.StringTypes): mod = sys.modules[mod]
	for k, v in updates.viewitems():
		if (only and k not in only) or (ignore and k in ignore): continue
		update_filter, update = v if isinstance(v, tuple) else (None, v)
		update = _smart_extend(getattr(mod, k, None), update, update_filter)
		setattr(mod, k, update)

update_settings = functools.partial(_update_module, updates=updates)

## Update django defaults (listed above) for direct imports
update_settings(__name__)
