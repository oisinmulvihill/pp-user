# -*- coding: utf-8 -*-
"""
Integration Test verifing the client REST interface against the service.

PythonPro Limited

"""
import unittest
import pkg_resources

from . import svrhelp
from pp.user.client import rest
from pp.user.validate import userdata


# Start the test app running on module set up and stop it running on teardown.
#
def setup_module():
    svrhelp.setup_module()

teardown_module = svrhelp.teardown_module


class UserServiceTestCase(unittest.TestCase):

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

    def test_existing_username(self):
        """Test that a username must be unique for created accounts.
        """
        user = dict(
            username="bob",
            password="123456",
            email="bob.sprocket@example.com",
        )

        bob = self.us.user.add(user)
        self.assertEquals(bob['username'], 'bob')

        user = dict(
            username="bob",
            password="111111",
            email="fred.bale@example.net",
        )

        self.assertRaises(userdata.UserNamePresentError, self.us.user.add, user)

    def test_password_change(self):
        """Test changing a user's password.
        """
        user = dict(
            username="bob",
            password="123456",
            email="bob.sprocket@example.com",
        )

        self.us.user.add(user)

        plain_pw = "123456"
        username = user['username']
        self.assertTrue(self.us.user.authenticate(username, plain_pw))

        # Change and test the old password is no longer valid.
        self.us.user.update(dict(
            username="bob",
            new_password="654321"
        ))

        plain_pw = "123456"
        username = user['username']
        self.assertFalse(self.us.user.authenticate(username, plain_pw))

        # Now test that password has changed.
        plain_pw = "654321"
        username = user['username']
        self.assertTrue(self.us.user.authenticate(username, plain_pw))

    def test_user_management(self):
        """Test the REST based interface to add/remove/update users.
        """
        user = dict(
            username="bob",
            password="123456",
            display_name="Bob Sprocket",
            email="bob.sprocket@example.com",
            phone="1234567890",
            extra={},
        )

        bob = self.us.user.add(user)

        self.assertEquals(bob['username'], user['username'])
        self.assertEquals(bob['display_name'], user['display_name'])
        self.assertEquals(bob['email'], user['email'])
        self.assertEquals(bob['phone'], user['phone'])
        self.assertEquals(bob['extra'], user['extra'])

        # Check the unique user id is in the bob dict. Its value is generated
        # by the server.
        self.assertTrue('uid' in bob)

        # No plain text password is stored or sent over the wire:
        self.assertTrue('password_hash' in bob)

        bob = self.us.user.get(user['username'])

        self.assertEquals(bob['username'], user['username'])
        self.assertEquals(bob['display_name'], user['display_name'])
        self.assertEquals(bob['email'], user['email'])
        self.assertEquals(bob['phone'], user['phone'])
        self.assertEquals(bob['extra'], user['extra'])
        self.assertTrue('uid' in bob)

        # Check I can't add the same user a second time:
        self.assertRaises(userdata.UserPresentError, self.us.user.add, user)

        # Test verifcation of the password:
        plain_pw = "123456"
        username = user['username']
        self.assertTrue(self.us.user.authenticate(username, plain_pw))

        plain_pw = "not the correct password"
        username = user['username']
        self.assertTrue(self.us.user.authenticate(username, plain_pw))

        # Try updating all user's information that can be changed:
        user = dict(
            username="bobby",
            new_password="654321",
            display_name="Sprokety Bob",
            email="bob.sprocket@example.com",
            phone="0987654321",
            extra={"a": 1},
        )

        bob = self.us.user.update(user)

        self.assertEquals(bob['username'], user['username'])
        self.assertEquals(bob['display_name'], user['display_name'])
        self.assertEquals(bob['email'], user['email'])
        self.assertEquals(bob['phone'], user['phone'])
        self.assertEquals(bob['extra'], user['extra'])

        # Now delete the user's account from the system.
        self.us.user.remove("bobby")
        self.assertRaises(userdata.UserNotPresentError, self.us.user.remove, "bobby")
