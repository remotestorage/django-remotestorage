#-*- coding: utf-8 -*-

import itertools as it, operator as op, functools as ft
from datetime import datetime
from os.path import exists, join
import calendar

from django.conf import settings
from django.conf.urls import include, url
from django.utils.http import http_date as django_http_date
from django.contrib import messages as django_messages


autonamed_url = lambda pat, mod, **kwz:\
	url(pat, mod, name=mod.rsplit('.', 1)[-1], **kwz)

def autons_include(mod, **kwz):
	ns = (mod[:-5] if mod.endswith('.urls') else mod).rsplit('.', 1)[-1]
	return include(mod, app_name=ns, namespace=ns)


def cors_wrapper(func):
	@ft.wraps(func)
	def wrapper(*argz, **kwz):
		response = func(*argz, **kwz)
		response['Access-Control-Allow-Origin'] = '*'
		response['Access-Control-Max-Age'] = 1000
		response['Access-Control-Allow-Headers'] = '*'
		response['Access-Control-Allow-Credentials'] = "true"
		response['Access-Control-Expose-Headers'] = '*'
		# Following methods are chosen on "enough for remoteStorage.js" basis
		response['Access-Control-Allow-Methods'] = 'OPTIONS, PUT, DELETE'
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
		url_res_remotestorage=try_local( 'django_unhosted_client/remoteStorage.js',
			'http://tutorial.unhosted.5apps.com/js/remoteStorage-0.6.9.min.js' ),
		url_res_jquery=try_local( 'django_unhosted_client/jquery.js',
			'http://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js' ) )


class MessagesProxy(object):
	def __getattr__(self, k):
		attr = getattr(django_messages, k)
		if k in ['debug', 'info', 'success', 'warning', 'error']:
			attr = ft.partial(attr, extra_tags='alert-{}'.format(k), fail_silently=True)
		return attr

messages = MessagesProxy()
