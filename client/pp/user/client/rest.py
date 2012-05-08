# -*- coding: utf-8 -*-
"""
This provides the REST classes used to access the User Service.

"""
import json
import logging

import requests


def get_log(extra=None):
    m = "pp.user.client.rest"
    if extra:
        if isinstance(extra, basestring):
            m = "%s.%s" % (m, extra)
    return logging.getLogger(m)


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

    def ping(self):
        """Recover the User Service status page.

        This will raise a connection error or it will return successfully.

        :returns: service status dict.

        """
        res = requests.get(self.uri)
        res.raise_for_status()
        return json.loads(res.content)
