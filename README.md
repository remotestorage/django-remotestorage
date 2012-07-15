django-unhosted: unhosted remoteStorage server implementation as a django app
--------------------

Under development.


Deploy
--------------------

	cd django_unhosted/static
	unzip bootstrap.zip

settings.py:

	STATIC_ROOT = ...
	STATIC_URL = ...

	INSTALLED_APPS = (
		'django_unhosted',
		'oauth2app',
		'crispy_forms',
		'south',
	...

	CRISPY_TEMPLATE_PACK = 'bootstrap'
	CRISPY_FAIL_SILENTLY = not DEBUG
