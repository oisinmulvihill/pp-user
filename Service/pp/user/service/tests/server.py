# -*- coding: utf-8 -*-
"""
User Service test runner

PythonPro Limited
"""
import os

import pytest

from pp.user.client import rest
from pp.testing import mongo_webservice


@pytest.fixture(scope='session')
def user_svc(request):
    """ Pytest fixture for the user service.
    """
    test_server = mongo_webservice.MongoConfiguredWebService(
        request=request,
        port_seed=64001,
        testing_ini=os.path.join(os.path.dirname(__file__), 'user.ini'),
        rest_api_class=rest.UserService)

    request.addfinalizer(lambda s=test_server: s.teardown())
    return test_server
