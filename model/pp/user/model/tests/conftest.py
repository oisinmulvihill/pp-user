# -*- coding: utf-8 -*-
"""

Substantially based upon PythonPro's pp-user project to get things off the
ground quickly.

Oisin Mulvihill
(c) PythonPro Limited, RedDeer Limited.
2014-01-23

"""
import uuid
import logging

import pytest


def get_log(e=None):
    return logging.getLogger("{0}.{1}".format(__name__, e) if e else __name__)


@pytest.fixture(scope='session')
def logger(request):
    """Set up a root logger showing all entries in the console.
    """
    log = logging.getLogger()
    hdlr = logging.StreamHandler()
    fmt = '%(asctime)s %(name)s %(levelname)s %(message)s'
    formatter = logging.Formatter(fmt)
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
    log.setLevel(logging.DEBUG)
    log.propagate = False

    return log


@pytest.fixture(scope='function')
def mongodb(request):
    """Set up a mongo connection reset and ready to roll.
    """
    from pp.user.model import db as mongo

    log = get_log('mongodb')

    db_name = "testingdb-{}".format(uuid.uuid4().hex)

    mongo.init(dict(db_name=db_name))
    db = mongo.db()
    db.hard_reset()
    log.info('database ready for testing "{}"'.format(db_name))

    def db_teardown(x=None):
        db.hard_reset()
        log.warn('teardown database for testing "{}"'.format(db_name))

    request.addfinalizer(db_teardown)

    return db
