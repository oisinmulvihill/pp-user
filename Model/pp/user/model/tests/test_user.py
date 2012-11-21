# -*- coding: utf-8 -*-
"""
Test the MongoDB implementation of user functionality.

"""
import unittest

from pp.auth import pwtools
from pp.user.model import db
from pp.user.model import user


class UserTC(unittest.TestCase):

    def setUp(self):
        """Set up the mongodb connection and database, clear out test data.
        """
        # Set up the mongodb connection:
        db.init(dict(db_name="unittesting1"))
        #db.init(dict(db_name="dal_unittesting1"))

        # Clear out anything that maybe left over after previous test runs:
        db.db().hard_reset()

    def test_validate_password(self):
        """
        """
        self.assertEquals(user.count(), 0)
        self.assertEquals(user.dump(), [])

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
        user.load(data)

        self.assertTrue(user.validate_password('bob.sprocket', '11amcoke'))
        self.assertFalse(user.validate_password('bob.sprocket', 'incorrect'))
        self.assertFalse(user.validate_password(username, '11amcoke'))
        self.assertTrue(user.validate_password(username, '$admintime$'))

    def test_dump_and_load(self):
        """Test the dump and loading of the user 'universe'.
        """
        self.assertEquals(user.count(), 0)
        self.assertEquals(user.dump(), [])

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

        user.load(data)

        self.assertEquals(user.count(), 2)

        item2 = user.get('bob.sprocket')
        user_dict = data[0]
        self.assertEquals(item2['username'], user_dict['username'])
        self.assertEquals(item2['display_name'], user_dict['display_name'])
        self.assertEquals(item2['email'], user_dict['email'])
        self.assertEquals(item2['phone'], user_dict['phone'])
        self.assertEquals(item2['oauth_tokens'], user_dict['oauth_tokens'])
        self.assertEquals(item2['cats'], 'big')
        self.assertEquals(item2['teatime'], 1)

        # Test the unicode name as still good:
        item1 = user.get(username)
        user_dict = data[1]
        self.assertEquals(item1['username'], username)
        self.assertEquals(item1['display_name'], display_name)
        self.assertEquals(item1['email'], email)
        self.assertEquals(item1['phone'], user_dict['phone'])

    def test_change_password(self):
        """The the single call to change a users password.
        """
        import nose
        raise nose.SkipTest("skipping over change_password test.")

        username = 'bob.sprocket'
        plain_pw = '1234567890'
        confirm_plain_pw = '1234567890'
        new_plain_pw = '0987654321'

        self.assertEquals(user.count(), 0)
        self.assertEquals(user.find(username=username), [])

        with self.assertRaises(user.UserNotFoundError):
            # The user isn't present to recover
            user.change_password(
                username,
                plain_pw,
                confirm_plain_pw,
                new_plain_pw
            )

        # Add the user:
        user_dict = dict(
            username=username,
            password=plain_pw,
            display_name='Bob Sprocket',
            email='bob.sprocket@example.com',
        )
        item1 = user.add(**user_dict)
        is_valid = pwtools.validate_password(plain_pw, item1['password_hash'])
        self.assertTrue(is_valid)

        # Now change the password
        user.change_password(
            username,
            plain_pw,
            confirm_plain_pw,
            new_plain_pw
        )
        item1 = user.get(username)

        # old password is not valid:
        is_valid = pwtools.validate_password(plain_pw, item1['password_hash'])
        self.assertFalse(is_valid)

        is_valid = pwtools.validate_password(
            new_plain_pw, item1['password_hash']
        )
        self.assertTrue(is_valid)

    def testExtraField(self):
        """Test the arbitrary dic that can be used to store useful fields
        per user.
        """
        username = 'bob.sprocket'
        plain_pw = '1234567890'

        self.assertEquals(user.count(), 0)
        self.assertEquals(user.find(username=username), [])

        user_dict = dict(
            username=username,
            password=plain_pw,
            display_name='Bob Sprocket',
            email='bob.sprocket@example.com',
            phone='9876543210'
        )
        item1 = user.add(**user_dict)

        # Make sure I cannot add the same username again:
        self.assertRaises(user.UserPresentError, user.add, **user_dict)

        self.assertEquals(user.find(username=username), [item1])
        self.assertEquals(user.has(username), True)
        self.assertEquals(user.count(), 1)

        item2 = user.get(username)

        self.assertEquals(item2['username'], user_dict['username'])
        self.assertEquals(item2['display_name'], user_dict['display_name'])
        is_validate = pwtools.validate_password(
            plain_pw, item1['password_hash']
        )
        self.assertTrue(is_validate)
        is_validate = pwtools.validate_password(
            "not the right one", item1['password_hash']
        )
        self.assertFalse(is_validate)
        self.assertEquals(item2['email'], user_dict['email'])
        self.assertEquals(item2['phone'], user_dict['phone'])

        # Now update all the user fields that can be changed
        # and add some extra data to the arbitrary fields:
        #
        oauth_tokens = dict(
            # Some pretend googleservice oauth data:
            googleauth=dict(
                request_token="1234567890",
            )
        )

        user_dict = dict(
            username=username,
            # change the password. new_password will be hashed and
            # its has stored as password_hash:
            new_password="ifidexmemwb",
            display_name='Bobby',
            email='bob@example.net',
            phone='12121212',
            oauth_tokens=oauth_tokens,
            cats='big',
            teatime=1,
        )

        user.update(**user_dict)
        item2 = user.get(username)

        self.assertEquals(item2['username'], user_dict['username'])
        self.assertEquals(item2['display_name'], user_dict['display_name'])
        is_validate = pwtools.validate_password(
            "ifidexmemwb", item2['password_hash']
        )
        self.assertTrue(is_validate)
        is_validate = pwtools.validate_password(
            plain_pw, item2['password_hash']
        )
        self.assertFalse(is_validate)
        is_validate = pwtools.validate_password(
            "not the right one", item1['password_hash']
        )
        self.assertFalse(is_validate)
        self.assertEquals(item2['email'], user_dict['email'])
        self.assertEquals(item2['phone'], user_dict['phone'])
        self.assertEquals(item2['oauth_tokens'], oauth_tokens)
        self.assertEquals(item2['cats'], 'big')
        self.assertEquals(item2['teatime'], 1)

    def test_unicode_fields(self):
        """Test the entry of unicode username, email, display name.
        """
        username = u'andrés.bolívar'

        self.assertEquals(user.count(), 0)
        self.assertEquals(user.find(username=username), [])

        plain_pw = u'í12345í67890é'

        user_dict = dict(
            username=username,
            password=plain_pw,
            display_name=u'Andrés Plácido Bolívar',
            email=u'andrés.bolívar@example.com',
            phone=u''
        )
        item1 = user.add(**user_dict)

        # Check the password is converted into a hashed password correctly:
        is_validate = pwtools.validate_password(
            plain_pw, item1['password_hash']
        )
        self.assertTrue(is_validate)

        # Try recoving by username, display_name, etc
        #
        for field in user_dict:
            if field == "password":
                # skip, no such thing as find via password.
                continue

            items = user.find(**{field: user_dict[field]})
            self.assertEquals(items, [item1])
            item1 = items[0]
            self.assertEquals(item1['username'], user_dict['username'])
            self.assertEquals(item1['display_name'], user_dict['display_name'])
            self.assertEquals(item1['email'], user_dict['email'])
            self.assertEquals(item1['phone'], user_dict['phone'])

    def testBasicCRUD(self):
        """Test the basic add and get method
        """
        username = 'bob.sprocket'

        self.assertEquals(user.count(), 0)

        self.assertEquals(user.find(username=username), [])

        # Test I cannot add a user if I don't provide either a
        # password or a password_hash
        #
        user_dict = dict(
            username=username,
            # Not provied password or password hash
            #password='1234567890',
        )
        self.assertRaises(user.UserAddError, user.add, **user_dict)

        plain_pw = '1234567890'

        user_dict = dict(
            username=username,
            password=plain_pw,
            display_name='Bob Sprocket',
            email='bob.sprocket@example.com',
            phone='9876543210'
        )
        item1 = user.add(**user_dict)

        # The password is hashed and then stored as password_hash. The password
        # it removed and never stored.
        self.assertTrue("password" not in item1)

        # Check the password is converted into a hashed password correctly:
        is_validate = pwtools.validate_password(
            plain_pw, item1['password_hash']
        )
        self.assertTrue(is_validate)

        # Make sure I cannot add the same username again:
        self.assertRaises(user.UserPresentError, user.add, **user_dict)

        self.assertEquals(user.find(username=username), [item1])
        self.assertEquals(user.has(username), True)
        self.assertEquals(user.count(), 1)

        item2 = user.get(username)

        self.assertEquals(item2["username"], user_dict['username'])
        self.assertEquals(item2['display_name'], user_dict['display_name'])
        self.assertEquals(item2['email'], user_dict['email'])
        self.assertEquals(item2['phone'], user_dict['phone'])

        user.remove(item2['username'])

        self.assertEquals(user.count(), 0)

        self.assertEquals(user.has(item2['username']), False)

        self.assertRaises(user.UserRemoveError, user.remove, item2['username'])
