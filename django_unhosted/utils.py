#-*- coding: utf-8 -*-

import itertools as it, operator as op, functools as ft

from django.conf.urls import include, url


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
		response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
		response['Access-Control-Max-Age'] = 1000
		response['Access-Control-Allow-Headers'] = '*'
		response['Access-Control-Allow-Credentials'] = "true"
		response['Access-Control-Expose-Headers'] = '*'
		return response
	return wrapper
