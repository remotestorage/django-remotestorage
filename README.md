django-unhosted: [Unhosted](http://unhosted.org/) [remoteStorage](http://www.w3.org/community/unhosted/wiki/RemoteStorage) server implementation
--------------------

This app is a server (storage) implementation for "stable" remoteStorage API
version, specified here:

	http://www.w3.org/community/unhosted/wiki/RemoteStorage-2011.10

Some parts of it (especially webfinger, oauth2, since I've used newer specs that
were available at the time) *might* be compatible with newer ("experimental")
API:

	https://www.w3.org/community/rww/wiki/read-write-web-00#simple
	http://www.w3.org/community/unhosted/wiki/Pds

But since remoteStorage.js 0.7.0 for experimental API is still under heavy
development, I haven't tested whether it works with current implementation.


remoteStorage
--------------------

Idea is that you can have storage account (with whatever policies and
authentication) on host1 and some webapp (say, some visual editor, think MS
Word) on host2.

To edit document in a webapp, generally host2 would have to implement some sort
of user registration, storage (like docs.google.com) for edited docs, etc.

With remoteStorage, this storage don't have to be on host2, so you don't have to
implement some complex policies and authenticated storage there to launch a
full-featured webapp - it can open and save docs to any remote host which
supports the protocol (which is basically GET/PUT from WebDAV with OAuth2 on
top).

host1 can be your VPS, client machine itself (especially easy with direct IPv6,
or IPv4 provided via some service like [pagekite](https://pagekite.net/)), some
reliable cloud provider or whatever.

To fully understand how it all works, I recommend looking at OAuth2, WebDAV,
CORS and Webfinger, which are basically all the technologies used to implement
the protocol.

This django app fully implements web-facing storage for host1, complete with
user registration forms (optional, users can be added by other django apps or
via django admin interface otherwise), client access management interfaces and a
simple demo client.


Security
--------------------

Since applicaton is a public-internet-facing interface to your (possibly
important) data and I'm in no way security expert or specialist, I recommend to
pentest or validate the code before storing any sensitive data in it.

Data loss or corruption is much easier to prevent (and backups go a long way
here, btw) than security exploits, so, again, please look at the code yourself
and find issues there which I have a blind spot (not to mention lack of skills)
for, thus won't be able to find on my own.

Example of *obvious* (to an outsider analysis) security flaws in another
storage-server implementation [can be found here]
(http://crypto.junod.info/2012/05/24/owncloud-4-0-and-encryption/), learn the
lession there.


Installation
--------------------

### Requirements

* [Python 2.7 (not 3.X)](http://python.org/)

* [Django](http://djangoproject.com)
* [Django OAuth 2.0 Server App (oauth2app)](http://hiidef.github.com/oauth2app/)
* [django-crispy-forms](http://django-crispy-forms.readthedocs.org/)
* (optinal, recommended) [South](http://south.aeracode.org) - for automated
	database schema updates

Note that various interfaces of the app use some external resources, like
[Twitter Bootstrap] (http://twitter.github.com/bootstrap/) CSS file (served from
bootstrapcdn.com) and [remoteStorage.js]
(https://github.com/unhosted/remoteStorage.js), which can be served from local
URLs, if available in STATIC_ROOT.
See "Customization / Interfaces" for details.

### Deployment / configuration

Django apps are deployed as a part of "django project", which is - at it's
minimum - just a few [configuration files]
(https://docs.djangoproject.com/en/dev/topics/settings/), specifying which
database to use, and which apps should handle which URLs.

##### TL;DR

Simple installation/setup may look like this:

	# Install the app itself (or not, it can be just checked-out into a project dir)
	git clone https://github.com/mk-fg/django-unhosted.git
	cd django-unhosted
	python setup.py install

	# Install all the needed deps
	pip install -r requirements.txt

	# Create django project
	cd
	django-admin.py startproject myproject
	cd myproject

	# Update settings.py (sqlite3 is used as db here) and urls.py
	sed -i\
		-e 's/'\''ENGINE'\''.*/"ENGINE": "django.db.backends.sqlite3",/'\
		-e 's/'\''NAME'\''.*/"NAME": "db.sqlite",/'\
		-e 's/STATIC_ROOT *=/STATIC_ROOT="./static"/'\
		myproject/settings.py
	echo 'from django_unhosted.settings_base import *' >> myproject/settings.py
	sed -i 's/# Examples:.*/("", include("django_unhosted.urls")),\n\n\0/' myproject/urls.py

	# Create database schema and link app static files to STATIC_ROOT
	./manage.py syncdb --noinput
	./manage.py migrate django_unhosted
	./manage.py collectstatic --noinput --link

	# Run simple dev server
	./manage.py runserver

(since webfinger protocol **requires** some sort of XRD authentication, like
https, it *won't work* properly on such a simple setup)

##### Django project configuration

Main idea is that two config files (in django project) need to be updated -
settings.py and urls.py.

There are several ways to update django settings.py to use the app:

* If it's the only app in a django project, so you don't have some custom
	settings.py already, you can use provided [settings_base.py file]
	(https://github.com/mk-fg/django-unhosted/blob/master/settings_base.py)
	directly.

	Rename it to settings.py and put it into project root (or wherever
	[DJANGO_SETTINGS_MODULE]
	(https://docs.djangoproject.com/en/dev/topics/settings/#designating-the-settings)
	is pointing), but make sure to look through it's settings and set at least
	SECRET\_KEY, DATABASES, MEDIA\_\* and STATIC\_\*.

	These are not the only ones that generally shouldn't be left to django, so I
	highly recommend to review at least basic [django (app-agnostic) settings]
	(https://docs.djangoproject.com/en/dev/topics/settings/) (and also set stuff
	like TIME_ZONE, ADMINS, LOGGING, etc).

* If there's already some custom settings.py file available (or it can be
	created along with the project by django-admin.py), add this line somewhere at
	the bottom of it: `from django_unhosted.settings_base import *`

	That will import all the options defined there (bare minimum that has to be
	changed) over your settings.

	Note that list of overidden options include INSTALLED_APPS, MIDDLEWARE_CLASSES
	and such, which are not only often customized, but are usually specific to the
	django version installed, so you can insert that import line at the
	*beginning* of the settings.py, so everything defined after it will override
	the options in the example.

	And you can always just copy-paste whatever necessary by hand, which is
	basically 3-10 lines.

* If you have great [django-configurations]
	(http://django-configurations.readthedocs.org/) module installed, you can use
	django_unhosted.settings_base.SettingsBase or SettingsFull classes to
	dynamically extend/filter stuff like MIDDLEWARE_CLASSES and
	TEMPLATE_CONTEXT_PROCESSORS.

	SettingsFull class only differs from SettingsBase in that it also extends
	INSTALLED_APPS with all the required (incl. django_unhosted itself) and
	optional apps.

	This should be the most DRY, flexible and correct way to merge settings.

Also make sure that django.contrib.messages app is installed and it's components
are added to MIDDLEWARE_CLASSES and TEMPLATE_CONTEXT_PROCESSORS ([as per docs]
(https://docs.djangoproject.com/en/dev/ref/contrib/messages/)).
It is installed by default in newer django (1.4, I think), but can be disabled
for older projects.

As for urls.py, just add the following line to the list of patterns:

	('', include('django_unhosted.urls')),

(that'd add all the app urls to the root-path, for the complete list of these
paths, see [django_unhosted.urls]
(https://github.com/mk-fg/django-unhosted/blob/master/django_unhosted/urls.py))

##### Database schema

Then the usual drill is to create the necessary database schema for the app (if
you get "Settings cannot be imported" error, make sure you run that from the
same path as "settings.py" file):

	django-admin.py syncdb

If [South app](http://south.aeracode.org) is installed (and specified in the
INSTALLED_APPS), you should also use it's migrations to create tables for which
they're available:

	django-admin.py migrate django_unhosted

Note that `django-admin.py migrate django_unhosted` can (and should) be run
after django-unhosted app updates to apply any possible changes to db schema.

#### Running

Pretty much anything that supports [WSGI]
(https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) protocol can be
used with django - there's nothing app-specific here, just plain django, which
is (usually) used as a backend with some httpd via wsgi.

See django docs on [deployment process]
(https://docs.djangoproject.com/en/dev/howto/deployment/) for generic
instructions.


Customization
--------------------

### OAuth2

It's highly recommended to raise database field lengths (using [oauth2app
settings](http://hiidef.github.com/oauth2app/settings.html)) *before* running
syncdb for the first time:

* "OAUTH2_CLIENT_KEY_LENGTH = 1024" (default: 30)
* "OAUTH2_SCOPE_LENGTH = 2048"  (default: 255)

See "Known Issues / OAuth2" section for more detailed explaination on why it
should be done.

### Webfinger

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

"UNHOSTED_CACHE_TIME" option can be used along with django cache subsystem to
configure (cache) timeout for "host-meta" and "webfinger" responses (vary per
GET query string, of course).

### WebDAV

Provided remoteStorage is backed by (configurable) [Django Storage
API](https://docs.djangoproject.com/en/dev/topics/files/).

By default, [DEFAULT_FILE_STORAGE]
(https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-DEFAULT_FILE_STORAGE)
storage class is used.
Different storage class can be specified by "UNHOSTED_DAV_STORAGE" parameter
(passed to [get_storage_class]
(https://docs.djangoproject.com/en/dev/ref/files/storage/#django.core.files.storage.get_storage_class)).

Django Storage API parameters can usually be configured with MEDIA_URL and
MEDIA_ROOT [settings](https://docs.djangoproject.com/en/dev/ref/settings/), see
["Managing files"](https://docs.djangoproject.com/en/dev/topics/files/) django
docs section for details.

There are also some optimization parameters:

* UNHOSTED_DAV_SENDFILE (bool, default: False)

	Pass Storage.path to httpd frontend via "X-Sendfile" header instead of the
	actual contents upon request, so that response can be served by frontend
	daemon directly without backend app involved.

* UNHOSTED_DAV_ACCEL (string, default: None)

	Return empty HttpResponse with "X-Accel-Redirect" header set to specified
	prefix (can be an empty string) plus the requested path, so the actual
	response can be served by [apache
	mod_accel](http://sysoev.ru/en/apache_modules.html).

* UNHOSTED_DAV_REDIRECT (bool, default: False)

	Return redirect to MEDIA_URL (produced by Storage.url method).
	Used only if MEDIA_URL is set to non-empty string.

	Serve these urls only after checking oauth2app-generated bearer tokens in http
	"Authorization" header either with django (or custom python code) or some
	smart httpd.

	**Do not** configure httpd to serve paths from MEDIA_URL without
	authorization, because everyone will be able to bypass OAuth2 and gain access
	to anything in remoteStorage just by guessing file paths or getting/reusing
	them from js, which is really easy to exploit.

### Interfaces

Mostly usual drill - put your own templates to loaders, specified in settings.py.

External resources that are served on these pages can be put to STATIC_ROOT to
be served by local httpd instead.
See "django_unhosted.utils.external_resources_context" context processor for
details.

Note that any/all of the UIs can (and actually should) be disabled, if they're
not needed, just don't include them in the urlconf, cherry-picking whichever
ones are actually needed.

For example, to leave only API, OAuth2 and Webfinger enabled (no user
registration/management interface, no demo client):

	urlpatterns = patterns( '',
		...
		url(r'', include('django_unhosted.apps.webfinger.urls', namespace='webfinger')),
		url(r'^oauth2/', include('django_unhosted.apps.oauth2.urls' namespace='oauth2')),
		url(r'^api/', include('django_unhosted.apps.api.urls', namespace='api')),
	)

Remember to include namespace names (same as the subapp names), as they're used
in the reverse() calls and template tags.
You can use django_unhosted.utils.autons_include() in place of include() helper
to infer these from subapp names automagically.


Known issues
--------------------

These are implementation-related issues, not the issues with the protocols
themselves (which doesn't imply there's none of the latter, just that it's not a
place for them).

### Webfinger

* No easy support for [signed
	XRD](http://docs.oasis-open.org/xri/xrd/v1.0/xrd-1.0.html#signature) at the
	moment. Signed *static* xml "templates" (or just files, served from httpd) can
	be used as a workaround if TLS is not an option.

### OAuth2

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

### WebDAV

* CSRF middleware ([django.middleware.csrf.CsrfViewMiddleware]
	(https://docs.djangoproject.com/en/dev/ref/contrib/csrf/)) must be disabled,
	because remoteStorage.js doesn't pass django csrf tokens along with PUT (and
	similar) requests.
	It's selectively enabled via decorator for app forms though.

* Data is currently stored in the Django Storage, while path metadata is stored
	through the Django Database API, which introduces two points of failure (and
	the possibility of sync loss between the two), because one data is useless
	without the other.

	There don't seem to be any easy way around it - storing path data in Storage
	keys won't work with any driver, pushing that to the content won't work when
	this content will be served by anything but python (say, httpd) and storing
	files in a db only works well for relatively small files.

	So make sure to backup db as well as the actual storage, or write some
	storage-specific kludge to store metadata there as well.
	Example would be to add a hook to [post-save django signal]
	(https://docs.djangoproject.com/en/dev/ref/models/instances/#what-happens-when-you-save),
	which would get storage path from StorageObject.data.name and store some
	"{name}.meta" file alongside with serialized model data.


TODO
--------------------

* Client (app, requesting access) deception - returning fake "authorized scopes"
	to it, but storing them somewhere to deny the actual access or provide random
	garbage instead.

	Idea is to prevent situation, common on twitter and android platforms, when
	apps always ask for everything and user is presented with "all or nothing"
	choice.

* Client (app which has access to user's storage) management interface with the
	ability to easily revoke access and maybe inspect stored/accessed resources.
