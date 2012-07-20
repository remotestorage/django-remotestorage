#-*- coding: utf-8 -*-

from os.path import join
from datetime import datetime
import mimetypes, hashlib, httplib, errno, calendar

from django.core.files.storage import get_storage_class
from django.core.files.base import ContentFile
from django.http import HttpResponse,\
	HttpResponseRedirect, HttpResponseNotAllowed,\
	HttpResponseNotFound, HttpResponseNotModified
from django.utils.http import http_date
from django.conf import settings
from django.views.decorators.http import condition

from oauth2app.authenticate import Authenticator, AuthenticationException


fs = get_storage_class(getattr(
	settings, 'UNHOSTED_DAV_STORAGE', None ))()


def methods(path, fs_path):
	if path and not fs.exists(fs_path):
		return 'OPTIONS'\
			if fs.get_available_name(fs_path) != fs_path\
			else ['OPTIONS', 'PUT', 'MKCOL', 'LOCK', 'UNLOCK']
	else:
		opts = [ 'OPTIONS', 'GET', 'HEAD', 'POST', 'DELETE', 'TRACE',
				'PROPFIND', 'PROPPATCH', 'COPY', 'MOVE', 'LOCK', 'UNLOCK' ]
		if path: opts.append('PUT')
		return opts

def http_date_ext(ts=None):
	if isinstance(ts, datetime):
		ts = calendar.timegm(ts.utctimetuple())
	return http_date(ts)


def storage(request, acct, path=''):
	authenticator = Authenticator()
	try: authenticator.validate(request)
	except AuthenticationException:
		return authenticator.error_response(content='Authentication failure.')

	# TODO: check path aganst scope
	# TODO: record original path into db, so there won't be
	#  conflicts due to fs.get_valid_name(path1) == fs.get_valid_name(path2)
	path = path.strip('/')
	fs_path = fs.get_valid_name(join(acct, path))

	try: fs_size = fs.size(fs_path)
	except (NotImplementedError, OSError): fs_size = None
	try: fs_mtime = fs.modified_time(fs_path)
	except (NotImplementedError, OSError):
		try: fs_mtime = fs.created_time(fs_path) # immutable storage?
		except (NotImplementedError, OSError): fs_mtime = fs_etag = None
	else:
		fs_etag = hashlib.sha1('{}\0{}'.format(
			http_date_ext(fs_mtime), fs_size )).hexdigest()

	return storage_api( request, path, fs_path,
		fs_size=fs_size, fs_mtime=fs_mtime, fs_etag=fs_etag )


@condition(
	etag_func=lambda *argz, **kwz: kwz.get('fs_etag', None),
	last_modified_func=lambda *argz, **kwz: kwz.get('fs_mtime', None) )
def storage_api( request, path, fs_path,
		fs_size=None, fs_mtime=None, fs_etag=None ):

	if request.method in ['GET', 'HEAD']:

		# Optimizations
		if getattr(settings, 'UNHOSTED_DAV_SENDFILE', False):
			try: real_path = fs.path(fs_path)
			except NotImplementedError: pass
			else:
				response = HttpResponse()
				response['X-SendFile'] = real_path
				return response
		accel_redir = getattr(settings, 'UNHOSTED_DAV_ACCEL', None)
		if accel_redir is not None:
			response = HttpResponse()
			response['X-Accel-Redirect'] = join(accel_redir, path)
			# response['X-Accel-Charset'] = 'utf-8'
			return response
		if getattr(settings, 'UNHOSTED_DAV_REDIRECT', False)\
				and getattr(settings, 'MEDIA_URL', False):
			try: return HttpResponseRedirect(fs.url(fs_path))
			except NotImplementedError: pass

		# Worst case - pipe through python
		content_type = mimetypes.guess_type(path)
		if isinstance(content_type, tuple):
			content_type = '{}; charset={}'.format(*content_type)

		try: response = HttpResponse(fs.open(fs_path), content_type=content_type)
		except IOError as err:
			if err.errno == errno.ENOENT:
				return HttpResponseNotFound('Path {!r} does not exists'.format(path))
			raise

		response['Date'] = http_date_ext()
		if fs_size is not None: response['Content-Length'] = fs_size
		if fs_mtime is not None: response['Last-Modified'] = http_date_ext(fs_mtime)
		if fs_etag is not None: response['ETag'] = fs_etag
		return response

	elif request.method == 'PUT':
		created = not fs.exists(fs_path) # racy!
		fs.save(fs_path, ContentFile(request.body))
		return HttpResponse(
			status=httplib.CREATED if created else httplib.NO_CONTENT )

	elif request.method == 'DELETE':
		if not fs.exists(fs_path): # racy!
			return HttpResponseNotFound()
		fs.delete(fs_path)
		return HttpResponse(status=httplib.NO_CONTENT)

	elif request.method == 'OPTIONS':
		response = HttpResponse(mimetype='httpd/unix-directory')
		for k,v in { 'DAV': '1,2', 'MS-Author-Via': 'DAV',
				'Date': http_date_ext(), 'Allow': methods(path, fs_path) }.viewitems():
			response[k] = v
		return response

	elif request.method in [ 'POST', 'TRACE', 'MKCOL',
			'PROPFIND', 'PROPPATCH', 'COPY', 'MOVE', 'LOCK', 'UNLOCK' ]:
		raise NotImplementedError('Method {}.'.format(request.method))

	return HttpResponseNotAllowed(methods(path, fs_path))
