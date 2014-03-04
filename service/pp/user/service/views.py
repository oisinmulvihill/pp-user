# -*- coding: utf-8 -*-
"""
pp-user-service

This provides the views which are used in the dispatch routing set up.

PythonPro Limited

"""
import json
import pkg_resources

from pyramid.view import view_config

from pp.web.base.restfulhelpers import json_result


@view_config(route_name='home', request_method='GET', renderer='json')
@json_result
def status(request):
    """This is used to 'ping' the web service to check if its running.

    :returns: a status dict which the configured view will return as JSON.

    The dict has the form::

        dict(
            status="ok",
            name="<project name>",
            version="<egg version of pp.user.service>"
        )

    """
    pkg = pkg_resources.get_distribution('pp-user-service')

    return dict(
        status="ok",
        name="pp-user-service",
        version=pkg.version,
    )
