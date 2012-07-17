#-*- coding: utf-8 -*-

from urlparse import urlparse

from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django import template
from django.conf import settings

from django_unhosted.utils import cors_wrapper
from .xrd_gen import xrd_cache


# TODO: caching (server- and client-side) for these (almost-static) pages


xrd_mime = lambda fmt:\
	'application/xrd+{}; charset={}'.format(fmt, settings.DEFAULT_CHARSET)


@cors_wrapper
def host_meta(request, ext=None, fmt='xml'):
	assert fmt in ['xml', 'json']

	try: tpl = template.loader.get_template('webfinger/host_meta.{}'.format(fmt))
	except template.TemplateDoesNotExist:
		if fmt != 'json': raise
		# Render proper JSON on-the-fly
		return HttpResponse(
			xrd_cache.gen_host_meta( fmt=fmt,
				template='{}?uri={{uri}}'.format(request.build_absolute_uri(
					reverse('webfinger:webfinger', kwargs=dict(fmt=fmt)) ))
			).to_json(),
			content_type=xrd_mime(fmt) )
	else:
		return HttpResponse(
			tpl.render(template.RequestContext(
				request, dict(q_fmt=fmt, url_base=request.build_absolute_uri('/').rstrip('/')) )),
			content_type=xrd_mime(fmt) )


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
		if fmt != 'json': raise
		# Render proper JSON on-the-fly
		return HttpResponse(
			xrd_cache.gen_webfinger( fmt=fmt,
				auth='{}?user={}'.format(reverse('oauth2:authorize'), acct),
				template='{}/{{category}}/'.format(
					reverse('api:storage', kwargs=dict(acct=acct)) )
			).to_json(),
			content_type=xrd_mime(fmt) )
	else:
		return HttpResponse(
			tpl.render(template.RequestContext(
				request, dict(q_fmt=fmt, q_subject=subject, q_acct=acct) )),
			content_type=xrd_mime(fmt) )
