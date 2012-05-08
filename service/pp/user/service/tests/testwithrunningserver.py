# -*- coding: utf-8 -*-
"""
Integration Test against a running instance of the WebService.

PythonPro Limited
2012-01-15

"""
import unittest
import pkg_resources

from . import svrhelp
from pp.user.client import rest


# Start the test app running on module set up and stop it running on teardown.
#
def setup_module():
    svrhelp.setup_module()

teardown_module = svrhelp.teardown_module


class WebServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.us = rest.UserService(svrhelp.webapp.URI)

    def testRestClientPing(self):
        """Test the rest client's ping of the user service.
        """
        report = self.us.ping()

        self.assertTrue("name" in report)
        self.assertTrue("version" in report)
        self.assertTrue("status" in report)

        pkg = pkg_resources.get_distribution("pp-user-service")

        self.assertEquals(report['status'], 'ok')
        self.assertEquals(report['name'], 'pp-user-service')
        self.assertEquals(report['version'], pkg.version)
