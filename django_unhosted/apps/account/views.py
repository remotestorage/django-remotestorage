#-*- coding: utf-8 -*-

from django.core.urlresolvers import reverse, NoReverseMatch
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from oauth2app.models import Client, AccessRange

from .forms import SignupForm, LoginForm, CreateClientForm, ClientRemoveForm


def auth_redirect():
	try: next_hop = reverse('demo:storage_client')
	except NoReverseMatch: next_hop = reverse('account:clients')
	return HttpResponseRedirect(next_hop)


@login_required
def clients(request):
	if request.method == 'POST':
		form = CreateClientForm(request.POST)
		remove_form = ClientRemoveForm(request.POST)
		if form.is_valid():
			Client.objects.create(
				name=form.cleaned_data['name'],
				user=request.user )
		elif remove_form.is_valid():
			Client.objects.filter(
				id=remove_form.cleaned_data['client_id'],
				user=request.user ).delete()
			form = CreateClientForm()
	else:
		form = CreateClientForm()
	ctx = dict( form=form,
		clients=Client.objects.filter(user=request.user) )
	return render_to_response(
		'account/clients.html', ctx, RequestContext(request) )


def login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			user = auth.authenticate(
				username=form.cleaned_data['username'],
				password=form.cleaned_data['password'] )
			auth.login(request, user)
			return auth_redirect()
	else: form = LoginForm()
	return render_to_response(
		'account/login.html', dict(form=form), RequestContext(request) )


@login_required
def logout(request):
	auth.logout(request)
	return render_to_response(
		'account/logout.html', dict(), RequestContext(request) )


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
			return auth_redirect()
	else: form = SignupForm()
	return render_to_response(
		'account/signup.html', dict(form=form), RequestContext(request) )
