# -*- coding: utf-8 -*-
"""
This provides the REST classes used to access the service.

"""
import json
import logging
from urlparse import urljoin

import requests

#from pp.auth import pwtools
from pp.user.validate import error


def get_log(extra=None):
    mod = '%s' % __name__
    if extra:
        if isinstance(extra, basestring):
            mod = '{}.{}'.format(__name__, extra)
    return logging.getLogger(mod)


class UserService(object):
    """This provides an interface to the REST service for dealing with
    user operations.
    """
    def __init__(self, uri='http://localhost:60706'):
        """Set the URI of the UserService.

        :param uri: The base address of the remote service server.

        """
        self.log = get_log('UserService')
        self.uri = uri

    def ping(self):
        """Recover the User Service status page.

        This will raise a connection error or it will return successfully.

        :returns: service status dict.

        """
        res = requests.get(self.uri)
        res.raise_for_status()
        return json.loads(res.content)
