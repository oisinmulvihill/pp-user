# -*- coding: utf-8 -*-
"""
pp-user-service

This provides the views which are used in the dispatch routing set up.

PythonPro Limited

"""
import json
import pkg_resources

from pyramid.view import view_config

from pp.web.base.restfulhelpers import status_body


@view_config(route_name='home', request_method='GET', renderer='json')
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


# -- Test Request Methods -----------------------------------------------------
#
def any_data_present(request):
    try:
        data = request.json_body
    except ValueError:
        # no data present
        data = {}
    return json.dumps(data)


@view_config(route_name='verb_test', request_method='GET', renderer="json")
def get_view(request):
    msg = 'GET id <%s>' % request.matchdict['id']
    # to_json = False : renderer takes care of conversion to json.
    return status_body(message=msg, to_json=False)


@view_config(route_name='verb_test', request_method='PUT', renderer="json")
def put_view(request):
    body = any_data_present(request)
    msg = 'PUT id <%s> JSON body <%s>' % (request.matchdict['id'], body)
    return status_body(message=msg, to_json=False)


@view_config(route_name='verb_test', request_method='POST', renderer="json")
def post_view(request):
    body = any_data_present(request)
    msg = 'POST id <%s> JSON body <%s>' % (request.matchdict['id'], body)
    return status_body(message=msg, to_json=False)


@view_config(route_name='verb_test', request_method='DELETE', renderer="json")
def delete_view(request):
    msg = 'DELETE id <%s>' % request.matchdict['id']
    return status_body(message=msg, to_json=False)
