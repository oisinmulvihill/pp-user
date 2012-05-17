# -*- coding: utf-8 -*-
"""
User Administration views for the REST interface.

PythonPro Limited

"""
import logging

import transaction
from pyramid.view import view_config

from pp.auth import pwtools
from pp.auth.plugins.sql import user
from pp.user.validate import userdata
from pp.common.db.utils import DBGetError


def get_log(extra=None):
    m = "pp.user.client.rest"
    if extra:
        if isinstance(extra, basestring):
            m = "%s.%s" % (m, extra)
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
    log.debug("Validating new user<%s>: %s" % (type(user_data), user_data))

    user_data = userdata.creation_required_fields(user_data)

    with transaction.manager:
        # Tell the lower level library not to handle the commit.
        user_data['no_commit'] = True
        user.add(**user_data)

    rc = user.get(user_data['username']).to_dict()

    return rc


@view_config(route_name='the_users', request_method='GET', renderer='json')
@view_config(route_name='the_users-1', request_method='GET', renderer='json')
def the_users(request):
    """Handle the recovery of all users currently on the system.

    :returns: A list of user dicts or an empty list.

    """
    log = get_log("user_get")

    log.debug("recovering all users on the system")

    the_users = [u.to_dict() for u in user.find()]

    log.debug("Returning all %d user(s)." % len(the_users))

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

    log.debug("user_auth: here")

    username = request.matchdict['username'].strip().lower()

    log.debug("attempting to verify user <%s> authentication" % username)

    user_data = request.json_body
    log.debug("raw_auth data: %s" % user_data)

    # obuscate the password so its not immediately obvious:
    # Need to convert to SSL or some other form of secure
    # transport.
    pw = user_data['password'].decode("base64")
    found_user = user.get(username)

    log.error("\n\nSHOULD NOT BE SHOWN: user<%s> password <%s>\n\n" % (
        found_user.to_dict(), pw
    ))

    result = found_user.validate_password(pw)

    log.debug("user <%s> password validated? %s" % (found_user.username, result))

    return result


@view_config(route_name='user', request_method='POST', renderer='json')
@view_config(route_name='user-1', request_method='POST', renderer='json')
def user_update(request):
    """Update a stored user on the system.

    :returns: The updated user dict.

    """
    log = get_log("user_update")

    log.debug("here")

    username = request.matchdict['username'].strip().lower()

    log.debug("updating user <%s>" % username)

    user_data = request.json_body
    log.debug("update data: %s" % user_data)

    found_user = user.get(username)

    # un-obuscate the new password, not ideal!
    if "new_password" in user_data:
        try:
            user_data["new_password"] = user_data["new_password"].decode("base64")
        except Exception as e:
            raise ValueError("The new_password not Base64 encoded: %s" % e)

    with transaction.manager:
        # Tell the lower level library not to handle the commit.
        user_data['no_commit'] = True
        user.update(**user_data)

    result = found_user.to_dict()
    log.debug("user <%s> updated ok." % (result['username']))

    return result


@view_config(route_name='user', request_method='GET', renderer='json')
@view_config(route_name='user-1', request_method='GET', renderer='json')
def user_get(request):
    """Recover a user based on the given username.

    :returns: The user dict.

    """
    log = get_log("user_get")
    log.debug("here")

    username = request.matchdict['username'].strip().lower()
    log.debug("attempting to recover <%s>" % username)

    found_user = user.get(username)
    result = found_user.to_dict()
    log.debug("user <%s> recovered ok." % (result['username']))

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
    log.warn("Attempting to remove user <%s>." % username)

    with transaction.manager:
        try:
            found_user = user.get(username)
            # Tell the lower level library not to handle the commit.
            user.remove(found_user, no_commit=True)
        except DBGetError:
            raise userdata.UserNotFoundError("Unable to remove user <%s>" % username)

    log.warn("user <%s> removed ok." % username)
