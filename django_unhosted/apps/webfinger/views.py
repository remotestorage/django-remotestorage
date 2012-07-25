#-*- coding: utf-8 -*-

from urlparse import urlparse

from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django import template
from django.conf import settings
from django.views.decorators.cache import cache_page

from django_unhosted.utils import cors_wrapper
from .xrd_gen import xrd_cache


# TODO: caching (server- and client-side) for these (almost-static) pages


xrd_mime = lambda fmt:\
	'application/xrd+{}; charset={}'.format(fmt, settings.DEFAULT_CHARSET)
cache_time = getattr(settings, 'UNHOSTED_CACHE_TIME', 3600)


@cache_page(cache_time)
@cors_wrapper
def host_meta(request, ext=None, fmt='xml'):
	assert fmt in ['xml', 'json']
	try: tpl = template.loader.get_template('webfinger/host_meta.{}'.format(fmt))
	except template.TemplateDoesNotExist:
		page = xrd_cache.gen_host_meta( fmt=fmt,
			template='{}?uri={{uri}}'.format(request.build_absolute_uri(
				reverse('webfinger:webfinger', kwargs=dict(fmt=fmt)) )) ),
	else:
		page = tpl.render(template.RequestContext(
			request, dict(q_fmt=fmt, url_base=request.build_absolute_uri('/').rstrip('/')) ))
	return HttpResponse(page, content_type=xrd_mime(fmt))


@cache_page(cache_time)
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
			auth='{}?user={}'.format(reverse('oauth2:authorize'), acct),
			template='{}/{{category}}/'.format(
				reverse('api:storage', kwargs=dict(acct=acct, path='')) ) )
	else:
		page = tpl.render(template.RequestContext(
			request, dict(q_fmt=fmt, q_subject=subject, q_acct=acct) )),
	return HttpResponse(page, content_type=xrd_mime(fmt))
