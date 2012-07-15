#-*- coding: utf-8 -*-

from django.template.loader import BaseLoader
from django.template.base import TemplateDoesNotExist
from django.conf import settings

from xrd import XRD, Link


# Ideally, these XRDs should be signed, but python-xrd doesn't support that atm
#  http://docs.oasis-open.org/xri/xrd/v1.0/xrd-1.0.html#signature

# https://tools.ietf.org/html/draft-jones-appsawg-webfinger-01

# Looking at existing implementation (Unhosted.py),
#  XRD seem to requre \r\n line breaks, but I can't find that in the specs
# Just using .replace('\n', '\r\n') on templates should break signatures there


class XRDTemplateCache(object):

	def __init__(self):
		self._templates = dict()

	@staticmethod
	def gen_host_meta( fmt='xml',
			href='{{ url_base }}{% url webfinger:webfinger fmt=q_fmt %}?uri={uri}' ):
		xrd = XRD()
		xrd.links.append(Link( rel='lrdd',
			type_='application/xrd+{}'.format(fmt), href=href ))
		return xrd

	@staticmethod
	def gen_webfinger( fmt='xml',
			auth='{% url oauth2:authorize %}?user={{ q_acct }}',
			template='{% url api:storage q_acct %}/{category}/' ):
		xrd = XRD()
		xrd.links.append(Link( rel='remoteStorage',
			template=template, api='simple', auth=auth ))
		return xrd

	@property
	def templates(self):
		if not self._templates:
			for tpl in 'host_meta', 'webfinger':
				generate = getattr(self, 'gen_{}'.format(tpl))
				self._templates['webfinger/{}.xml'.format(tpl)] = generate('xml')\
					.to_xml().toprettyxml(indent='  ', encoding=settings.DEFAULT_CHARSET)
				## JSON responses should not use templates to ensure proper serialization
				# self._templates['webfinger/{}.json'.format(tpl)] = generate('json').to_json()
		return self._templates

xrd_cache = XRDTemplateCache()


class Loader(BaseLoader):

	is_usable = True

	def load_template_source(self, template_name, template_dirs=None):
		try: return xrd_cache.templates[template_name], template_name
		except KeyError:
			raise TemplateDoesNotExist(template_name)
