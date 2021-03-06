# -*- coding: utf-8 -*-
"""
This provides the REST classes used to access the User Service.

This API is not for Public consumption. It is meant for internal tools and
service to service access.

Oisin Mulvihill
(c) PythonPro Limited, RedDeer Limited.
2014-01-23

"""
import json
import logging
from urlparse import urljoin

import requests

from pp.user.validate import error
from pp.user.validate import userdata


def get_log(e=None):
    return logging.getLogger("{0}.{1}".format(__name__, e) if e else __name__)


def new_user_dict():
    return dict(
        username="",
        password="",
        display_name="",
        email="",
        phone="",
        extra={},
    )


class UserManagement(object):

    JSON_CT = {'content-type': 'application/json'}

    ADD = "/users/"

    ALL = "/users/"

    AUTH = "/access/auth/%(username)s/"

    TOKEN = "/access/secret/%(access_token)s/"

    GET_UPDATE_OR_DELETE = "/user/%(username)s/"

    def __init__(self, uri):
        self.log = get_log("UserManagement")
        self.base_uri = uri

    def all(self):
        """Return all users currently on the system.

        :returns: A list or users or an empty list.

        """
        self.log.debug("all: attempting to recover all users on the system.")

        uri = urljoin(self.base_uri, self.ALL)
        self.log.debug("all: uri <%s>" % uri)

        res = requests.get(uri)
        rc = res.json()
        if not rc['success']:
            raise userdata.UserServiceError(rc['message'])

        self.log.debug("all: found <%s>" % len(rc['data']))

        return rc['data']

    def get(self, username):
        """Get an existing user of the system.

        :returns: The user dict.

        """
        #self.log.debug("get: attempting to get user <%s>" % username)

        uri = urljoin(self.base_uri, self.GET_UPDATE_OR_DELETE % dict(
            username=username,
        ))
        #self.log.debug("get: uri <%s>" % uri)

        res = requests.get(uri, headers=self.JSON_CT)
        rc = res.json()
        if not rc['success']:
            raise userdata.UserServiceError(rc['message'])

        return rc['data']

    def add(self, user):
        """Add a new user to the system.

        :returns: The update user dict.

        """
        self.log.debug("add: attempting to add user <%s>" % user)

        user = userdata.creation_required_fields(user)

        if "password" in user:
            user['password'] = user['password'].encode("base64")

        uri = urljoin(self.base_uri, self.ADD)
        self.log.debug("add: uri <%s>" % uri)

        res = requests.put(uri, json.dumps(user), headers=self.JSON_CT)
        rc = res.json()
        if not rc['success']:
            raise userdata.UserServiceError(rc['message'])

        return rc['data']

    def remove(self, username):
        """Remove an existing user from the system.

        :returns: None.

        """
        self.log.debug("remove: attempting to remove user <%s>" % username)

        uri = urljoin(self.base_uri, self.GET_UPDATE_OR_DELETE % dict(
            username=username,
        ))
        self.log.debug("remove: uri <%s>" % uri)

        res = requests.delete(uri, headers=self.JSON_CT)
        rc = res.json()
        if not rc['success']:
            raise userdata.UserServiceError(rc['message'])

        return rc['data']

    def update(self, data):
        """Update the details about an existing user.

        :param data: This must contain the 'username' field at least.

        You only need to provide the fields that are to be updated.

        To change password, the "new_password" field is provided.

        :returns: A dict containing the updated user details.

        """
        self.log.debug("update: validating given data")

        data = userdata.user_update_fields_ok(data)
        username = data['username']

        self.log.debug("update: attempting to update user <%s>." % username)

        # TODO: at the moment this is travelling over the intranet we control,
        # however this needs much stronger protection i.e. HTTPS/SSL between
        # services talking to each other.
        #
        # obuscate for moment.
        if "new_password" in data:
            data["new_password"] = data["new_password"].encode("base64")

        uri = urljoin(self.base_uri, self.GET_UPDATE_OR_DELETE % dict(
            username=username,
        ))
        self.log.debug("update: uri <%s>" % uri)

        res = requests.put(uri, json.dumps(data), headers=self.JSON_CT)
        rc = res.json()
        if not rc['success']:
            raise userdata.UserServiceError(rc['message'])

        return rc['data']

    def authenticate(self, username, plain_password):
        """Verify the password for the given username.

        :param username: The username string.

        :param plain_password: The plain password to be hashed and compared.

        :returns: True, password ok otherwise False.

        """
        self.log.debug("authenticate: user <%s>" % username)

        # TODO: at the moment this is travelling over the intranet we control,
        # however this needs much stronger protection i.e. HTTPS/SSL
        #
        # obuscate for moment.
        data = dict(password=plain_password.encode("base64"))

        uri = urljoin(self.base_uri, self.AUTH % dict(username=username))
        self.log.debug("authenticate: uri <%s>" % uri)

        res = requests.post(uri, json.dumps(data), headers=self.JSON_CT)
        rc = res.json()
        if not rc['success']:
            raise userdata.UserServiceError(rc['message'])

        return rc['data']

    def secret_for_access_token(self, access_token):
        """Recover the secret for the given access token.
        """
        uri = urljoin(self.base_uri, self.TOKEN % dict(
            access_token=access_token,
        ))
        self.log.debug("secret_for_access_token: uri <%s>" % uri)

        res = requests.get(uri, headers=self.JSON_CT)
        rc = res.json()
        if not rc['success']:
            raise userdata.UserServiceError(rc['message'])

        return rc['data']
