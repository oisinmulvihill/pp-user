# -*- coding: utf-8 -*-
"""
User Service test runner

PythonPro Limited
"""
import ConfigParser

import pytest
from pkglib.testing import pyramid_server
from pkglib.testing.mongo_server import MongoTestServer

from pp.user.client import rest


@pytest.fixture(scope='function')
def mongo_server(request):
    """ Turn off random port mapping for these tests as we want the
        webserver to stay up but rebuild the database
    """
    class NonRandomMongoServer(MongoTestServer):
        random_port = False
    test_server = NonRandomMongoServer()
    request.addfinalizer(lambda s=test_server: s.teardown())
    return test_server


@pytest.fixture(scope='session')
def user_service(request):
    """ Pytest fixture for the user service. Looks for the mongo server
        fixture and sets up the server config to point to that.
        Also attaches a client API to the object.
    """
    class UserService(pyramid_server.PyramidTestServer):
        def __init__(self, **kwargs):
            super(UserService, self).__init__(**kwargs)
            self.api = rest.UserService(self.uri)

        def pre_setup(self):
            super(UserService, self).pre_setup()
            parser = ConfigParser.ConfigParser()
            parser.read(self.config)
            mongo_server = request.getfuncargvalue('mongo_server')
            parser.set('app:main', 'mongodb.host', mongo_server.hostname)
            parser.set('app:main', 'mongodb.port', mongo_server.port)
            print "User Service using mongodb at %s:%s" % (mongo_server.hostname,
                                                           mongo_server.port)
            with self.config.open('w') as fp:
                parser.write(fp)

    test_server = UserService()
    request.addfinalizer(lambda s=test_server: s.teardown())
    return test_server
