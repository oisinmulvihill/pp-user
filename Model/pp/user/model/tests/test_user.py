# -*- coding: utf-8 -*-
"""
Test the MongoDB implementation of user functionality.

"""
import unittest

from pp.common.db import utils
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

        self.assertEquals(item2.username, user_dict['username'])
        self.assertEquals(item2.display_name, user_dict['display_name'])
        self.assertTrue(item2.validate_password(plain_pw))
        self.assertFalse(item2.validate_password("not the right one"))
        self.assertEquals(item2.email, user_dict['email'])
        self.assertEquals(item2.phone, user_dict['phone'])
        self.assertEquals(item2.extra, {})

        # Now update all the user fields that can be changed
        # and add some extra data to the arbitrary fields:
        #
        freeform_data = dict(
            # Some pretend googleservice oauth data:
            googleauth=dict(
                request_token="1234567890",
            )
        )

        user_dict = dict(
            username=username,
            password_hash=pwtools.hash_password("ifidexmemwb"),
            display_name='Bobby',
            email='bob@example.net',
            phone='12121212',
            extra=freeform_data,
        )

        user.update(**user_dict)
        item2 = user.get(username)

        self.assertEquals(item2.username, user_dict['username'])
        self.assertEquals(item2.display_name, user_dict['display_name'])
        self.assertTrue(item2.validate_password("ifidexmemwb"))
        self.assertFalse(item2.validate_password("not the right one"))
        self.assertEquals(item2.email, user_dict['email'])
        self.assertEquals(item2.phone, user_dict['phone'])
        self.assertEquals(item2.extra, freeform_data)

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
        is_validate = item1.validate_password(plain_pw)
        self.assertTrue(is_validate)

        # Try recoving by username, display_name, etc
        #
        for field in user_dict:
            if field == "password":
                # skip and no such thing as find via password although by
                # hash should in theory work.
                continue

            items = user.find(**{field: user_dict[field]})
            self.assertEquals(items, [item1])
            item1 = items[0]
            self.assertEquals(item1.username, user_dict['username'])
            self.assertEquals(item1.display_name, user_dict['display_name'])
            self.assertEquals(item1.email, user_dict['email'])
            self.assertEquals(item1.phone, user_dict['phone'])

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
