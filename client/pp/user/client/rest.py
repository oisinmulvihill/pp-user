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
from pp.user.client.user import UserManagement


def get_log(e=None):
    return logging.getLogger("{0}.{1}".format(__name__, e) if e else __name__)


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
        self.api = self.user

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
