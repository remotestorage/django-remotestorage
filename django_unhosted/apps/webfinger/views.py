#-*- coding: utf-8 -*-

from urlparse import urlparse

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import Http404


# Ideally, these XRDs should be signed
#  http://docs.oasis-open.org/xri/xrd/v1.0/xrd-1.0.html#signature

# Looking at existing implementation (Unhosted.py),
#  XRD seem to requre \r\n line breaks, but I can't find that in the specs
# Just using .replace('\n', '\r\n') on templates should break signatures there

# This stuff should be auto-generated from data,
#  so both /.well-known/host-meta.json and xml stuff will work
# Another plus is that it won't be a hand-crafted tag-soup, of course
# https://tools.ietf.org/html/draft-jones-appsawg-webfinger-01


def webfinger(request):
	try: subject = request.GET['uri']
	except KeyError: raise Http404
	subject_parsed = urlparse(subject, 'acct')
	if subject_parsed.scheme != 'acct': raise Http404
	return render_to_response(
		'webfinger/webfinger.xml',
		dict(q_subject=subject, q_acct=subject_parsed.path),
		mimetype='application/xrd+xml' )

def host_meta(request):
	return render_to_response(
		'webfinger/host_meta.xml',
		dict(url_base=request.build_absolute_uri('/').rstrip('/')),
		mimetype='application/xrd+xml' )
