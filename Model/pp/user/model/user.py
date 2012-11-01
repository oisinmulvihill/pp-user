# -*- coding: utf-8 -*-
"""
The mongodb implementation of the methods that the sql user implementation
provides.

"""
import logging

from pp.auth import pwtools
from pp.user.model import db


def get_log(fn=''):
    if fn and fn.strip():
        fn = ".%s" % fn
    return logging.getLogger('%s%s' % (__name__, fn))


def has(username):
    """Check if the given user name is on the system.

    :returns: True if username is present False otherwise.

    """
    returned = False
    log = get_log("has")

    log.debug("looking for <{}>".format(username))
    conn = db.db().conn()

    if conn.find_one(dict(username=username)):
        log.debug("has: looking for <{}>".format(username))
        returned = True

    return returned


class UserNotFoundError(Exception):
    """Raised when a user was not found."""


def get(username):
    """Recover the detail of a user on the system.

    :param username: The unique user name to look for.

    If the username is not found the UserNotFoundError will be raised.

    :returns: The user dict.

    """
    log = get_log("get")

    log.debug("looking for <{}>".format(username))
    conn = db.db().conn()

    returned = conn.find_one(dict(username=username))
    if not returned:
        log.error("user not found for <{}>".format(username))
        raise UserNotFoundError("Unknown username <{}>".format(username))

    print "returned: <{}>".format(returned)

    return returned


def find(**kwargs):
    """Find one or many users.

    :returns: A list of user dicts or empty list.

    """
    log = get_log("find")

    log.debug("looking users with criteria <{}>".format(kwargs))
    conn = db.db().conn()

    returned = list(conn.find(kwargs))

    return returned


class UserRemoveError(Exception):
    """Raised when a user could not be removed."""


def remove(username):
    """Remove a user from the system.

    :param username: The unique user name to look for.

    """
    log = get_log("remove")
    u = {"username": username}

    log.debug("Attempting to remove user <{!r}>".format(username))
    conn = db.db().conn()

    if not conn.find_one(u):
        raise UserRemoveError(
            "The user '{}' is not present to remove.".format(username)
        )

    conn.remove(u)
    log.debug("'{}' removed OK.".format(username))


class UserPresentError(Exception):
    """Raised by add when an existing username conflicts with the new one."""


class UserAddError(Exception):
    """Raised for problems adding a new user."""


def add(**user):
    """Called to add a new user to the system.

    :param user: This is a dict of fields a user_table.UserTable() can accept.

    The username must not be present in the system already. if
    it is then UserPresentError will be raised.

    :returns: A new instance of user_table.UserTable.

    """
    log = get_log('add')

    log.debug("Given user <{}> to add.".format(user))
    username = user['username']

    if has(username):
        raise UserPresentError(
            "The username <{}> is present & cannot be added.".format(username)
        )

    if "password" not in user and "password_hash" not in user:
        raise UserAddError("No password or hash given when its required!")

    if "password" in user:
        new_password = user['password']
        # password is never stored in plain text:
        user.pop('password')
        # Set the new password hash to store, replacing the current one:
        new_password = pwtools.hash_password(new_password)
        user['password_hash'] = new_password

    if "_id" not in user:
        user['_id'] = db.doc_id_for('user')

    log.debug("The username <{}> is not present. OK to add.".format(username))

    conn = db.db().conn()
    conn.insert(user)

    log.debug("The user <{}> was added OK.".format(username))

    return get(username)


def update(**user):
    """Called to update the details of an exiting user on the system.

    This handles the 'new_password' field before passing on to the update.

    Only password can be changed at the moment.

    """
    log = get_log('update')

    log.debug("Given user <{}> to update.".format(user))

    update_data = {}

    # Make sure the user if present before attempting to add.
    current = get(user['username'])

    if "new_password" in user:
        new_password = user['new_password']
        user.pop('new_password')
        # Set the new password hash to store, replacing the current one:
        new_password = pwtools.hash_password(new_password)
        update_data['password_hash'] = new_password

    if "display_name" in user:
        update_data['display_name'] = user['display_name']

    if "new_username" in user:
        new_username = user['new_username']
        if not has(user['new_username']):
            update_data['username'] = new_username
        else:
            raise UserPresentError(
                "Cannot rename to username <%s> as it is used." % new_username
            )

    if "password_hash" in user:
        update_data['password_hash'] = user['password_hash']

    if "email" in user:
        update_data['email'] = user['email']

    if "phone" in user:
        update_data['phone'] = user['phone']

    log.debug("update_data: <{}>".format(update_data))

    _id = current['_id']

    # update current with the date preserving the db id:
    current.update(update_data)
    current['_id'] = _id

    log.debug("updated current instance to save: <{}>".format(current))
    conn = db.db().conn()
    conn.save(current)

    log.debug("<%s> updated OK." % user['username'])

    # Return the updated user details:
    return get(user['username'])


def count():
    """Return the number of users on the system.

    :returns: a number greater or equal to zero.

    """
    conn = db.db().conn()
    return conn.count()
