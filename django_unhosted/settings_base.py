
class Base(object):

	### Make sure to set these

	## Used by Django it lots of places.
	# SECRET_KEY = ...

	## SQL database is used in oauth2app, django.contrib.auth
	##  and to store remoteStorage object paths in django_unhosted.
	# DATABASES = ...

	## MEDIA_ROOT is used by default to store *files* by Django Storage API.
	## All the actual remoteStorage content will go there,
	##  unless either DEFAULT_FILE_STORAGE or UNHOSTED_DAV_STORAGE
	##  is redefined to use another Storage implementation.
	# MEDIA_ROOT = ...
	# MEDIA_URL = ...

	## Used for several js files.
	## Use django.contrib.staticfiles to manage these.
	# STATIC_ROOT = ...
	# STATIC_URL = ...

	## Size of oauth2app model fields.
	## See "Known Issues / OAuth2" section
	##  in README file for reasoning behind these.
	OAUTH2_CLIENT_KEY_LENGTH = 1024
	OAUTH2_SCOPE_LENGTH = 2048

	## Necessary for proper interface styles.
	CRISPY_TEMPLATE_PACK = 'bootstrap'
	# CRISPY_FAIL_SILENTLY = not DEBUG

	## Can be used to disable unnecessary functionality like Sign Up or demo client.
	## Default: 'webfinger', 'oauth2', 'api', 'account', 'demo'
	# UNHOSTED_COMPONENTS = 'webfinger', 'oauth2', 'api', 'account_authonly'

	## Content storage and serving customization.
	## See "Customization / WebDAV" section in README.
	# DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
	# UNHOSTED_DAV_STORAGE = DEFAULT_FILE_STORAGE
	# UNHOSTED_DAV_SENDFILE = False
	# UNHOSTED_DAV_ACCEL = False
	# UNHOSTED_DAV_REDIRECT = False

	## Cache settings for static views (host-meta, webfinger).
	# UNHOSTED_CACHE_TIME = 3600



## Set all the vars from Base mixin class,
##  so that module can be used in DJANGO_SETTINGS_MODULE
import __main__ as mod_self

for k,v in vars(Base).items():
	if not k.isupper() or k.startswith('_'): continue
	setattr(mod_self, k, v)



## Try to import django-configurations, if available.
##  http://django-configurations.readthedocs.org/

try: from configurations import Settings
except ImportError:
	Settings = SettingsBase = SettingsFull = None

else:

	def smart_extend(to, *classes):
		for cls in classes:
			if cls not in to: to += cls,
		return to

	class SettingsBase(Settings, Base):

		## Request context processor is used in auth forms
		##  and external_resources_context is used in demo views.
		TEMPLATE_CONTEXT_PROCESSORS = smart_extend(
			Settings.TEMPLATE_CONTEXT_PROCESSORS,
			'django.core.context_processors.csrf',
			'django.core.context_processors.messages',
			'django.core.context_processors.request',
			'django_unhosted.utils.external_resources_context' )

		## Caches XML templates for host-meta and webfinger requests.
		TEMPLATE_LOADERS = smart_extend(
			Settings.TEMPLATE_LOADERS,
			'django_unhosted.apps.webfinger.xrd_gen.Loader' )

		## CSRF middleware BREAKS WebDAV methods.
		## See "Known Issues / WebDAV" section in README for details.
		MIDDLEWARE_CLASSES = tuple(filter(
			lambda cls: cls != 'django.middleware.csrf.CsrfViewMiddleware',
			Settings.MIDDLEWARE_CLASSES ))

		## Messages middleware is used in interfaces extensively
		MIDDLEWARE_CLASSES = smart_extend(
			MIDDLEWARE_CLASSES,
			'django.contrib.messages.middleware.MessageMiddleware' )


	class SettingsFull(ConfigurationsBase):

		## ConfigurationsBase class should always contain
		##  everything necessary but INSTALLED_APPS.
		## Use that one, if you don't need some of the optional apps here.

		## Technically, "south" is not necessary, unless you need migrations.
		INSTALLED_APPS = smart_extend(
			Settings.INSTALLED_APPS,
			'django.contrib.messages',
			'django_unhosted',
			'oauth2app',
			'crispy_forms',
			'south' )



## Provide some pre-merged definitions (Django-1.4 version!)
##  for import convenience or so that module can be used
##  as a DJANGO_SETTINGS_MODULE

TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
	'django_unhosted.apps.webfinger.xrd_gen.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	'django.contrib.auth.context_processors.auth',
	'django.core.context_processors.debug',
	'django.core.context_processors.i18n',
	'django.core.context_processors.media',
	'django.core.context_processors.static',
	'django.core.context_processors.tz',
	'django.contrib.messages.context_processors.messages',
	'django.core.context_processors.request',
	'django_unhosted.utils.external_resources_context',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
)

INSTALLED_APPS = (
	'django_unhosted',
	'oauth2app',
	'crispy_forms',
	'south',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.admin',
)
