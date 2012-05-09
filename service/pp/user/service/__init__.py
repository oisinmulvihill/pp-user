# -*- coding: utf-8 -*-
"""
PythonPro REST Service 'pp-user-service'

"""
import logging
import httplib

from pyramid.config import Configurator

from pp.web.base import restfulhelpers
from pp.web.base import common_db_configure
from pp.web.base import pp_auth_middleware


def get_log():
    return logging.getLogger("pp.user.service")


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    common_db_configure(settings)

    config = Configurator(settings=settings)

    # Custom 404 json response handler. This returns a useful JSON
    # response in the body of the 404.
    # XXX this is conflicting
    #config.add_view(restfulhelpers.notfound_404_view, context=HTTPNotFound)

    not_found = restfulhelpers.xyz_handler(httplib.NOT_FOUND)
    config.add_view(not_found, context='pyramid.exceptions.NotFound')

    bad_request = restfulhelpers.xyz_handler(httplib.BAD_REQUEST)
    config.add_view(bad_request, context='pyramid.httpexceptions.HTTPBadRequest')

    # Maps to the status page:
    config.add_route('home', '/')

    # Testing clients for GET, PUT, POST, DELETE against out server:
    config.add_route('verb_test', '/verb/test/{id}')

    # Pick up the views which set up the views automatically:
    #
    config.scan("pp.user.service")

    # Make the pyramid app I'll then wrap in other middleware:
    app = config.make_wsgi_app()

    app = pp_auth_middleware(settings, app)

    # RESTful helper class to handle PUT, DELETE over POST requests:
    app = restfulhelpers.HttpMethodOverrideMiddleware(app)

    # Should be last to catch all errors of below wsgi apps. This
    # returns useful JSON response in the body of the 500:
    app = restfulhelpers.JSONErrorHandler(app)

    return app

