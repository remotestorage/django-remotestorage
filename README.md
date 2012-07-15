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

	TEMPLATE_LOADERS = (
		...
		'django_unhosted.apps.webfinger.xrd_gen.Loader',
	)

	INSTALLED_APPS = (
		'django_unhosted',
		'oauth2app',
		'crispy_forms',
		'south',
	...

	CRISPY_TEMPLATE_PACK = 'bootstrap'
	CRISPY_FAIL_SILENTLY = not DEBUG


Customization
--------------------

##### Webfinger

If [webfinger](https://tools.ietf.org/html/draft-jones-appsawg-webfinger-01) and
[host-meta](https://tools.ietf.org/html/draft-hammer-hostmeta-05) requests for
the domain should carry more data than just for remoteStorage, they can be
extended either by replacing webfinger app entirely or adding custom templates
for it.

Webfinger app is using "webfinger/host_meta.{xml,json}" and
"webfinger/webfinger.{xml,json}" templates, provided by
django_unhosted.apps.webfinger.xrd_gen.Loader or generated dynamically (in case
of json, if template provide can't be found).

See example xml templates in
[django_unhosted/templates/webfinger/{host_meta,webfinger}.xml.example]
(https://github.com/mk-fg/django-unhosted/blob/master/django_unhosted/templates/webfinger/).


Known issues
--------------------

##### Webfinger

* No easy support for [signed
	XRD](http://docs.oasis-open.org/xri/xrd/v1.0/xrd-1.0.html#signature), due to
	lack of support in [python-xrd](https://github.com/jcarbaugh/python-xrd/),
	signed *static* xml "templates" (or just files, served from httpd) can be used
	as a workaround if TLS is not an option.

* [Original (PyPI) version](https://github.com/jcarbaugh/python-xrd/) of
	python-xrd can't be used, due to lack of support for custom attributes for
	links (like "auth" and "api"), which are used in remoteStorage protocol atm,
	only [my fork](https://github.com/mk-fg/python-xrd/) with experimental support
	for these.
