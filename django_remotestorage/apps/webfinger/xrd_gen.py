#-*- coding: utf-8 -*-

from django.template.loader import BaseLoader
from django.template.base import TemplateDoesNotExist
from django.conf import settings

from xrd import Link, Property, generate_xrd, generate_jrd

try: import simplejson as json
except ImportError: import json


# Ideally, these XRDs should be signed, but no support for that atm
#  http://docs.oasis-open.org/xri/xrd/v1.0/xrd-1.0.html#signature

# https://tools.ietf.org/html/draft-jones-appsawg-webfinger-01

# Looking at existing implementation (Remotestorage.py),
#  XRD seem to requre \r\n line breaks, but I can't find that in the specs
# Just using .replace('\n', '\r\n') on templates should break signatures there


class XRDTemplateCache(object):

	_abs_url_prefix = '{% if request.is_secure %}https'\
		'{% else %}http{% endif %}://{{ request.get_host }}'

	def __init__(self):
		self._templates = dict()

	@staticmethod
	def serialize(fmt, **kwz):
		if fmt == 'xml':
			return generate_xrd(**kwz)\
				.toprettyxml(indent='  ', encoding=settings.DEFAULT_CHARSET)
		elif fmt == 'json':
			return json.dumps(generate_jrd(**kwz))
		raise ValueError('Unknown serialization format: {!r}'.format(fmt))

	@classmethod
	def gen_host_meta( cls, fmt='xml', href=None,
			template='{{ url_base }}{% url remotestorage:webfinger:webfinger fmt=q_fmt %}?uri={uri}',
			**attrs ):
		link = Link(dict( rel='lrdd',
			type='application/xrd+{}'.format(fmt), **attrs ), list(), list())
		if href: link.attributes['href'] = href
		else: link.attributes['template'] = template
		return cls.serialize(fmt, links=[link])

	@classmethod
	def gen_webfinger( cls, fmt='xml', href=None,
			auth_method='http://tools.ietf.org/html/draft-ietf-oauth-v2-26#section-4.2',
			auth=_abs_url_prefix + '{% url remotestorage:oauth2:authorize %}?user={{ q_acct }}',
			template=_abs_url_prefix + "{% url remotestorage:api:storage acct=q_acct path='' %}/{category}/",
			type='https://www.w3.org/community/rww/wiki/read-write-web-00#simple' ):
		link = Link(
			dict(auth=auth, api='simple', rel='remoteStorage', type=type),
			list(), [
				Property(auth, dict(type='auth_endpoint')),
				Property(auth_method, dict(type='auth_method')) ] )
		if href: link.attributes['href'] = href
		else: link.attributes['template'] = template
		return cls.serialize(fmt, links=[link])

	@property
	def templates(self):
		if not self._templates:
			for tpl in 'host_meta', 'webfinger':
				generate = getattr(self, 'gen_{}'.format(tpl))
				self._templates['webfinger/{}.xml'.format(tpl)] = generate('xml')
				## JSON responses should not use templates to ensure proper serialization
				# self._templates['webfinger/{}.json'.format(tpl)] = generate('json')
		return self._templates

xrd_cache = XRDTemplateCache()


class Loader(BaseLoader):

	is_usable = True

	def load_template_source(self, template_name, template_dirs=None):
		try: return xrd_cache.templates[template_name], template_name
		except KeyError:
			raise TemplateDoesNotExist(template_name)
