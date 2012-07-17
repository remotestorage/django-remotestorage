#-*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools as it, operator as op, functools as ft
from hashlib import sha512

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.encoding import smart_unicode
from django.utils.http import urlquote, urlquote_plus
from django.db import transaction, IntegrityError

from oauth2app.authorize import Authorizer,\
	MissingRedirectURI, AuthorizationException, InvalidClient, InvalidScope,\
	UnvalidatedRequest, UnauthenticatedUser
from oauth2app.models import Client, AccessRange
from crispy_forms.helpers import FormHelper, Submit, Reset

from .forms import AuthorizeForm


def canonical_path_spec(path_spec):
	'''Strip slashes at start/end of path part,
		collapse redundant ones, add ":rw", if only path is given.'''
	try: path, caps = path_spec.rsplit(':', 1)
	except ValueError: path, caps = path_spec, 'rw'
	path = '/'.join(it.ifilter(None, path.split('/')))
	return '{}:{}'.format(path, caps)

def path_spec_cap(path_spec):
	'Transform path_spec to a "scope" cap for oauth2app.'
	return 'path:sha512:{}'.format(sha512(path_spec).hexdigest())


@login_required
def missing_redirect_uri(request):
	return render_to_response(
		'oauth2/missing_redirect_uri.html',
		dict(), RequestContext(request) )


@login_required
def authorize(request):
	# Workaround for OAuth2 issue in 0.6.9 (and earlier) remoteStorage.js versions.
	#  http://www.w3.org/community/unhosted/wiki/RemoteStorage-2011.10#OAuth
	# Also see "Known Issues / OAuth2" section in README.
	scope = request.REQUEST.get('scope')
	if scope and ':' not in scope:
		scope_fixed = urlquote_plus(' '.join(
			canonical_path_spec(path) for path in scope.split(',') ), safe='/:')
		url = request.get_full_path()
		for scope in urlquote(scope, safe=''), scope,\
				 urlquote(scope), urlquote(scope, safe=','), urlquote_plus(scope):
			url_fixed = url.replace(u'&scope={}'.format(scope), '&scope={}'.format(scope_fixed))
			if url != url_fixed: break
		else: raise ValueError('Failed to create redirect URL with fixed "scope" parameter')
		return HttpResponseRedirect(url_fixed)

	# Process OAuth2 request from query_string
	authorizer = Authorizer()
	missing_models = None
	try: authorizer.validate(request)
	except MissingRedirectURI:
		return HttpResponseRedirect(reverse('missing_redirect_uri'))
	except (InvalidClient, InvalidScope) as err:
		if isinstance(err, InvalidClient): missing_models = 'client'
		else: missing_models = 'scope'
	except AuthorizationException:
		# The request is malformed or otherwise invalid.
		# Automatically redirects to the provided redirect URL,
		#  providing error parameters in GET, as per spec.
		return authorizer.error_redirect()

	paths = set(it.imap(canonical_path_spec, authorizer.scope))
	form = ft.partial( AuthorizeForm, paths=paths,
		app=authorizer.client_id, action=request.get_full_path() )

	if request.method == 'GET':
		# Display form with a glorified "authorize? yes/no" question.
		# Scope/client_id are set even in case of failed validation,
		#  not sure if it's safe to rely on that in the future though.
		if missing_models == 'client':
			# With remoteStorage (0.6.9), client_id is the hostname of a webapp site,
			#  which is requesting storage, so it's a new app, and that fact should be
			#  made clear to the user.
			messages.add_message(
				request, messages.WARNING,
				( u'It is the first time app from domain {}'
					u' tries to access this storage, make sure it is the one you want to.' )\
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
			if missing_models:
				try:
					with transaction.commit_on_success():
						if missing_models == 'client':
							Client.objects.create(name=authorizer.client_id, user=request.user)
						if missing_models: # at least some "scopes" are missing
							for path_spec in form.cleaned_data['path_access']:
								scope, created = AccessRange.objects.get_or_create(
									key=path_spec_cap(path_spec), defaults=dict(description=path_spec) )
								if not created and scope.description != path_spec:
									raise NotImplementedError( ( 'Detected hash colision'
											' when inserting path_spec {!r} with existing path_spec {!r}' )\
										.format(path_spec, scope.description) )
						# Can still raise all kinds of errors, rolling back updates above
						authorizer.validate(request)
				except AuthorizationException: return authorizer.error_redirect()
			return authorizer.grant_redirect()\
				if form.cleaned_data['connect'] == 'Yes' else authorizer.error_redirect()

	if request.method in ['GET', 'POST']:
		return render_to_response( 'oauth2/authorize.html',
			dict(form=form, app_host=authorizer.client_id), RequestContext(request) )

	# Shouldn't get here unless by mistake
	return HttpResponse( '<h1>Please issue proper'
		' GET request with OAuth2 authorization parameters.</h1>', status=501 )
