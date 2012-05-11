# -*- coding: utf-8 -*-
"""
User Administration views for the REST interface.

PythonPro Limited

"""
import logging

import transaction
from pyramid.view import view_config

from pp.auth.plugins.sql import user
from pp.user.validate import userdata


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
        # Tell the library add not to handle the commit.
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


@view_config(route_name='user', request_method='POST', renderer='json')
def user_update(request):
    """
    """
    return {}


@view_config(route_name='user', request_method='DELETE', renderer='json')
def user_remove(request):
    """
    """
    return {}
