#!/usr/bin/env python

from setuptools import setup, find_packages
import os

from django_remotestorage import __version__

pkg_root = os.path.dirname(__file__)

# Error-handling here is to allow package to be built w/o README included
try: readme = open(os.path.join(pkg_root, 'README.txt')).read()
except IOError: readme = ''

setup(

	name = 'django-remotestorage',
	version = __version__,
	author = 'Mike Kazantsev',
	author_email = 'mk.fraggod@gmail.com',
	license = 'WTFPL',
	keywords = 'django unhosted app remoteStorage server'
		' cloud silo storage oauth webfinger xrd read-write-web webdav',
	url = 'https://github.com/RemoteStorage/django-remotestorage',

	description = 'Unhosted remoteStorage server app for django',
	long_description = readme,

	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Plugins',
		'Environment :: Web Environment',
		'Framework :: Django',
		'Intended Audience :: Developers',
		'Intended Audience :: Information Technology',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved',
		'Natural Language :: English',
		'Operating System :: POSIX',
		'Operating System :: Unix',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 2 :: Only',
		'Topic :: Database :: Front-Ends',
		'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
		'Topic :: Software Development :: Libraries :: Python Modules' ],

	install_requires = ['Django'],
	dependency_links = ['git+https://github.com/hiidef/oauth2app.git'],
	extras_require = {'db_migration': ['South']},

	zip_safe = False,
	packages = find_packages(),
	include_package_data = True,
	# package_data = ... <-- ignored for sdist in some setuptools/distribute versions
	exclude_package_data = {'': ['README.*']} )
