#-*- coding: utf-8 -*-

import itertools as it, operator as op, functools as ft
from urlparse import urlparse
from hashlib import sha1
import os

from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django import template
from django.conf import settings
from django.views.decorators.http import etag

from django_remotestorage import __version__
from django_remotestorage.utils import cors_wrapper
from .xrd_gen import xrd_cache


xrd_mime = lambda fmt:\
	'application/xrd+{}; charset={}'.format(fmt, settings.DEFAULT_CHARSET)


etag_base = sha1(__version__).hexdigest()

def etag_func(request, ext=None, fmt=None):
	return sha1('\0'.join(it.imap(bytes, [
		etag_base, ext, fmt,
		request.build_absolute_uri('/'),
		reverse('remotestorage:webfinger:webfinger'),
		reverse('remotestorage:api:storage', kwargs=dict(acct='dummy', path='')),
		request.GET.get('uri', '') ]))).hexdigest()


@etag(etag_func)
@cors_wrapper
def host_meta(request, ext=None, fmt='xml'):
	assert fmt in ['xml', 'json']
	try: tpl = template.loader.get_template('webfinger/host_meta.{}'.format(fmt))
	except template.TemplateDoesNotExist:
		page = xrd_cache.gen_host_meta( fmt=fmt,
			template='{}?uri={{uri}}'.format(request.build_absolute_uri(
				reverse('remotestorage:webfinger:webfinger', kwargs=dict(fmt=fmt)) )) ),
	else:
		page = tpl.render(template.RequestContext(
			request, dict(q_fmt=fmt, url_base=request.build_absolute_uri('/').rstrip('/')) ))
	return HttpResponse(page, content_type=xrd_mime(fmt))


@etag(etag_func)
@cors_wrapper
def webfinger(request, ext=None, fmt='xml'):
	assert fmt in ['xml', 'json']

	try: subject = request.GET['uri']
	except KeyError: raise Http404
	subject_parsed = urlparse(subject, 'acct')
	if subject_parsed.scheme != 'acct'\
		or '@' not in subject_parsed.path: raise Http404
	acct = subject_parsed.path.split('@', 1)[0]

	try: tpl = template.loader.get_template('webfinger/webfinger.{}'.format(fmt))
	except template.TemplateDoesNotExist:
		page = xrd_cache.gen_webfinger( fmt=fmt,
			auth='{}?user={}'.format(
				request.build_absolute_uri(reverse('remotestorage:oauth2:authorize')), acct),
			template='{}/{{category}}/'.format(request.build_absolute_uri(
				reverse('remotestorage:api:storage', kwargs=dict(acct=acct, path='')) )) )
	else:
		page = tpl.render(template.RequestContext(
			request, dict(q_fmt=fmt, q_subject=subject, q_acct=acct) )),
	return HttpResponse(page, content_type=xrd_mime(fmt))
