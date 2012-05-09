# -*- coding: utf-8 -*-
"""
User Administration views for the REST interface.

PythonPro Limited

"""
#import json

from pyramid.view import view_config

#from pp.web.base.restfulhelpers import status_body


@view_config(route_name='user', request_method='GET', renderer='json')
def user_get(request):
    """
    """
    #msg = 'PUT id <%s> JSON body <%s>' % (request.matchdict['id'], body)
    return {}


@view_config(route_name='users', request_method='PUT', renderer='json')
def user_add(request):
    """
    """
    return {}


@view_config(route_name='user', request_method='POST', renderer='json')
def user_update(request):
    """
    """
    return {}


@view_config(route_name='user', request_method='DELETE', renderer='json')
def user_remove(request):
    """
    """
    return {}
