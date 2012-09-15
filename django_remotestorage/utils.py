#-*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools as it, operator as op, functools as ft
from datetime import datetime
from os.path import exists, join
import calendar

from django.conf import settings
from django.conf.urls import include, url
from django.utils.http import http_date as django_http_date
from django.contrib import messages as django_messages
from django.contrib.auth.decorators import login_required as django_login_required
from django.utils.functional import curry, lazy
from django.core.urlresolvers import reverse, NoReverseMatch


autonamed_url = lambda pat, mod, **kwz:\
	url(pat, mod, name=mod.rsplit('.', 1)[-1], **kwz)

def autons_include(mod, **kwz):
	ns = (mod[:-5] if mod.endswith('.urls') else mod).rsplit('.', 1)[-1]
	return include(mod, app_name=ns, namespace=ns)


def reverse_with_fallback(name, fallback):
	try: return reverse(name)
	except NoReverseMatch: return fallback
reverse_with_fallback_lazy = lazy(reverse_with_fallback, str)
login_required = curry( django_login_required,
	login_url=reverse_with_fallback_lazy(
		'remotestorage:account:login', settings.LOGIN_URL ) )


def cors_wrapper(func):
	@ft.wraps(func)
	def wrapper(*argz, **kwz):
		response = func(*argz, **kwz)
		for k,v in [
				('Access-Control-Allow-Origin', '*'),
				('Access-Control-Max-Age', 1000),
				('Access-Control-Allow-Headers', '*'),
				('Access-Control-Allow-Credentials', 'true'),
				('Access-Control-Expose-Headers', '*'),
				# Following methods are chosen on "enough for remoteStorage.js" basis
				('Access-Control-Allow-Methods', 'OPTIONS, PUT, DELETE') ]:
			if k not in response: response[k] = v
		return response
	return wrapper


def http_date(ts=None):
	if isinstance(ts, datetime):
		ts = calendar.timegm(ts.utctimetuple())
	return django_http_date(ts)


def external_resources_context(request):
	def try_local(path, url):
		return join(settings.STATIC_URL, path)\
			if exists(join(settings.STATIC_ROOT, path))\
			else url
	return dict(
		url_res_bootsrap=try_local( 'bootstrap/css/bootstrap.min.css',
			'http://current.bootstrapcdn.com'
				'/bootstrap-v204/css/bootstrap-combined.min.css' ),
		url_res_remotestorage=try_local( 'django_remotestorage_client/remoteStorage.js',
			'http://cdnjs.cloudflare.com/ajax/libs/remoteStorage/0.6.9/remoteStorage.min.js' ),
		url_res_jquery=try_local( 'django_remotestorage_client/jquery.js',
			'http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js' ) )


class MessagesProxy(object):
	def __getattr__(self, k):
		attr = getattr(django_messages, k)
		if k in ['debug', 'info', 'success', 'warning', 'error']:
			attr = ft.partial(attr, extra_tags='alert-{}'.format(k), fail_silently=True)
		return attr

messages = MessagesProxy()
