# -*- coding: utf-8 -*-
"""
This provides the REST classes used to access the User Service.

This API is not for Public consumption. It is meant for internal tools and
service to service access.

"""
import json
import logging
from urlparse import urljoin

import requests

from pp.user.validate import error
from pp.user.validate import userdata


def get_log(extra=None):
    m = "{}.{}".format(__name__, extra) if extra else __name__
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

    JSON_CT = {'content-type': 'application/json'}

    ADD = "/users/"

    ALL = "/users/"

    AUTH = "/access/auth/%(username)s/"

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

        rc = json.loads(res.content)
        if "status" in rc:
            # List should be a list and not an error dict!
            raise error.CommunicationError(rc['message'])

        else:
            return rc

        self.log.debug("all: found <%s>" % len(rc))

        return rc

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
        rc = json.loads(res.content)

        # this should be a user dict and not a status which means error:
        if rc and "status" in rc:
            error = rc['error'].strip()
            if hasattr(userdata, error):
                # re-raise the error:
                raise getattr(userdata, error)(rc['message'])
            else:
                raise error.UserRemoveError("%s: %s" % (error, rc['message']))
        else:
            return rc

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
        rc = json.loads(res.content)

        if rc and "status" in rc and rc['status'] == "error":
            error = rc['error'].strip()
            if hasattr(userdata, error):
                # re-raise the error:
                raise getattr(userdata, error)(rc['message'])
            else:
                raise userdata.UserNotFoundError(
                    "{}: {}".format(error, rc['message'])
                )
        else:
            return rc

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
        rc = json.loads(res.content)

        # If this is a dict its an error status.
        if isinstance(rc, dict):
            error = rc['error'].strip()
            if hasattr(userdata, error):
                # re-raise the error:
                raise getattr(userdata, error)(rc['message'])
            else:
                raise SystemError("%s: %s" % (error, rc['message']))
        else:
            return rc

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
        rc = json.loads(res.content)

        # This should be a user dict and not a status response:
        if rc and "status" in rc:
            error = rc['error'].strip()
            if hasattr(userdata, error):
                # re-raise the error:
                raise getattr(userdata, error)(rc['message'])
            else:
                raise SystemError("%s: %s" % (error, rc['message']))
        else:
            return rc

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
    DUMP = "/usiverse/dump/"

    LOAD = "/usiverse/load/"

    def __init__(self, uri="http://localhost:16801"):
        """Set the URI of the UserService.

        :param uri: The base address of the User Service server.

        """
        self.log = get_log("UserService")
        self.base_uri = uri
        self.user = UserManagement(self.base_uri)

    def ping(self):
        """Recover the User Service status page.

        This will raise a connection error or it will return successfully.

        :returns: service status dict.

        """
        res = requests.get(self.base_uri)
        res.raise_for_status()
        return json.loads(res.content)

    def dump(self):
        """Used in testing to dump the entire user universe.

        :returns: A dict.

        This has the form::

            dumped = [
                user dict 1,
                :
                etc
            ]

        """
        uri = urljoin(self.base_uri, self.DUMP)
        self.log.debug("dump: uri <{}>".format(uri))

        res = requests.get(uri)

        rc = json.loads(res.content)

        if res.status_code not in [200]:
            raise error.CommunicationError(rc['message'])

        return rc

    def load(self, data):
        """Used in testing to load an entire user universe.

        :param data: See the return of a call to dump().

        """
        uri = urljoin(self.base_uri, self.LOAD)
        self.log.debug("load: uri <{}>".format(uri))

        data = json.dumps(data)
        res = requests.post(uri, data=data)

        rc = json.loads(res.content)

        if res.status_code not in [200]:
            raise error.CommunicationError(rc['message'])
