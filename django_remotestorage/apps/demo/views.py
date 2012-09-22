#-*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext

from oauth2app.models import Client, AccessToken


def storage_client(request):
	ctx = dict()
	if request.user.is_authenticated():
		clients = Client.objects.filter(user=request.user)
		access_tokens = AccessToken.objects.filter(user=request.user)
		access_tokens = access_tokens.select_related()
		ctx['access_tokens'] = access_tokens
		ctx['clients'] = clients
	return render_to_response(
		'demo/client.html', ctx, RequestContext(request) )


def storage_token(request, ext):
	return render_to_response(
		'demo/receive_token.html', dict(), RequestContext(request) )
