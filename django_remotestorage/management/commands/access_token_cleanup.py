# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import itertools as it, operator as op, functools as ft
from datetime import datetime
from optparse import make_option
from time import time

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import get_default_timezone

from oauth2app.models import Client, AccessToken


class Command(BaseCommand):
	args = '[ username ... ]'
	help = 'Cleanup expired OAuth'\
		' access_tokens (just for username(s), if specified)'
	option_list = BaseCommand.option_list + (
		make_option('-t', '--grace-period',
			type='int', default=0, metavar='seconds',
			help="Don't remove tokens expired"
					' within the last N seconds (default: remove all expired).'
				' Can be negative, to remove tokens which are about to expire.'),
		make_option('-n', '--dry-run', action='store_true',
			help="Don't actually remove any tokens, just show how many are selected"),
	)

	def handle(self, *users, **optz):
		clients = Client.objects
		if users: clients = clients.filter(user__username__in=users)
		tokens = AccessToken.objects.filter(
			pk__in=clients.values_list('accesstoken__pk', flat=True),
			expire__lte=time() - optz['grace_period'] )
		tokens_count = tokens.count()
		if int(optz['verbosity']) > 1:
			tz = get_default_timezone()
			for token in tokens:
				token = ', '.join(it.starmap( '{}={}'.format,
					[ ('id', token.pk),
						('user', token.user.username),
						('client_name', token.client.name),
						('expired', datetime.fromtimestamp(token.expire, tz)) ] ))
				self.stdout.write('Removing token: {}.\n'.format(token))
		if not optz['dry_run']: tokens.delete()
		if int(optz['verbosity']) >= 1:
			self.stdout.write('{} access token(s) removed.\n'.format(tokens_count))
