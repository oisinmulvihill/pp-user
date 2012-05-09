# -*- coding: utf-8 -*-
import unittest

from pp.user.validate import userdata


class UserDataTC(unittest.TestCase):

    def test_minimal_account_data(self):
        """Test that the minimal account details are provided.
        """
        # username is missing, empty or too small errors:
        user = dict(
            #username="bob",
            password="123456",
            email="bob.sprocket@example.com",
        )

        self.assertRaises(userdata.UserNameRequiredError, userdata.creation_required_fields, user)

        user = dict(
            username="  ",
            password="123456",
            email="bob.sprocket@example.com",
        )

        self.assertRaises(userdata.UserNameRequiredError, userdata.creation_required_fields, user)

        user = dict(
            username=None,
            password="123456",
            email="bob.sprocket@example.com",
        )

        self.assertRaises(userdata.UserNameRequiredError, userdata.creation_required_fields, user)

        user = dict(
            username="bo",
            password="123456",
            email="bob.sprocket@example.com",
        )

        self.assertRaises(userdata.UserNameTooSmallError, userdata.creation_required_fields, user)

        # password present, empty or too small errors:
        user = dict(
            username="bob",
            #password="123456",
            email="bob.sprocket@example.com",
        )

        self.assertRaises(userdata.PasswordRequiredError, userdata.creation_required_fields, user)

        user = dict(
            username="bob",
            password=" ",
            email="bob.sprocket@example.com",
        )

        self.assertRaises(userdata.PasswordRequiredError, userdata.creation_required_fields, user)

        user = dict(
            username="bob",
            password=None,
            email="bob.sprocket@example.com",
        )

        self.assertRaises(userdata.PasswordRequiredError, userdata.creation_required_fields, user)

        # email is present and not empty:
        user = dict(
            username="bob",
            password="123456",
            #email="bob.sprocket@example.com",
        )

        self.assertRaises(userdata.EmailRequiredError, userdata.creation_required_fields, user)

        user = dict(
            username="bob",
            password="123456",
            email="  ",
        )

        self.assertRaises(userdata.EmailRequiredError, userdata.creation_required_fields, user)

        user = dict(
            username="bob",
            password="123456",
            email=None,
        )

        self.assertRaises(userdata.EmailRequiredError, userdata.creation_required_fields, user)

    def test_passthrough_unchanged(self):
        """Test the data should not be changed on its way through validation.
        """
        user = dict(
            username="bob",
            password="123456",
            email="bob.sprocket@example.com",
        )
        self.assertEquals(userdata.creation_required_fields(user), user)

    def test_minimum_password_length(self):
        """Test the minimum six character password is provided.
        """
        user = dict(
            username="bob",
            password="12345",
            email="bob.sprocket@example.com",
        )

        self.assertRaises(userdata.PasswordTooSmallError, userdata.creation_required_fields, user)
