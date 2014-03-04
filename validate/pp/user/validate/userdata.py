# -*- coding: utf-8 -*-
"""
This provides validation functions of user data used in both the client and
server side.

"""


class UserServiceError(Exception):
    """Base class for UserService errors."""


class UserAddError(UserServiceError):
    """A server error occured adding a user."""


class UserPresentError(UserServiceError):
    """Raised when a user was attempted to be added when present."""


class UserRemoveError(UserServiceError):
    """Raised when a user could not be removed."""


class UserNotFoundError(UserServiceError):
    """Raised when a user is not present on the system."""


class UserNameRequiredError(UserServiceError):
    """Raised when a username is not present or empty."""


class UserNameTooSmallError(UserServiceError):
    """The user name is not >= 3 characters."""


class PasswordRequiredError(UserServiceError):
    """Raised when a password is not present or empty."""


class EmailRequiredError(UserServiceError):
    """Raised when a email is not present or empty."""


class PasswordTooSmallError(UserServiceError):
    """Password must be a >= 6 characters."""


def user_update_fields_ok(data):
    """Make sure the given data dict is valid for an updated.

    :returns: The given data.

    """
    if 'username' in data:
        if not data['username']:
            raise UserNameRequiredError(
                "The field is present but empty"
            )

        elif not data['username'].strip():
            raise UserNameRequiredError(
                "The field is present but empty"
            )

        elif len(data['username']) < 3:
            raise UserNameTooSmallError(
                "Given user is too small to create and account"
            )
    else:
        raise UserNameRequiredError(
            "The username field is not present"
        )

    if 'new_password' in data:
        password = data['new_password']
        if not password:
            raise PasswordTooSmallError(
                "The new_password is present but empty"
            )

        elif not password.strip():
            raise PasswordTooSmallError(
                "The new_password is present but empty"
            )

        elif len(password) < 6:
            raise PasswordTooSmallError(
                "Given new_password is too small to create and account"
            )

        else:
            data['new_password'] = data['new_password'].strip()

    return data


def creation_required_fields(data):
    """Check the given user dict for the required fields.

    username, password and email are the minimum required fields. Errors
    will be raised if they are not present or empty.

    """
    if 'password' in data:
        password = data['password']
        if not password:
            raise PasswordRequiredError(
                "The field is present but empty"
            )

        elif not password.strip():
            raise PasswordRequiredError(
                "The field is present but empty"
            )

        elif len(password) < 6:
            raise PasswordTooSmallError(
                "Given password is too small to create and account"
            )

    else:
        if not 'password_hash' in data:
            raise PasswordRequiredError(
                "The password field is not present"
            )

    if 'username' in data:
        if not data['username']:
            raise UserNameRequiredError(
                "The field is present but empty"
            )

        elif not data['username'].strip():
            raise UserNameRequiredError(
                "The field is present but empty"
            )

        elif len(data['username']) < 3:
            raise UserNameTooSmallError(
                "Given user is too small to create and account"
            )
    else:
        raise UserNameRequiredError(
            "The username field is not present"
        )

    if 'email' in data:
        if not data['email']:
            raise EmailRequiredError(
                "The field is present but empty"
            )

        elif not data['email'].strip():
            raise EmailRequiredError(
                "The field is present but empty"
            )
    else:
        raise EmailRequiredError(
            "The email field is not present"
        )

    return data
