django-unhosted: [Unhosted](http://unhosted.org/) [remoteStorage](http://www.w3.org/community/unhosted/wiki/RemoteStorage) server implementation
--------------------

Under development, not yet ready for general usage.


Deploy
--------------------

(for testing/development only at the moment, hence that compicated)

	git clone https://github.com/mk-fg/django-unhosted
	git clone https://github.com/unhosted/remoteStorage.js
	wget http://twitter.github.com/bootstrap/assets/bootstrap.zip
	wget http://requirejs.org/docs/release/jquery-require/jquery1.7.2-requirejs2.0.4/jquery-require-sample.zip
	unzip jquery-require-sample.zip

	basepath=$(pwd)
	pushd django_unhosted/django_unhosted/static
	unzip $basepath/bootstrap.zip
	cd demo
	ln -s $basepath/remoteStorage.js/src remoteStorage
	ln -s $basepath/jquery-require-sample/webapp/scripts/require-jquery.js .
	popd

settings.py:

	STATIC_ROOT = ...
	STATIC_URL = ...

	TEMPLATE_LOADERS = (
		...
		'django_unhosted.apps.webfinger.xrd_gen.Loader',
	)

	TEMPLATE_CONTEXT_PROCESSORS = (
		...
		'django.core.context_processors.request',
	)

	INSTALLED_APPS = (
		...
		'django_unhosted',
		'oauth2app',
		'crispy_forms',
		'south',
	)

	OAUTH2_CLIENT_KEY_LENGTH = 1024
	OAUTH2_SCOPE_LENGTH = 2048

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

These are implementation-related issues, not the issues with the protocols
themselves (which doesn't imply there's none of the latter, just that it's not a
place for them).

##### Webfinger

* No easy support for [signed
	XRD](http://docs.oasis-open.org/xri/xrd/v1.0/xrd-1.0.html#signature) at the
	moment. Signed *static* xml "templates" (or just files, served from httpd) can
	be used as a workaround if TLS is not an option.

##### OAuth2

* Stored object path (think "public/myphoto.jpg") is used as OAuth2 "scope" by
	remoteStorage.
	oauth2app basically keeps a single table of these (treating them as a finite
	up-front set of capabilities).

	Problems here:

	* oauth2app stores "scope" as a 255-char key, while paths can potentially be
		longer.
		Upstream [pull request](https://github.com/hiidef/oauth2app/pull/31) to
		specify field length was merged (as of 19.07.2012), so use any newer version
		with the large-enough OAUTH2_SCOPE_LENGTH parameter in settings.py (it
		[doesn't really affect
		performance](http://www.depesz.com/2010/03/02/charx-vs-varcharx-vs-varchar-vs-text/)
		of modern databases, just making your life a bit harder).

	* Currently, oauth2app checks existance of AccessRange (scope) models as they
		are specified in the request, even though access to some of them might not
		be authorized by user, requiring temporary creation of this clutter.
		Upstream pull request: https://github.com/hiidef/oauth2app/pull/32

	* There's some extra code/db overhead involved in maintaining the (pointless
		in this case) table.

	All these are currently addressed in [my fork of
	oauth2app](https://github.com/mk-fg/oauth2app/), but project should work with
	the original oauth2app, it'd just involve some limitations (like 255-char
	paths) and extra work (creation of AccessRange models to pass validation).

* remoteStorage.js 0.6.9 ("stable" version at the moment) has a [known
	issue](http://www.w3.org/community/unhosted/wiki/RemoteStorage-2011.10#OAuth)
	of passing legacy "path1,path2" as a "scope", further complicating things for
	oauth2app (which would think that it's a single capability, as per spec) if
	several paths are passed.

	Workaround used is to detect the old format by lack of ":rw" suffixes and
	update "scope" in the address by issuing a redirect.

	Note that since paths may contain commas, "path1,path2" can be ambiguous
	(because of this issue) and can be treated either as "path1:rw" and "path2:rw"
	or "path1,path2:rw".
	Current implementation chooses the former interpretation if there's no
	colon-delimeted suffix.

* remoteStorage.js 0.6.9 ("stable" version at the moment) uses hostname of the
	app site as OAuth2 client_id, which, in oauth2app corresponds to the "key"
	field, which is just 32-chars long by default, which might not be enough for
	some hostnames, but can (and *should*!) be configured by
	OAUTH2_CLIENT_KEY_LENGTH parameter in django project's settings.py.
	Remember to do that *before* syncdb, or update the table column later.

	Possible workaround might be to use hashes as the client_id's internally and
	redirect remoteStorage requests with "client_id=hostname.com" to something
	like "client_id=sha1:bbc21f0ccb5dfbf81f5043d78aa".

	I can't see why client_id should be random or non-meaningful at the moment, if
	there's a reason for that, please report an issue, some automatic migration to
	hashes can probably be deployed at any time.


TODO
--------------------

* Client (app, requesting access) deception - returning fake "authorized scopes"
	to it, but storing them somewhere to deny the actual access or provide random
	garbage instead.

	Idea is to prevent situation, common on twitter and android platforms, when
	apps always ask for everything and user is presented with "all or nothing"
	choice.
