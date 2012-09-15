django-remotestorage
--------------------

[Unhosted](http://unhosted.org)
[remoteStorage](http://remotestoragejs.com) server
implementation

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

Package (and django app) was called django-unhosted in the past and was
eventually renamed.  If you're using django-unhosted package, please read the
[notes on
migration](https://github.com/RemoteStorage/django-remotestorage#migration-from-django-unhosted)
under
[Installation](https://github.com/RemoteStorage/django-remotestorage#installation)
section.



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
storage-server implementation [can be found
here](http://crypto.junod.info/2012/05/24/owncloud-4-0-and-encryption/),
learn the lession there.



Installation
--------------------


### Requirements

* [Python 2.7 (not 3.X)](http://python.org/)

* [Django](http://djangoproject.com)
* [Django OAuth 2.0 Server App (oauth2app)](http://hiidef.github.com/oauth2app/)
* (optional, recommended) [South](http://south.aeracode.org) - for automated
	database schema updates

oauth2app is [not on PyPI](https://github.com/hiidef/oauth2app/issues/7) at the
moment, but pip can install it from github directly.

Various interfaces of the app use some external resources, like [Twitter
Bootstrap](http://twitter.github.com/bootstrap/) CSS file (served from
bootstrapcdn.com) and
[remoteStorage.js](https://github.com/RemoteStorage/remoteStorage.js), which can be
served - and **should be**, if you're using https for interfaces - from local
URLs, if available in STATIC_ROOT.  See "Customization / Interfaces" for
details.


### Migration from django-unhosted

Package was called django-unhosted in the past, but it was decided to rename it
before it was way too late.

Unfortunately, there's no easy way to rename django app and python package,
especially if it's undesirable to keep older package names around for eternity,
so some manual steps have to be taken in order to migrate to the new
(django-remotestorage) app/package.

* Uninstall django-unhosted python package (either through `pip uninstall
	django-unhosted`, OS tools, or remove module path manually).

* Rename all database tables with "django_unhosted" in name to be starting with
	"django_remotestorage" instead.  Lots of easy-to-use GUI tools (such as
	[pgadmin](http://www.pgadmin.org/),
	[phpPgAdmin](http://phppgadmin.sourceforge.net/),
	[phpMyAdmin](http://www.phpmyadmin.net/),
	[phpSQLiteAdmin](http://phpsqliteadmin.sourceforge.net/), etc) or native CLI
	interfaces (`sqlite3 /path/to/db.sqlite`, `psql`, `mysql`, etc) can be used
	for that.

* Update settings.py and urlconf to import stuff from "django_remotestorage"
	module instead of "django_unhosted".
	Replace all "UNHOSTED_" in variable names to "REMOTESTORAGE_", if used in
	settings.py.

* If you have a custom urlconf and/or templates, replace references to
	"unhosted" namespace with "remotestorage".

It should fairly straightforward, but feel free to open Issue or [contact
developers](https://github.com/RemoteStorage/django-remotestorage#contacts--support)
if the described process doesn't work for you.


### Deployment / configuration

Django apps are deployed as a part of "django project", which is - at it's
minimum - just a few [configuration
files](https://docs.djangoproject.com/en/dev/topics/settings/), specifying which
database to use, and which apps should handle which URLs.

##### TL;DR

Simple installation/setup from scratch may look like this.

Install the app itself (or not, it can be just checked-out into a project dir):

	pip install django-remotestorage

...or, to install directly from git master branch:

	pip install 'git+https://github.com/RemoteStorage/django-remotestorage.git#egg=django-remotestorage'

...or you can do it manually:

	git clone https://github.com/RemoteStorage/django-remotestorage.git
	cd django-remotestorage
	python setup.py install
	pip install -r requirements.txt # or download/install each by hand as well

"pip" tool, mentioned above, should usually come with OS of choice, otherwise
see [pip installation docs](http://www.pip-installer.org/en/latest/installing.html).
Don't use "easy_install" for anything except installing the pip itself.

Install oauth2app in a similar fashion:

	pip install 'git+https://github.com/hiidef/oauth2app.git#egg=oauth2app'

Then create and configure a django project:

	cd
	django-admin.py startproject myproject
	cd myproject

	# Update settings.py (sqlite3 is used as db here) and urls.py
	sed -i \
		-e 's/'\''ENGINE'\''.*/"ENGINE": "django.db.backends.sqlite3",/' \
		-e 's/'\''NAME'\''.*/"NAME": "db.sqlite",/' \
		-e 's/STATIC_ROOT *=/STATIC_ROOT="./static"/' \
		myproject/settings.py
	echo -e >>myproject/settings.py \
		'from django_remotestorage.settings_base import update_settings' \
		'\nupdate_settings(__name__)'
	sed -i \
		-e '1afrom django_remotestorage.urls import remotestorage_patterns' \
		-e 's/# Examples:.*/("", include(remotestorage_patterns)),\n\n\0/' \
		myproject/urls.py

	# Create database schema and link app static files to STATIC_ROOT
	./manage.py syncdb --noinput
	./manage.py migrate django_remotestorage
	./manage.py collectstatic --noinput --link

	# Run simple dev server
	./manage.py runserver

(since webfinger protocol **requires** some sort of XRD authentication, like
https, it *won't work* properly on such a simple setup)

More detailed explaination of configuration process follows.

##### Django project configuration

Main idea is that two config files (in django project) need to be updated -
settings.py and urls.py.

There are several ways to update django settings.py to use the app:

* If it's the only app in a django project and there's no custom settings.py
	already, options from
	[django_remotestorage.settings_base](https://github.com/RemoteStorage/django-remotestorage/blob/master/django_remotestorage/settings_base.py)
	module can be imported into it directly.

	To do that, add the following lines to the *end* of
	"{your_app_name}/settings.py" (or wherever
	[DJANGO_SETTINGS_MODULE](https://docs.djangoproject.com/en/dev/topics/settings/#designating-the-settings)
	is used) file:

		from django_remotestorage.settings_base import *

	That will import all the options there (bare minimum that has to be changed)
	over those defined above in the original file.

	Note that list of overidden options include INSTALLED_APPS, MIDDLEWARE_CLASSES
	and such, which are not only often customized, but are usually specific to the
	django version installed, so you may alternatively insert that import line at
	the *beginning* of the settings.py, so everything defined after it will
	override the imported options.

* If there's already some custom settings.py file available, there's
	django_remotestorage.settings_base.update_settings helper function available to
	update configuration without blindly overriding any options.

	It can be used at the end of settings.py file like this:

		from django_remotestorage.settings_base import update_settings
		update_settings(__name__)

	Full list of changes it'll make can be found in "updates" dict at the
	beginning of
	[django_remotestorage.settings_base](https://github.com/RemoteStorage/django-remotestorage/blob/master/django_remotestorage/settings_base.py)
	module.

	"update_settings" function also takes an optional "only" and "ignore" keywords
	(expecting an iterable of option names), which can be used to control which
	parameters should be updated or explicitly left untouched.

	This should be more safe, flexible and future-proof way of merging necessary
	option updates with existing (site-specific) configuration.

* Update the file by hand.

	Default values for the most settings can be found in [django
	documentation](https://docs.djangoproject.com/en/dev/ref/settings/).

	For the class-listing type options, duplicate values may be omitted.
	Note that order of MIDDLEWARE_CLASSES is significant.

		OAUTH2_CLIENT_KEY_LENGTH = 1024
		OAUTH2_SCOPE_LENGTH = 2048

		TEMPLATE_CONTEXT_PROCESSORS = (
			...whatever is already there...
			'django.core.context_processors.csrf',
			'django.core.context_processors.request',
			'django.contrib.messages.context_processors.messages',
			'django_remotestorage.utils.external_resources_context',
		)

		TEMPLATE_LOADERS = (
			...whatever is already there...
			'django_remotestorage.apps.webfinger.xrd_gen.Loader',
		)

		MIDDLEWARE_CLASSES = (
			...whatever is already there...
			<remove 'django.middleware.csrf.CsrfViewMiddleware', if it's there>
			...whatever is already there, except for ConditionalGet / FetchFromCache...
			'django.contrib.messages.middleware.MessageMiddleware',
			...ConditionalGetMiddleware and FetchFromCacheMiddleware (and such), if used...
		)

		INSTALLED_APPS = (
			...whatever is already there...
			'django.contrib.messages',
			'django_remotestorage',
			'oauth2app',
			'south',
		)

	"south" should be omitted from INSTALLED_APPS, if not used.

In any case, if you've just created django project (with "django-admin.py
startproject" or whatever), make sure to look through it's settings.py file and
edit at least DATABASES, MEDIA\_\* and STATIC\_\* options.  You might also want
to set other (optonal) settings there - TIME_ZONE, ADMINS, LOGGING, etc.

As for urls.py, just add the following line to url patterns (importing
remotestorage_patterns from django_remotestorage.urls module beforehand):

	('', include(remotestorage_patterns)),

So it'd look like this:

	...
	from django_remotestorage.urls import remotestorage_patterns
	...
	urlpatterns = patterns('',
		('', include(remotestorage_patterns)),
	...

That will add all the app urls to the root-path (for the complete list of these
paths, see [the module
code](https://github.com/RemoteStorage/django-remotestorage/blob/master/django_remotestorage/__init__.py)).
To selectively disable some of the components, see "Customization" section.

##### Database schema

Then the usual drill is to create the necessary database schema for the app (if
you get "Settings cannot be imported" error, make sure you run that from the
same path as "settings.py" file):

	django-admin.py syncdb

If [South app](http://south.aeracode.org) is installed (and specified in the
INSTALLED_APPS), you should also use it's migrations to create tables for which
they are available:

	django-admin.py migrate django_remotestorage

That command can (and should) also be run after django-remotestorage app updates to
apply any possible changes to db schema.

#### Running

Pretty much anything that supports
[WSGI](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) protocol can
be used with django - there's nothing app-specific here, just plain django,
which is (usually) used as a backend with some httpd via wsgi.

See django docs on [deployment
process](https://docs.djangoproject.com/en/dev/howto/deployment/) for generic
instructions.



Customization
--------------------


### Components

The app consists of several independent components (sub-apps, bound to url paths
via
[django_remotestorage.urls](https://github.com/RemoteStorage/django-remotestorage/blob/master/django_remotestorage/urls.py)):

* Webfinger (name: webfinger, URL: {include_prefix}/.well-known/host-meta,
	{include_prefix}/webfinger; see
	[django_remotestorage.apps.webfinger.urls](https://github.com/RemoteStorage/django-remotestorage/blob/master/django_remotestorage/apps/webfinger/urls.py),
	there are similar urlconf-files for other subapps).

* OAuth2 (name: oauth2, URL: {include_prefix}/oauth2).

* Storage API (name: api, URL: {include_prefix}/api).

* Account/client management (name: "account", URL: {include_prefix}/account).
	Can also be enabled partially with the following names: "account_auth"
	(login/logout forms/links), "account_auth_management" (signup form),
	"account_client_management" (client/app access management interface for
	logged-in users).
	"account" is an alias for all of these interfaces.

* Demo client (name: demo, URL: {include_prefix}/)

Some components provide links to each other (for example, webfinger provides
links to OAuth2 and API in served XRD/JSON data), resolved as
"remotestorage:{app}:{view_name}", so you can rebind these apps to any URLs, as long
as you provide the same namespace/view_name for [django "reverse()"
function](https://docs.djangoproject.com/en/dev/topics/http/urls/#reverse) and "url"
template tags.

When including "django_remotestorage.urls.remotestorage_patterns" directly (not the
urlconfs from individual components), "REMOTESTORAGE_COMPONENTS" settings.py option
can be set to an iterable of components which should be enabled, for example:

	REMOTESTORAGE_COMPONENTS = 'webfinger', 'oauth2', 'api'

...will enable just Storage API, OAuth2 and Webfinger subapps - bare minimum for
functional remoteStorage node.
Unless some other means to authenticate django user (like
[django.contrib.auth.views.login](https://docs.djangoproject.com/en/dev/topics/auth/#django.contrib.auth.views.login)
or django.contrib.admin) are enabled, it might also be necessary to enable
"account_auth" interface to pass OAuth2 authorization.

If "account" (or it's parts) and "demo" apps are omitted from urlconf entirely
(if not needed), there won't be any links to them in OAuth2 access confirmation
interface.
Their interface pages and functionality won't be accessible.

"api" and "oauth2" sub-apps are not linked to any other components either, so
may be used separately from others and from each other as well (e.g. if
authorization server and storage are on a different hosts), but they must share
a database in order for api to be able to validate auth tokens.


### OAuth2

It's highly recommended to raise database field lengths (using [oauth2app
settings](http://hiidef.github.com/oauth2app/settings.html)) *before* running
syncdb for the first time:

* OAUTH2_CLIENT_KEY_LENGTH = 1024 (default: 30)
* OAUTH2_SCOPE_LENGTH = 2048 (default: 255)

See "Known Issues / OAuth2" section for more detailed explaination on why it
should be done.

Another important tunable is OAUTH2_ACCESS_TOKEN_EXPIRATION (default: 3600 = 1
hour), which - at least with remoteStorage.js 0.6.9 ("stable" at the moment of
writing) - essentially sets a maximal interval between the need to visit OAuth2
interface and get new access token, because remoteStorage.js doesn't seem to be
able to refresh these.


### Webfinger

If [webfinger](https://tools.ietf.org/html/draft-jones-appsawg-webfinger-01) and
[host-meta](https://tools.ietf.org/html/draft-hammer-hostmeta-05) requests for
the domain should carry more data than just for remoteStorage, they can be
extended either by replacing webfinger app entirely or adding custom templates
for it.

Webfinger app is using "webfinger/host_meta.{xml,json}" and
"webfinger/webfinger.{xml,json}" templates, provided by
django_remotestorage.apps.webfinger.xrd_gen.Loader or generated dynamically (in case
of json, if template provide can't be found).

See example xml templates in
[django_remotestorage/templates/webfinger/{host_meta,webfinger}.xml.example](https://github.com/RemoteStorage/django-remotestorage/blob/master/django_remotestorage/templates/webfinger/).


### Storage / WebDAV

Provided remoteStorage is backed by (configurable) [Django Storage
API](https://docs.djangoproject.com/en/dev/topics/files/).

By default,
[DEFAULT_FILE_STORAGE](https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-DEFAULT_FILE_STORAGE)
storage class is used.
Different storage class can be specified by "REMOTESTORAGE_DAV_STORAGE" parameter
(passed to [get_storage_class](https://docs.djangoproject.com/en/dev/ref/files/storage/#django.core.files.storage.get_storage_class)).

Examples of Storage API implementation might include:

* [django-storages](http://django-storages.readthedocs.org/en/latest/index.html)
	(S3, CouchDB, SQL, FTP, MongoDB, CloudFiles, etc)
* [django-dropbox](https://github.com/andres-torres-marroquin/django-dropbox)
	(Dropbox)
* [django-riak-engine](https://github.com/oubiwann/django-riak-engine) (Riak)
* [django-tahoestorage](https://github.com/thraxil/django-tahoestorage)
	(Tahoe-LAFS)

But basically there's a client for pretty much any data storage technology -
just google it, install and set REMOTESTORAGE_DAV_STORAGE (or DEFAULT_FILE_STORAGE)
to it.

Default Storage (FileStorage) parameters can be configured with MEDIA_URL and
MEDIA_ROOT [settings](https://docs.djangoproject.com/en/dev/ref/settings/), see
["Managing files"](https://docs.djangoproject.com/en/dev/topics/files/) django
docs section for details.

There are also some optimization parameters:

* REMOTESTORAGE_DAV_SENDFILE (bool, default: False)

	Pass Storage.path (if supported by backend) to httpd frontend via "X-Sendfile"
	header instead of the actual contents upon request, so that response can be
	served by frontend daemon directly without backend app involved.

* REMOTESTORAGE_DAV_ACCEL (string, default: None)

	Return empty HttpResponse with "X-Accel-Redirect" header set to specified
	prefix (can be an empty string) plus the requested path, so the actual
	response can be served by [apache
	mod_accel](http://sysoev.ru/en/apache_modules.html).

* REMOTESTORAGE_DAV_REDIRECT (bool, default: False)

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
See [django_remotestorage.utils.external_resources_context](https://github.com/RemoteStorage/django-remotestorage/blob/master/django_remotestorage/utils.py)
context processor for details.

Take special care to make resources local if you serve these interfaces over
https - there's just no security gain if MitM can place any javascript (loaded
over plain http) to a page.

Note that any/all of the UIs can be disabled, if they're not needed, just use
REMOTESTORAGE_COMPONENTS option (described in "Components" section) or don't include
them in the urlconf, cherry-picking whichever ones are actually needed.

One common case of customization is the need to put whole app into some subpath
("/remotestorage" in the example) can be addressed by putting this into the project's
root urls.py:

	from django.conf.urls import patterns, include, url

	from django_remotestorage.apps.webfinger.urls import host_meta_patterns
	from django_remotestorage.urls import remotestorage_patterns

	urlpatterns = patterns('',
		url(r'', include(host_meta_patterns)),
		url(r'^remotestorage/', include(remotestorage_patterns)),
	)

That way, demo client will be available at "/remotestorage" url and all the links
will include that prefix (for example authorization link from webfinger will
point to "/remotestorage/oauth2/authorize").

Make sure, however, that host_meta view of webfinger app is [available at a
well-known url](https://tools.ietf.org/html/draft-jones-appsawg-webfinger-04#section-3.1)
"/.well-known/host-meta", hence the "host_meta_patterns" special-case link from
root.



Commands
--------------------

### access_token_cleanup [options] [ username ... ]

Remove expired OAuth access tokens (just for username(s), if specified) from the
database.

Can be occasionally run from cron (use --verbosity=0 to supress activity
reports) to keep token number from growing indefinitely, removing non-refreshed
or about-to-expire (with negative --grace-period) ones.

Usage example:

	% ./manage.py access_token_cleanup -v2 -n -t 3600 test
	Removing token: id=1, user=test, client_name=localhost, expired=2012-07-31 03:24:30+06:00.
	1 access token(s) removed.



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

	* oauth2app stores "scope" as a 255-char key, while paths / collection_names
		can potentially be longer.
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

* oauth2app is [not on PyPI](https://github.com/hiidef/oauth2app/issues/7) at
	the moment, but pip can install it from github directly.

### WebDAV

* CSRF middleware
	([django.middleware.csrf.CsrfViewMiddleware](https://docs.djangoproject.com/en/dev/ref/contrib/csrf/))
	must be disabled, because remoteStorage.js doesn't pass django csrf tokens
	along with PUT (and similar) requests.
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
	Example would be to add a hook to
	[post-save django signal](https://docs.djangoproject.com/en/dev/ref/models/instances/#what-happens-when-you-save),
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

* Add ability to inspect stored/accessed resources to the client management
	interface.


Contacts / Support
--------------------

Feel free to drop by to #unhosted or #remotestorage channels on [freenode
IRC](http://freenode.net), you can always find authors and people (developers
included) willing to help understand, setup and resolve any issues there.

Mailing lists, twitter and other channels of indirect communication can also be
found on [Unhosted movement site](http://unhosted.org/).

And of course, open Issues for [github
repository](https://github.com/RemoteStorage/django-remotestorage).
