#-*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools as it, operator as op, functools as ft
from time import time

from django.core.urlresolvers import reverse, NoReverseMatch
from django.http import HttpResponseRedirect,\
	HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect

from oauth2app.models import Client, AccessRange

from django_remotestorage.utils import messages, login_required
from .forms import SignupForm, LoginForm


def auth_redirect(request, redirect_field_name='next'):
	next_hop = request.GET.get(redirect_field_name)
	if not next_hop:
		try: next_hop = reverse('remotestorage:demo:storage_client')
		except NoReverseMatch: next_hop = reverse('remotestorage:account:clients')
	return HttpResponseRedirect(next_hop)


@csrf_protect
@login_required
def client(request, client_id, action):
	raise NotImplementedError('Not there yet')

@csrf_protect
@login_required
def client_action(request, client_id, action, cap=None):
	# POST-only to prevent CSRF exploits from extending/revoking access
	if request.method != 'POST':
		return HttpResponseNotAllowed(['POST'])
	client = Client.objects.get(id=client_id, user=request.user) # may raise 404

	if action == 'post': action = request.POST.get('action')

	if action == 'remove':
		if cap:
			tokens = list(client.accesstoken_set.filter(scope__key=cap))
			for token in tokens: token.scope.remove(*token.scope.filter(key=cap))
			messages.success( request, 'Successfully revoked'
				' capability "{}" from {} access tokens.'.format(cap, len(tokens)) )
			return HttpResponseRedirect(reverse('remotestorage:account:clients'))
		else:
			client.delete()
			messages.success( request,
				'Successfully revoked access for client "{}".'.format(client.name) )
			return HttpResponseRedirect(reverse('remotestorage:account:clients'))

	elif action == 'cap_add':
		if cap and cap != request.POST['cap']:
			return HttpResponseBadRequest(
				'Conflicting caps in URL/POST: {}, {}'.format(cap, request.POST['cap']) )
		cap = cap or request.POST['cap']
		if not cap:
			messages.error( request,
				'Access capability (like "path:rw") must be specified.' )
			return HttpResponseRedirect(reverse('remotestorage:account:clients'))
		cap_path, cap_perms = cap.rsplit(':', 1)
		if set(cap_perms).difference('rw'):
			messages.error( request, 'Invalid format'
				' for access capability (should be like "path:rw").' )
			return HttpResponseRedirect(reverse('remotestorage:account:clients'))
		cap_range, created = AccessRange.objects.get_or_create(key=cap)
		tokens = list(client.accesstoken_set.all())
		for token in tokens: token.scope.add(cap_range)
		messages.success( request, 'Successfully added'
			' capability "{}" to {} access tokens.'.format(cap, len(tokens)) )
		return HttpResponseRedirect(reverse('remotestorage:account:clients'))

	elif action == 'cap_cleanup':
		tokens = client.accesstoken_set.filter(expire__lte=time())
		tokens_count = tokens.count()
		tokens.delete()
		messages.success(request, '{} access tokens removed.'.format(tokens_count))
		return HttpResponseRedirect(reverse('remotestorage:account:clients'))

	return HttpResponseBadRequest('Unknown action: {}'.format(action))

@csrf_protect
@login_required
def clients(request):
	client_list, ts_now = list(), time()
	for client in Client.objects.filter(user=request.user):
		tokens = client.accesstoken_set
		info = dict(
			tokens_active=tokens.filter(expire__gt=ts_now),
			tokens_expired=tokens.filter(expire__lte=ts_now) )
		for k in 'active', 'expired':
			info['scope_{}'.format(k)] = set(it.ifilter( None,
				info['tokens_{}'.format(k)].values_list('scope__key', flat=True) ))
		info['status'] = 'No active tokens' if not info['tokens_active'].count() else 'Active'
		client_list.append((client, info))
	return render_to_response( 'account/clients.html',
		dict(clients=client_list), RequestContext(request) )


@csrf_protect
def login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			user = auth.authenticate(
				username=form.cleaned_data['username'],
				password=form.cleaned_data['password'] )
			auth.login(request, user)
			return auth_redirect(request)
	else: form = LoginForm()
	return render_to_response(
		'account/login.html', dict(form=form), RequestContext(request) )


@login_required
def logout(request):
	auth.logout(request)
	return render_to_response(
		'account/logout.html', dict(), RequestContext(request) )


@csrf_protect
def signup(request):
	if request.method == 'POST':
		form = SignupForm(request.POST)
		if form.is_valid():
			user = User.objects.create_user(
				form.cleaned_data['username'],
				form.cleaned_data['email'],
				form.cleaned_data['password1'] )
			user = auth.authenticate(
				username=form.cleaned_data['username'],
				password=form.cleaned_data['password1'] )
			auth.login(request, user)
			return auth_redirect(request)
	else: form = SignupForm()
	return render_to_response(
		'account/signup.html', dict(form=form), RequestContext(request) )
