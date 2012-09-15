#-*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools as it, operator as op, functools as ft
from hashlib import sha512
import re, urllib

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.utils.encoding import smart_unicode, iri_to_uri
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.views.decorators.csrf import csrf_protect

from oauth2app.authorize import Authorizer, TOKEN,\
	MissingRedirectURI, AuthorizationException, InvalidClient, InvalidScope,\
	UnvalidatedRequest, UnauthenticatedUser
from oauth2app.models import Client, AccessRange

from django_remotestorage.utils import messages, login_required
from .forms import AuthorizeForm


def canonical_path_spec(path_spec):
	'''Strip slashes at start/end of path part,
		collapse redundant ones, add ":rw", if only path is given.'''
	try: path, caps = path_spec.rsplit(':', 1)
	except ValueError: path, caps = path_spec, 'rw'
	path = '/'.join(it.ifilter(None, path.split('/')))
	return '{}:{}'.format(path, caps)


@login_required
def missing_redirect_uri(request):
	return render_to_response(
		'oauth2/missing_redirect_uri.html',
		dict(), RequestContext(request) )


@csrf_protect
@login_required
def authorize(request):
	# Workaround for OAuth2 issue in 0.6.9 (and earlier) remoteStorage.js versions.
	#  http://www.w3.org/community/unhosted/wiki/RemoteStorage-2011.10#OAuth
	# Also see "Known Issues / OAuth2" section in README.
	scope = request.REQUEST.get('scope')
	if scope and ':' not in scope:
		query = urllib.urlencode(dict(it.chain(
			request.REQUEST.items(),
			[('scope', ' '.join(
				canonical_path_spec(path) for path in scope.split(',') ))] )))
		return HttpResponseRedirect('{}?{}'.format(request.path, iri_to_uri(query)))

	# Process OAuth2 request from query_string
	authorizer = Authorizer(response_type=TOKEN)
	validate_missing, validate_kwz = None, dict(check_scope=False)
	try:
		try: authorizer.validate(request, **validate_kwz)
		except TypeError: # older version
			validate_kwz.pop('check_scope')
			authorizer.validate(request)
	except MissingRedirectURI:
		return HttpResponseRedirect(reverse('remotestorage:oauth2:missing_redirect_uri'))
	except (InvalidClient, InvalidScope) as err:
		if isinstance(err, InvalidClient): validate_missing = 'client'
		else: validate_missing = 'scope'
	except AuthorizationException:
		# The request is malformed or otherwise invalid.
		# Automatically redirects to the provided redirect URL,
		#  providing error parameters in GET, as per spec.
		return authorizer.error_redirect()

	paths = authorizer.scope
	form = ft.partial(AuthorizeForm, paths=paths, app=authorizer.client_id)

	if request.method == 'GET':
		# Display form with a glorified "authorize? yes/no" question.
		if validate_missing == 'client':
			# With remoteStorage (0.6.9), client_id is the hostname of a webapp site,
			#  which is requesting storage, so it's a new app, and that fact should be
			#  made clear to the user.
			messages.add_message(
				request, messages.WARNING,
				( 'This is the first time app from domain "{}"'
					" tries to access this storage, make sure it's"
					' the one you want to grant access to.' )\
				.format(smart_unicode(authorizer.client_id)) )
		form = form()
		# Stored to validate that nothing has extended the submitted list client-side
		request.session['authorizer.paths'] = paths

	elif request.method == 'POST':
		if not paths or paths != request.session.get('authorizer.paths'):
			# These paths can potentially be tampered with in the submitted form client-side,
			#  resulting in granting access to something user didn't see in the displayed form,
			#  hence passing the list server-side as well within the session
			return HttpResponseRedirect(request.get_full_path())
		form = form(request.POST)
		if form.is_valid():
			# Check list of authorized paths, building new scope
			paths_auth, paths_form = set(), set(form.cleaned_data['path_access'])
			while paths_form:
				path_spec = paths_form.pop()
				# Try to condense :r and :w to :rw
				path, cap = path_spec.split(':')
				for a, b in 'rw', 'wr':
					if cap == a and '{}:{}'.format(path, b) in paths_form:
						paths_auth.add('{}:rw'.format(path))
						paths_form.remove('{}:{}'.format(path, b))
						break
				else: paths_auth.add(path_spec)
			# Re-validate form, creating missing models
			if validate_missing:
				try:
					with transaction.commit_on_success():
						if validate_missing == 'client':
							Client.objects.create( user=request.user,
								name=authorizer.client_id, key=authorizer.client_id )
						if 'check_scope' not in validate_kwz:
							# Create all these just to delete them after validation
							for path_spec in paths:
								AccessRange.objects.get_or_create(key=path_spec)
						authorizer.validate(request, **validate_kwz)
						for path_spec in paths_auth:
							AccessRange.objects.get_or_create(key=path_spec)
						if 'check_scope' not in validate_kwz:
							for path_spec in paths.difference(paths_auth):
								try: AccessRange.objects.get(key=path_spec).delete()
								except (IntegrityError, ObjectDoesNotExist): pass
				except AuthorizationException:
					return authorizer.error_redirect()
			authorizer.scope = paths_auth
			return authorizer.grant_redirect()\
				if form.cleaned_data['authorize'] == 'allow'\
				else authorizer.error_redirect()

	if request.method in ['GET', 'POST']:
		return render_to_response( 'oauth2/authorize.html',
			dict(form=form, app_host=authorizer.client_id), RequestContext(request) )

	# Shouldn't get here unless by mistake
	return HttpResponse( '<h1>Please issue proper'
		' GET request with OAuth2 authorization parameters.</h1>', status=501 )
