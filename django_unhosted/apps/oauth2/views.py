#-*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from oauth2app.authorize import Authorizer, MissingRedirectURI, AuthorizationException
from oauth2app.authorize import UnvalidatedRequest, UnauthenticatedUser
from crispy_forms.helpers import FormHelper, Submit, Reset

from .forms import AuthorizeForm


@login_required
def missing_redirect_uri(request):
	return render_to_response(
		'oauth2/missing_redirect_uri.html',
		dict(), RequestContext(request) )


@login_required
def authorize(request):
	authorizer = Authorizer()
	try: authorizer.validate(request)
	except MissingRedirectURI:
		return HttpResponseRedirect(reverse('missing_redirect_uri'))
	except (InvalidClient, InvalidScope) as err:
		if isinstance(err, InvalidClient):
			# With remoteStorage (0.6.9), client_id is the hostname of a webapp site,
			#  which is requesting storage, so it's a new app, and that fact should be
			#  made clear to the user.
			# Scope (path, basically) *might* be undefined yet as well.
			raise NotImplementedError('Add message about first-time-for-app.')
		raise NotImplementedError('Yes/No/path_components page for user.')
	except AuthorizationException:
		# The request is malformed or otherwise invalid.
		# Automatically redirects to the provided redirect URL,
		#  providing error parameters in GET, as per spec.
		return authorizer.error_redirect()

	if request.method == 'GET':
		# Make sure the authorizer is validated before requesting
		#  the client or access_ranges as otherwise they will be None.
		ctx = dict(
			client=authorizer.client,
			access_ranges=authorizer.access_ranges )
		helper = FormHelper()
		ctx['form'], ctx['helper'] = AuthorizeForm(), helper
		helper.add_input(Submit('connect', 'No'))
		helper.add_input(Submit('connect', 'Yes'))
		helper.form_action = '{}?{}'.format(
			reverse('authorize'), authorizer.query_string )
		helper.form_method = 'POST'
		return render_to_response(
			'oauth2/authorize.html', ctx, RequestContext(request) )

	elif request.method == 'POST':
		form = AuthorizeForm(request.POST)
		if form.is_valid():
			return authorizer.grant_redirect()\
				if request.POST.get('connect') == 'Yes' else authorizer.error_redirect()

	return HttpResponseRedirect(reverse('django_unhosted:root'))
