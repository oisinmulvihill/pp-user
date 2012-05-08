# -*- coding: utf-8 -*-
"""
Setuptools script for pp-user-service (pp.user.service)

"""
from setuptools import setup, find_packages

# Get the version from the source or the cached egg version:
import json
import ConfigParser
cp = ConfigParser.ConfigParser()
try:
    cp.read('../eggs_version.ini')
    version = dict(cp.items('default'))['version']
except:
    # inside and egg, read the cache version instead.
    with file("cached_version.json", "r") as fd:
        version = json.loads(fd.read())['egg_version']
else:
    # write out the version so its cached for in egg use:
    with file("cached_version.json", "w") as fd:
        fd.write(json.dumps(dict(egg_version=version)))

Name = 'pp-user-service'
ProjectUrl = ""
Version = version
Author = ''
AuthorEmail = 'everyone at pythonpro dot co dot uk'
Maintainer = ''
Summary = 'Pyramid REST Application for pp-user-service'
License = ''
Description = Summary
ShortDescription = Summary

needed = [
    'sphinx',  # for docs generation.

    # base auth set up:
    'pp-web-base',
]

test_needed = [
]

test_suite = 'pp.user.service.tests'

EagerResources = [
    'pp',
]

# Example including shell script out of scripts dir
ProjectScripts = [
#    'pp.user.service/scripts/somescript',
]

PackageData = {
    '': ['*.*'],
}

# Web Entry points
EntryPoints = """
[console_scripts]
userservice-admin = pp.user.service.scripts.main:main

[paste.app_factory]
      main = pp.user.service:main
"""

setup(
    url=ProjectUrl,
    name=Name,
    zip_safe=False,
    version=Version,
    author=Author,
    author_email=AuthorEmail,
    description=ShortDescription,
    long_description=Description,
    classifiers=[
      "Programming Language :: Python",
      "Framework :: Pylons",
      "Topic :: Internet :: WWW/HTTP",
      "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    keywords='web wsgi bfg pylons pyramid',
    license=License,
    scripts=ProjectScripts,
    install_requires=needed,
    tests_require=test_needed,
    test_suite=test_suite,
    include_package_data=True,
    packages=find_packages(),
    package_data=PackageData,
    eager_resources=EagerResources,
    entry_points=EntryPoints,
    namespace_packages=['pp', 'pp.user'],
)
