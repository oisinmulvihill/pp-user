# -*- coding: utf-8 -*-
"""
This provides the REST classes used to access the User Service.

"""
import json
import logging
from urlparse import urljoin

import requests

from pp.auth import pwtools
from pp.user.validate import error
from pp.user.validate import userdata


def get_log(extra=None):
    m = "pp.user.client.rest"
    if extra:
        if isinstance(extra, basestring):
            m = "%s.%s" % (m, extra)
    return logging.getLogger(m)


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

    ADD = "/users/"

    ALL = "/users/"

    AUTH = "/access/auth/%(username)s/"

    GET_UPDATE_OR_DELETE = "/user/%()s/"

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

        rc = json.loads(res.content)
        if "status" in rc:
            # List should be a list and not an error dict!
            raise error.CommunicationError(rc['message'])

        else:
            return rc

        self.log.debug("all: found <%s>" % len(rc))

        return rc

    def add(self, user):
        """Add a new user to the system.

        :returns: The update user dict.

        """
        self.log.debug("add: attempting to add user <%s>" % user)

        user = userdata.creation_required_fields(user)

        uri = urljoin(self.base_uri, self.ADD)
        self.log.debug("add: uri <%s>" % uri)

        res = requests.put(uri, json.dumps(user), headers={'content-type': 'application/json'})
        rc = json.loads(res.content)

        if rc and "status" in rc and rc['status'] == "error":
            error = rc['error'].strip()
            if hasattr(userdata, error):
                # re-raise the error:
                raise getattr(userdata, error)(rc['message'])
            else:
                raise SystemError("%s: %s" % (error, rc['message']))
        else:
            return rc

    def update(self, data):
        """
        """
        self.log.debug("authenticate: user <%s>" % data['username'])

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

        res = requests.post(uri, json.dumps(data), headers={'content-type': 'application/json'})
        rc = json.loads(res.content)

        # this should only be True or False and not a status dict
        # which has an error.
        if not isinstance(rc, bool):
            error = rc['error'].strip()
            if hasattr(userdata, error):
                # re-raise the error:
                raise getattr(userdata, error)(rc['message'])
            else:
                raise SystemError("%s: %s" % (error, rc['message']))
        else:
            return rc


class UserService(object):
    """This provides and interface to the REST service for dealing with
    user operations.
    """
    def __init__(self, uri="http://localhost:16801"):
        """Set the URI of the UserService.

        :param uri: The base address of the User Service server.

        """
        self.log = get_log("UserService")
        self.uri = uri
        self.user = UserManagement(self.uri)

    def ping(self):
        """Recover the User Service status page.

        This will raise a connection error or it will return successfully.

        :returns: service status dict.

        """
        res = requests.get(self.uri)
        res.raise_for_status()
        return json.loads(res.content)
