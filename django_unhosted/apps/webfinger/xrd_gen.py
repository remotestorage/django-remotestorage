#-*- coding: utf-8 -*-

from django.template.loader import BaseLoader
from django.template.base import TemplateDoesNotExist
from django.conf import settings

from xrd import Link, generate_xrd, generate_jrd

try: import simplejson as json
except ImportError: import json


# Ideally, these XRDs should be signed, but no support for that atm
#  http://docs.oasis-open.org/xri/xrd/v1.0/xrd-1.0.html#signature

# https://tools.ietf.org/html/draft-jones-appsawg-webfinger-01

# Looking at existing implementation (Unhosted.py),
#  XRD seem to requre \r\n line breaks, but I can't find that in the specs
# Just using .replace('\n', '\r\n') on templates should break signatures there


class XRDTemplateCache(object):

	def __init__(self):
		self._templates = dict()

	@staticmethod
	def serialize(fmt, **kwz):
		if fmt == 'xml':
			return generate_xrd(**kwz)\
				.toprettyxml(indent='  ', encoding=settings.DEFAULT_CHARSET)
		elif fmt == 'json':
			return json.dumps(generate_jrd(**kwz))
		else: raise ValueError('Unknown serialization format: {!r}'.format(fmt))

	@classmethod
	def gen_host_meta( cls, fmt='xml', href=None,
			template='{{ url_base }}{% url webfinger:webfinger fmt=q_fmt %}?uri={uri}' ):
		link = Link({'rel': 'lrdd', 'type': 'application/xrd+{}'.format(fmt)}, list(), list())
		if href: link.attributes['href'] = href
		else: link.attributes['template'] = template
		return cls.serialize(fmt, links=[link])

	@classmethod
	def gen_webfinger( cls, fmt='xml', href=None,
			auth='{% url oauth2:authorize %}?user={{ q_acct }}',
			template="{% url api:storage acct=q_acct path='' %}/{category}/" ):
		link = Link({'rel': 'remoteStorage', 'api': 'simple', 'auth': auth}, list(), list())
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
