# -*- coding: utf-8 -*-
"""
User Service test runner

PythonPro Limited
"""
import os

import pytest

from pp.testing import mongo_webservice
from pp.user.client import rest


@pytest.fixture(scope='session')
def user_svc(request):
    """ Pytest fixture for the user service.
    """
    test_server = mongo_webservice.MongoConfiguredWebService(
        request=request,
        testing_ini=os.path.join(os.path.dirname(__file__), 'user.ini'),
        rest_api_class=rest.UserService)

    request.addfinalizer(lambda s=test_server: s.teardown())

    # XXX not available using session scope
    # This is to support UnitTest-based tests
    #if request.cls:
    #    request.cls.user_svc = test_server

    return test_server
