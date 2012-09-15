#-*- coding: utf-8 -*-

import itertools as it, operator as op, functools as ft
from os.path import join, dirname
import hashlib

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db import models
from django.core.files.storage import get_storage_class
from django.contrib.auth.models import User

from django_remotestorage.utils import http_date


fs = get_storage_class(getattr(
	settings, 'REMOTESTORAGE_DAV_STORAGE', None ))()


class StoredObjects(models.Manager):

	def user_path(self, user, path):
		try: return self.get_query_set().get(user=user, path=path)
		except ObjectDoesNotExist:
			return self.model(user=user, path=path)


class StoredObject(models.Model):
	objects = StoredObjects()

	def fs_path(self, name):
		return self.data.storage.get_available_name(
				self.data.storage.get_valid_name(
					join(self.user.username, name or self.path) ) )

	user = models.ForeignKey(User)
	path = models.CharField(max_length=2048)
	data = models.FileField( 'Storage API Object',
		upload_to=fs_path, max_length=1024, storage=fs )

	class Meta:
		unique_together = ('user', 'path'),
		app_label = 'django_remotestorage'

	def __unicode__(self):
		return '{}:{}'.format(self.user, self.path)


	_dmeta = _size = _mtime = _etag = None

	def _dmeta_init(self):
		fs_path = self.data.name
		if not fs.exists(fs_path): return
		# OSError's can be raised in the default FileStorage class,
		#  though they shouldn't be with exists() check in place (races?)
		try: self._size = fs.size(fs_path)
		except (NotImplementedError, OSError): pass
		try: self._mtime = fs.modified_time(fs_path)
		except (NotImplementedError, OSError):
			try: self._mtime = fs.created_time(fs_path) # immutable storage?
			except (NotImplementedError, OSError): pass
		else:
			self._etag = hashlib.sha1('{}\0{}'.format(
				http_date(self._mtime), self._size )).hexdigest()

	def _dmeta_get(self, k):
		if not self._dmeta and self.data: self._dmeta_init()
		return getattr(self, '_{}'.format(k))

	size = property(lambda s: s._dmeta_get('size'))
	mtime = property(lambda s: s._dmeta_get('mtime'))
	etag = property(lambda s: s._dmeta_get('etag'))


	@property
	def can_be_created(self):
		'Returns False if object with path == dirname(obj.path) exists.'
		return not self.objects.filter(user=self.user, path=dirname(self.path)).exists()
