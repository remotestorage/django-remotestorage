#-*- coding: utf-8 -*-

from django.http import HttpResponse

from oauth2app.authenticate import Authenticator, AuthenticationException


# TODO: handle PUT (and other non-GET) requests
def storage(request, acct, path):
	authenticator = Authenticator()
	try: authenticator.validate(request)
	except AuthenticationException:
		return authenticator.error_response(content='Authentication failure.')
	username = authenticator.user.username
	# TODO: serve the actual requested data here
	return HttpResponse(( 'Hi {}, requested'
		' path (acct: {}): {}' ).format(username, acct, path))
