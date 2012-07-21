#-*- coding: utf-8 -*-

import itertools as it, operator as op, functools as ft
from os.path import join, dirname
import mimetypes, httplib, errno

from django.conf import settings
from django.core.files.storage import get_storage_class
from django.core.files.base import ContentFile
from django.http import HttpResponse,\
	HttpResponseRedirect, HttpResponseNotAllowed,\
	HttpResponseNotFound, HttpResponseNotModified,\
	HttpResponseForbidden
from django.views.decorators.http import condition

from oauth2app.authenticate import Authenticator, AuthenticationException
from django_unhosted.utils import http_date

from .models import StoredObject


def methods(path, exists=False, can_be_created=False):
	if path and not exists:
		return 'OPTIONS' if parent_used\
			else ['OPTIONS', 'PUT', 'MKCOL', 'LOCK', 'UNLOCK']
	else:
		opts = [ 'OPTIONS', 'GET', 'HEAD', 'POST', 'DELETE', 'TRACE',
				'PROPFIND', 'PROPPATCH', 'COPY', 'MOVE', 'LOCK', 'UNLOCK' ]
		if path: opts.append('PUT')
		return opts

def caps(method):
	cap = list()
	if method in [ 'OPTIONS', 'GET', 'HEAD', 'TRACE',
		'COPY', 'MOVE', 'PROPFIND', 'PROPPATCH' ]: cap.append('r')
	if method in [ 'PUT', 'POST', 'MKCOL', 'DELETE',
		'LOCK', 'UNLOCK', 'MOVE', 'PROPPATCH' ]: cap.append('w')
	cap = {'rw', ''.join(cap)}
	return cap


def storage(request, acct, path=''):
	authenticator = Authenticator()
	try: authenticator.validate(request)
	except AuthenticationException:
		return authenticator.error_response(content='Authentication failure.')

	# Normalize the path
	path = '/'.join(it.ifilter(None, path.split('/')))
	path_dir = dirname(path)

	# Check if access to path is authorized for this token
	if not authenticator.scope.filter(
			key__in=['{}:{}'.format(path_dir, cap) for cap in caps(request.method)] ).exists():
		return HttpResponseForbidden( 'Access (method: {})'
			' to path "{}" is forbidden for this token.'.format(request.method, path) )

	return storage_api( request,
		StoredObject.objects.user_path(authenticator.user, path) )


@condition(
	etag_func=lambda request, obj: obj.etag,
	last_modified_func=lambda request, obj: obj.mtime )
def storage_api(request, obj):
	if obj.data: fs = obj.data.storage

	if request.method in ['GET', 'HEAD']:
		if not obj.data:
			return HttpResponseNotFound(
				'Path {!r} does not exists'.format(obj.path) )

		# Optimizations
		if getattr(settings, 'UNHOSTED_DAV_SENDFILE', False):
			try: real_path = fs.path(obj.data.name)
			except NotImplementedError: pass
			else:
				response = HttpResponse()
				response['X-SendFile'] = real_path
				return response
		accel_redir = getattr(settings, 'UNHOSTED_DAV_ACCEL', None)
		if accel_redir is not None:
			response = HttpResponse()
			response['X-Accel-Redirect'] = join(accel_redir, obj.path)
			# response['X-Accel-Charset'] = 'utf-8'
			return response
		if getattr(settings, 'UNHOSTED_DAV_REDIRECT', False)\
				and getattr(settings, 'MEDIA_URL', False):
			try: return HttpResponseRedirect(obj.data.url)
			except NotImplementedError: pass

		# Worst case - pipe through python
		content_type = mimetypes.guess_type(obj.path)
		if isinstance(content_type, tuple):
			content_type = '{}; charset={}'.format(*content_type)

		response = HttpResponse(fs.open(obj.data.name), content_type=content_type)

		response['Date'] = http_date()
		if obj.size is not None: response['Content-Length'] = obj.size
		if obj.mtime is not None: response['Last-Modified'] = http_date(obj.mtime)
		if obj.etag is not None: response['ETag'] = obj.etag
		return response

	elif request.method == 'PUT':
		created = not obj.data
		fs.delete(obj.data.name)
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
