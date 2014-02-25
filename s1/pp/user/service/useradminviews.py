# -*- coding: utf-8 -*-
"""
User Administration views for the REST interface.

PythonPro Limited

"""
import logging

from pyramid.view import view_config

from pp.auth import pwtools
from pp.user.model import user
from pp.user.validate import userdata


def get_log(extra=None):
    m = "{}.{}".format(__name__, extra) if extra else __name__
    return logging.getLogger(m)


@view_config(route_name='the_users', request_method='PUT', renderer='json')
@view_config(route_name='the_users-1', request_method='PUT', renderer='json')
def user_add(request):
    """Add a new user to the system when the data is PUT to the server.

    The user dict that's posted must validate against
    userdata.creation_required_fields(user_data).

    """
    log = get_log("user_add")

    user_data = request.json_body
    log.debug(
        "Validating new user<{}>: {!r}".format(type(user_data), user_data)
    )

    user_data = userdata.creation_required_fields(user_data)

    rc = user.add(**user_data)

    return rc


@view_config(route_name='the_users', request_method='GET', renderer='json')
@view_config(route_name='the_users-1', request_method='GET', renderer='json')
def the_users(request):
    """Handle the recovery of all users currently on the system.

    :returns: A list of user dicts or an empty list.

    """
    log = get_log("user_get")

    log.debug("recovering all users on the system")

    the_users = [u for u in user.find()]

    log.debug("Returning all '{}' user(s).".format(len(the_users)))

    return the_users


@view_config(route_name='user-auth', request_method='POST', renderer='json')
def user_auth(request):
    """Handle password verification.

    The username is given along with the POSTed password_hash.

    No plain text password is sent. The hashed version is given and needs to
    verfied.

    :returns: True, password hash is ok otherwise False.

    """
    log = get_log("user_auth")

    username = request.matchdict['username'].strip().lower()

    log.debug(
        "attempting to verify user <{!r}> authentication".format(username)
    )

    user_data = request.json_body
    log.debug("raw_auth data: {!r}".format(user_data))

    # obuscate the password so its not immediately obvious:
    # Need to convert to SSL or some other form of secure
    # transport.
    pw = user_data['password'].decode("base64")
    found_user = user.get(username)

    # log.error("\n\nSHOULD NOT BE SHOWN: user<%s> password <%s>\n\n" % (
    #     found_user, pw
    # ))

    result = pwtools.validate_password(
        pw, found_user['password_hash']
    )

    log.debug("user <{!r}> password validated? {}".format(
        found_user['username'], result
    ))

    return result


@view_config(route_name='user', request_method='PUT', renderer='json')
@view_config(route_name='user-1', request_method='PUT', renderer='json')
def user_update(request):
    """Update a stored user on the system.

    :returns: The updated user dict.

    """
    log = get_log("user_update")

    username = request.matchdict['username'].strip().lower()

    log.debug("updating user <{!r}>".format(username))

    user_data = request.json_body

    # un-obuscate the new password, not ideal!
    if "new_password" in user_data:
        try:
            decoded = user_data["new_password"].decode("base64")
            user_data["new_password"] = decoded
        except Exception as e:
            raise ValueError("The new_password not Base64 encoded: %s" % e)

    result = user.update(**user_data)

    log.debug("user <{!r}> updated ok.".format(result['username']))

    return result


@view_config(route_name='user', request_method='GET', renderer='json')
@view_config(route_name='user-1', request_method='GET', renderer='json')
def user_get(request):
    """Recover a user based on the given username.

    :returns: The user dict.

    """
    log = get_log("user_get")

    username = request.matchdict['username'].strip().lower()
    log.debug("attempting to recover <{!r}>".format(username))

    result = user.get(username)
    log.debug("user <{!r}> recovered ok.".format((result['username'])))

    return result


@view_config(route_name='user', request_method='DELETE', renderer='json')
@view_config(route_name='user-1', request_method='DELETE', renderer='json')
def user_remove(request):
    """Remove a user from the system.

    :returns: None

    """
    log = get_log("user_remove")
    log.debug("here")

    username = request.matchdict['username'].strip().lower()
    log.warn("Attempting to remove user <{!r}>.".format(username))

    user.remove(username)

    log.warn("user <{!r}> removed ok.".format(username))
