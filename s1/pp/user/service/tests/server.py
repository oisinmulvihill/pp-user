# -*- coding: utf-8 -*-
"""
User Service test runner

PythonPro Limited
"""
import os
import ConfigParser

import pytest

from pp.user.client import rest
from pkglib.testing import pyramid_server


@pytest.fixture(scope='session')
def user_svc(request):
    """ Pytest fixture for the user service.
    """

    class TestService(pyramid_server.PyramidTestServer):
        port_seed = 64001

        def __init__(self, **kwargs):
            kwargs['testing_ini'] = os.path.join(
                os.path.dirname(__file__),
                'user.ini'
            )
            super(TestService, self).__init__(**kwargs)
            self.api = rest.UserService(self.uri)

        def pre_setup(self):
            super(TestService, self).pre_setup()
            parser = ConfigParser.ConfigParser()
            parser.read(self.config)

            mongo_server = request.getfuncargvalue('mongo_server')
            host = mongo_server.hostname
            port = mongo_server.port
            print(
                "UserService: mongo server '{0}:'{1}'".format(host, port)
            )
            parser.set('app:main', 'mongodb.host', host)
            parser.set('app:main', 'mongodb.port', port)
            with self.config.open('w') as fp:
                parser.write(fp)

    test_server = TestService()
    request.addfinalizer(lambda s=test_server: s.teardown())
    return test_server
