#-*- coding: utf-8 -*-

import itertools as it, operator as op, functools as ft
from os.path import join, dirname
import mimetypes, httplib, errno, logging

from django.conf import settings
from django.core.files.base import ContentFile
from django.http import HttpResponse,\
	HttpResponseRedirect, HttpResponseNotAllowed,\
	HttpResponseNotFound, HttpResponseNotModified,\
	HttpResponseForbidden
from django.views.decorators.http import condition

from oauth2app.authenticate import Authenticator, AuthenticationException
from django_remotestorage.utils import http_date, cors_wrapper

from .models import User, StoredObject

log = logging.getLogger(__name__)


def methods(path, exists=False, can_be_created=False):
	if path and not exists:
		return 'OPTIONS' if not can_be_created\
			else ['OPTIONS', 'PUT', 'MKCOL', 'LOCK', 'UNLOCK']
	else:
		opts = [ 'OPTIONS', 'GET', 'HEAD', 'POST', 'DELETE', 'TRACE',
				'PROPFIND', 'PROPPATCH', 'COPY', 'MOVE', 'LOCK', 'UNLOCK' ]
		if path: opts.append('PUT')
		return opts

def caps(method):
	caps, auth_required = list(), False
	if method in [ 'OPTIONS', 'GET', 'HEAD', 'TRACE',
			'COPY', 'MOVE', 'PROPFIND', 'PROPPATCH' ]:
		caps.append('r')
		if method == 'PROPFIND': auth_required = True
	elif method in [ 'PUT', 'POST', 'MKCOL', 'DELETE',
			'LOCK', 'UNLOCK', 'MOVE', 'PROPPATCH' ]:
		caps.append('w')
		auth_required = True
	caps = {'rw', ''.join(caps)}.union(caps)
	return caps, auth_required


@cors_wrapper
def storage(request, acct, path=''):
	# Fast-path for CORS preflight requests
	if request.method == 'OPTIONS' and request.META.get('HTTP_ORIGIN')\
			and request.META.get('HTTP_ACCESS_CONTROL_REQUEST_METHOD'):
		# Mirror response headers
		response = HttpResponse('')
		response['Access-Control-Allow-Origin'] = request.META['HTTP_ORIGIN']
		response['Access-Control-Allow-Methods'] =\
			request.META['HTTP_ACCESS_CONTROL_REQUEST_METHOD']
		response['Access-Control-Allow-Headers'] =\
			request.META.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS', '*')
		return response

	authenticator = Authenticator()
	try: authenticator.validate(request)
	except AuthenticationException:
		auth_fail = authenticator.error_response(
			content='OAuth2 authentication failure,'
				' see "WWW-Authenticate" header for details.')
	else: auth_fail = None
	# It's also possible to check that acct==user here,
	#  but I'm not sure about how and when it's actually useful

	# Normalize the path
	path = '/'.join(it.ifilter(None, path.split('/')))

	# Check if access to path is authorized for this token
	category = dirname(path)
	path_caps, auth_required = caps(request.method)
	path_caps = list('{}:{}'.format(category, cap) for cap in path_caps)
	log.debug(( '(acct: {}, path: {}) required'
		' cap (any): {}' ).format(acct, path, ', '.join(path_caps)))

	if auth_fail:
		# One special case - "public:r" access, otherwise 401
		if auth_required or 'public:r' not in path_caps: return auth_fail
		user = User.objects.get(username=acct)
	elif not authenticator.scope.filter(key__in=path_caps).exists():
		# Authorized clients get 403 instead
		log.debug(( '(acct: {}, path: {}) access denied,'
			' caps available: {}' ).format( acct, path,
				', '.join(authenticator.scope.values_list('key', flat=True)) ))
		return HttpResponseForbidden( 'Access (method: {})'
			' to path "{}" is forbidden for this token.'.format(request.method, path) )
	else: user = authenticator.user

	return storage_api(request, StoredObject.objects.user_path(user, path))


@condition(
	etag_func=lambda request, obj: obj.etag,
	last_modified_func=lambda request, obj: obj.mtime )
def storage_api(request, obj):
	fs = obj.data.storage

	if request.method in ['GET', 'HEAD']:
		if not obj.data:
			return HttpResponseNotFound(
				'Path {!r} does not exists'.format(obj.path) )

		# Optimizations
		if getattr(settings, 'REMOTESTORAGE_DAV_SENDFILE', False):
			try: real_path = fs.path(obj.data.name)
			except NotImplementedError: pass
			else:
				response = HttpResponse()
				response['X-SendFile'] = real_path
				return response
		accel_redir = getattr(settings, 'REMOTESTORAGE_DAV_ACCEL', None)
		if accel_redir is not None:
			response = HttpResponse()
			response['X-Accel-Redirect'] = join(accel_redir, obj.path)
			# response['X-Accel-Charset'] = 'utf-8'
			return response
		if getattr(settings, 'REMOTESTORAGE_DAV_REDIRECT', False)\
				and getattr(settings, 'MEDIA_URL', False):
			try: return HttpResponseRedirect(obj.data.url)
			except NotImplementedError: pass

		# Worst case - pipe through python
		content_type, encoding = mimetypes.guess_type(obj.path)
		content_type = 'application/data' if content_type is None\
			else '{}; charset={}'.format(content_type, encoding)

		response = HttpResponse(
			fs.open(obj.data.name).read(), content_type=content_type )

		response['Date'] = http_date()
		if obj.size is not None: response['Content-Length'] = obj.size
		if obj.mtime is not None: response['Last-Modified'] = http_date(obj.mtime)
		if obj.etag is not None: response['ETag'] = obj.etag
		return response

	elif request.method == 'PUT':
		created = not obj.data
		if not created: fs.delete(obj.data.name)
		obj.data.save(obj.path, ContentFile(request.body))
		return HttpResponse(
			status=httplib.CREATED if created else httplib.NO_CONTENT )

	elif request.method == 'DELETE':
		if not obj.data: return HttpResponseNotFound()
		with transaction.commit_on_success():
			obj.delete()
			fs.delete(obj.data.name)
		return HttpResponse(status=httplib.NO_CONTENT)

	elif request.method == 'OPTIONS':
		response = HttpResponse(mimetype='httpd/unix-directory')
		for k,v in { 'DAV': '1,2', 'MS-Author-Via': 'DAV',
				'Date': http_date(), 'Allow': methods( obj.path,
					exists=obj.data, can_be_created=obj.can_be_created ) }.viewitems():
			response[k] = v
		return response

	elif request.method in [ 'POST', 'TRACE', 'MKCOL',
			'PROPFIND', 'PROPPATCH', 'COPY', 'MOVE', 'LOCK', 'UNLOCK' ]:
		raise NotImplementedError('Method {}.'.format(request.method))

	return HttpResponseNotAllowed(methods( obj.path,
		exists=obj.data, can_be_created=obj.can_be_created ))
