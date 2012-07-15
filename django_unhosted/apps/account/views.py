#-*- coding: utf-8 -*-

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from oauth2app.models import Client, AccessRange

from .forms import SignupForm, LoginForm


def login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			user = auth.authenticate(
					username=form.cleaned_data['username'],
					password=form.cleaned_data['password'])
			auth.login(request, user)
			return HttpResponseRedirect('/')
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
				form.cleaned_data['password1'],)
			user = auth.authenticate(
				username=form.cleaned_data['username'],
				password=form.cleaned_data['password1'])
			auth.login(request, user)
			return HttpResponseRedirect('/')
	else: form = SignupForm()
	return render_to_response(
		'account/signup.html', dict(form=form), RequestContext(request) )
