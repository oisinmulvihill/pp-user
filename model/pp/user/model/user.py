# -*- coding: utf-8 -*-
"""
The mongodb implementation of the methods that the sql user implementation
provides.

"""
import logging

from pp.auth import pwtools
from pp.user.model import db
from pp.user.validate.userdata import UserAddError
from pp.user.validate.userdata import UserRemoveError
from pp.user.validate.userdata import UserNotFoundError
from pp.user.validate.userdata import UserPresentError


def get_log(extra=None):
    m = "{}.{}".format(__name__, extra) if extra else __name__
    return logging.getLogger(m)


def has(username):
    """Check if the given user name is on the system.

    :returns: True if username is present False otherwise.

    """
    returned = False
    log = get_log("has")

    log.debug("looking for <{!r}>".format(username))
    conn = db.db().conn()

    if conn.find_one(dict(username=username)):
        log.debug("has: found <{!r}>".format(username))
        returned = True

    return returned


def get(username):
    """Recover the detail of a user on the system.

    :param username: The unique user name to look for.

    If the username is not found the UserNotFoundError will be raised.

    :returns: The user dict.

    """
    log = get_log("get")

    if isinstance(username, unicode):
        username = username.encode('utf-8')

    #log.debug("looking for <{!r}>".format(username))
    conn = db.db().conn()

    returned = conn.find_one(dict(username=username))
    if not returned:
        log.error("user not found for <{!r}>".format(username))
        raise UserNotFoundError("Unknown username <{!r}>".format(username))

    return returned


def find(**kwargs):
    """Find one or many users.

    :returns: A list of user dicts or empty list.

    """
    log = get_log("find")

    log.debug("looking users with criteria <{!r}>".format(kwargs))
    conn = db.db().conn()

    returned = list(conn.find(kwargs))

    return returned


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
            "The user '{!r}' is not present to remove.".format(username)
        )

    conn.remove(u)
    log.debug("'{!r}' removed OK.".format(username))


def add(**user):
    """Called to add a new user to the system.

    :param user: This is a dict of fields a user_table.UserTable() can accept.

    The username must not be present in the system already. if
    it is then UserPresentError will be raised.

    :returns: A new instance of user_table.UserTable.

    """
    log = get_log('add')

    username = user['username']
    log.debug("Given user <{!r}> to add.".format(username))

    if has(username):
        raise UserPresentError(
            "The username <{!r}> is present & cannot be added.".format(
                username
            )
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

    log.debug(
        "The username <{!r}> is not present. OK to add.".format(username)
    )

    conn = db.db().conn()
    conn.insert(user)

    log.debug("The user <{!r}> was added OK.".format(username))

    return get(username)


def update(**user):
    """Called to update the details of an exiting user on the system.

    This handles the 'new_password' field before passing on to the update.

    Only password can be changed at the moment.

    """
    log = get_log('update')

    # Make sure the user if present before attempting to add.
    current = get(user['username'])

    log.debug("Given user <{!r}> to update.".format(user['username']))

    if "new_password" in user:
        new_password = user['new_password']
        user.pop('new_password')
        # Set the new password hash to store, replacing the current one:
        new_password = pwtools.hash_password(new_password)
        current['password_hash'] = new_password

    if "new_username" in user:
        new_username = user['new_username']
        user.pop('new_username')
        if not has(user['new_username']):
            current['username'] = new_username
        else:
            raise UserPresentError(
                "Cannot rename to username <{!r}> as it is used.".format(
                    new_username
                )
            )

    # update current with the date preserving the db id:
    _id = current['_id']
    for key in user:
        current[key] = user[key]
    else:
        current['_id'] = _id

    # log.debug(
    #     "updated current instance to save:\n\n <{!r}>\n\n\n".format(current)
    # )
    conn = db.db().conn()
    conn.save(current)

    log.debug("<{!r}> updated OK.".format(user['username']))

    # Return the updated user details:
    return get(user['username'])


def change_password(username, plain_pw, confirm_plain_pw, new_plain_pw):
    """Change a user's password in a single step.

    :param username: The user's unique username.

    :param plain_pw: The user's current password in plain text.

    :param confirm_plain_pw: The user's current password in plain text.

    """


def validate_password(username, plain_pw):
    """Validate a user's password.

    :param username: The unique username of the system user.

    :param plain_pw: The plain text password to check.

    :returns: True means password valiates otherwise False is returned.

    """
    found_user = get(username)

    result = pwtools.validate_password(
        plain_pw, found_user['password_hash']
    )

    return result


def secret_for_access_token(access_token):
    """Recover the user's for the given access_token.

    :param access_token: The access token string to look with.

    :returns: the secret token string or None if nothing was found.

    """
    access_secret = None
    log = get_log('user_for_access_token')

    log.debug("Looking for access token '{}' owner".format(access_token))

    for userdict in find():
        if 'tokens' not in userdict:
            log.debug(
                "user '{}' has no tokens field. Skipping.".format(
                    userdict['username']
                )
            )
            continue

        if access_token in userdict['tokens']:
            access_secret = userdict['tokens'][access_token]['access_secret']
            log.debug(
                "secret found for access_token '{}' owner:'{}'" .format(
                    access_token, userdict['username']
                )
            )
            break

        else:
            log.debug(
                "user '{}' access token doesn't match.".format(
                    userdict['username']
                )
            )

    if not access_secret:
        log.debug(
            "No access secret found for access_token '{}'".format(
                access_token
            )
        )

    return access_secret


def load(data):
    """Load all users into the system.
    """
    log = get_log('load')
    conn = db.db().conn()
    log.warn("loading '{}' users.".format(len(data)))
    conn.insert(data)


def dump():
    """Dump all users to a list ready for backup.
    """
    log = get_log('dump')

    log.warn("dumping all users of the system.")
    returned = list(find())

    return returned


def count():
    """Return the number of users on the system.

    :returns: a number greater or equal to zero.

    """
    conn = db.db().conn()
    return conn.count()
