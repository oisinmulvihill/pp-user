# -*- coding: utf-8 -*-
"""
pp-allotment-service

PythonPro Limited

"""
import logging

from pyramid.view import view_config

from pp.user.model import db


def get_log(extra=None):
    m = "{}.{}".format(__name__, extra) if extra else __name__
    return logging.getLogger(m)


@view_config(route_name='dump', request_method='GET', renderer='json')
def dump_everyone(request):
    """JSON dump of everything.

    Not meant for anything other then testing!

    """
    get_log("dump_everyone").warn("Dumping the entire system to JSON.")
    return db.dump()


@view_config(route_name='load', request_method='POST', renderer='json')
def load_everyone(request):
    """Load the JSON representation of all known users.

    Not meant for anything other then testing!

    """
    get_log("load_everyone").warn("Loading from JSON.")
    data = request.json_body
    db.load(data)
