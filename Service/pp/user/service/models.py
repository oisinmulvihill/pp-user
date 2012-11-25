# -*- coding: utf-8 -*-
"""
pp-user-service

PythonPro Limited

"""
import logging


def get_log(extra=None):
    m = "{}.{}".format(__name__, extra) if extra else __name__
    return logging.getLogger(m)


def populate():
    pass


def initialize_sql(engine):
    pass
