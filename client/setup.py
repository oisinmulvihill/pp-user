# -*- coding: utf-8 -*-
"""
Setuptools script for pp-user-client (pp.user.client)

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

Name = 'pp-user-client'
ProjectUrl = ""
Version = version
Author = ''
AuthorEmail = 'everyone at pythonpro dot co dot uk'
Maintainer = ''
Summary = ' pp-user-client '
License = ''
Description = Summary
ShortDescription = Summary

needed = [
    'sphinx',  # for docs generation.
    'evasion-common',
]

test_needed = [
]

test_suite = 'pp.user.client.tests'

EagerResources = [
    'pp',
]

# Example including shell script out of scripts dir
ProjectScripts = [
#    'pp.user.client/scripts/somescript',
]

PackageData = {
    '': ['*.*'],
}

# Example console script and paster template integration:
EntryPoints = {
    'console_scripts': [
        'clientapp = pp.user.client.scripts.main:main',
    ],
}


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
