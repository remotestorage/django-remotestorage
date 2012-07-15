#-*- coding: utf-8 -*-

from django.conf.urls import include, url

autonamed_url = lambda pat, mod, **kwz:\
	url(pat, mod, name=mod.rsplit('.', 1)[-1], **kwz)

def autons_include(mod, **kwz):
	ns = (mod[:-5] if mod.endswith('.urls') else mod).rsplit('.', 1)[-1]
	return include(mod, namespace=ns, **kwz)
