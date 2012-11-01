# -*- coding: utf-8 -*-
"""
Run tests against a fake wsgi server instance. This is for lightweight testing.

"""
import unittest
import pkg_resources
from pyramid import testing

from pp.user.service.views import status


# def _initTestingDB():
#     from sqlalchemy import create_engine
#     from pp.bookingsys.frontend.models import initialize_sql
#     session = initialize_sql(create_engine('sqlite://'))
#     return session


class TestMatryoshkaSlotServiceFakeWSGI(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        # _initTestingDB()

    def tearDown(self):
        testing.tearDown()

    def test_status_view(self):
        """Test what gets returned by the status view.
        """
        request = testing.DummyRequest()

        info = status(request)

        pkg = pkg_resources.get_distribution("pp-user-service")

        self.assertEqual(info['status'], 'ok')
        self.assertEqual(info['name'], 'pp-user-service')
        self.assertEqual(info['version'], pkg.version)
