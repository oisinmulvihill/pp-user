# -*- coding: utf-8 -*-
"""
Integration Test verifing the client REST interface against the service.

PythonPro Limited

"""
import unittest
import pkg_resources

from . import svrhelp
from pp.auth import pwtools
from pp.user.model import db
from pp.user.client import rest
from pp.user.validate import userdata


# Start the test app running on module set up and stop it running on teardown.
#
def setup_module():
    svrhelp.setup_module()

teardown_module = svrhelp.teardown_module


class UserServiceTC(unittest.TestCase):

    def setUp(self):
        self.us = rest.UserService(svrhelp.webapp.URI)
        db.db().hard_reset()

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

    def testUserLoadingAndDumping(self):
        """Test the rest client's ping of the user service.
        """
        self.assertEquals(len(self.us.user.all()), 0)
        self.assertEquals(self.us.dump(), [])

        username = u'andrés.bolívar'
        display_name = u'Andrés Plácido Bolívar'
        email = u'andrés.bolívar@example.com'

        data = [
            {
                "username": "bob.sprocket",
                "oauth_tokens": {
                    "googleauth": {
                        "request_token": "1234567890"
                    }
                },
                "display_name": "Bobby",
                "phone": "12121212",
                "cats": "big",
                "teatime": 1,
                "_id": "user-2719963b00964c01b42b5d81c998fd05",
                "email": "bob@example.net",
                "password_hash": pwtools.hash_password('11amcoke')
            },
            {
                "username": username.encode('utf-8'),
                "display_name": display_name.encode('utf-8'),
                "phone": "",
                "_id": "user-38ed1d2903344702b30bb951916aaf1c",
                "email": email.encode('utf-8'),
                "password_hash": pwtools.hash_password('$admintime$')
            }
        ]

        self.us.load(data)

        self.assertEquals(len(self.us.user.all()), 2)

        item2 = self.us.user.get('bob.sprocket')
        user_dict = data[0]
        self.assertEquals(item2['username'], user_dict['username'])
        self.assertEquals(item2['display_name'], user_dict['display_name'])
        self.assertEquals(item2['email'], user_dict['email'])
        self.assertEquals(item2['phone'], user_dict['phone'])
        self.assertEquals(item2['oauth_tokens'], user_dict['oauth_tokens'])
        self.assertEquals(item2['cats'], 'big')
        self.assertEquals(item2['teatime'], 1)

        # Test the unicode name as still good:
        item1 = self.us.user.get(username)
        user_dict = data[1]
        self.assertEquals(item1['username'], username)
        self.assertEquals(item1['display_name'], display_name)
        self.assertEquals(item1['email'], email)
        self.assertEquals(item1['phone'], user_dict['phone'])

    def test_existing_username(self):
        """Test that a username must be unique for created accounts.
        """
        # make sure nothing is there to begin with.
        self.assertEquals(len(self.us.user.all()), 0)

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

        self.assertRaises(userdata.UserPresentError, self.us.user.add, user)

    def test_password_change(self):
        """Test changing a user's password.
        """
        username = "bob"
        plain_pw = "123456"

        user = dict(
            username=username,
            password_hash=pwtools.hash_password(plain_pw),
            email="bob.sprocket@example.com",
        )

        self.us.user.add(user)

        result = self.us.user.authenticate(username, plain_pw)
        self.assertTrue(result)

        # Change and test the old password is no longer valid.
        new_plain_pw = "654321"

        self.us.user.update(dict(
            username=username,
            password_hash=pwtools.hash_password(new_plain_pw),
        ))

        username = user['username']
        self.assertFalse(self.us.user.authenticate(username, plain_pw))

        # Now test that password has changed.
        username = user['username']
        self.assertTrue(self.us.user.authenticate(username, new_plain_pw))

    def test_user_management(self):
        """Test the REST based interface to add/remove/update users.
        """
        user = dict(
            username="bob",
            password_hash=pwtools.hash_password("123456"),
            display_name="Bob Sprocket",
            email="bob.sprocket@example.com",
            phone="1234567890",
            #extra={},
        )

        bob = self.us.user.add(user)

        self.assertEquals(bob['username'], user['username'])
        self.assertEquals(bob['display_name'], user['display_name'])
        self.assertEquals(bob['email'], user['email'])
        self.assertEquals(bob['phone'], user['phone'])
        #self.assertEquals(bob['extra'], user['extra'])

        # Check the unique user id is in the bob dict. Its value is generated
        # by the server.
        self.assertTrue('_id' in bob)

        # No plain text password is stored or sent over the wire:
        self.assertTrue('password_hash' in bob)

        bob = self.us.user.get(user['username'])

        self.assertEquals(bob['username'], user['username'])
        self.assertEquals(bob['display_name'], user['display_name'])
        self.assertEquals(bob['email'], user['email'])
        self.assertEquals(bob['phone'], user['phone'])
        #self.assertEquals(bob['extra'], user['extra'])
        self.assertTrue('_id' in bob)

        # Check I can't add the same user a second time:
        self.assertRaises(userdata.UserPresentError, self.us.user.add, user)

        # Test verifcation of the password:
        plain_pw = "123456"
        username = user['username']
        self.assertTrue(self.us.user.authenticate(username, plain_pw))

        plain_pw = "not the correct password"
        username = user['username']
        self.assertFalse(self.us.user.authenticate(username, plain_pw))

        # Try updating all user's information that can be changed:
        user = dict(
            username=username,
            password_hash=pwtools.hash_password("654321"),
            display_name="Sprokety Bob",
            email="bob.sprocket@example.com",
            phone="0987654321",
            #extra={"a": 1},
        )

        self.us.user.update(user)

        bob = self.us.user.get(user['username'])

        self.assertEquals(bob['username'], user['username'])
        self.assertEquals(bob['display_name'], user['display_name'])
        self.assertEquals(bob['email'], user['email'])
        self.assertEquals(bob['phone'], user['phone'])
        #self.assertEquals(bob['extra'], user['extra'])

        # Now delete the user's account from the system.
        self.us.user.remove(username)
        self.assertRaises(
            userdata.UserRemoveError, self.us.user.remove, username
        )
