#-*- coding: utf-8 -*-

import itertools as it, operator as op, functools as ft
from datetime import datetime
import calendar

from django.conf.urls import include, url
from django.utils.http import http_date as django_http_date


autonamed_url = lambda pat, mod, **kwz:\
	url(pat, mod, name=mod.rsplit('.', 1)[-1], **kwz)

def autons_include(mod, **kwz):
	ns = (mod[:-5] if mod.endswith('.urls') else mod).rsplit('.', 1)[-1]
	return include(mod, namespace=ns, **kwz)


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
