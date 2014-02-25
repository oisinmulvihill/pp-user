# -*- coding: utf-8 -*-
"""

Substantially based upon PythonPro's pp-user project to get things off the
ground quickly.

Oisin Mulvihill
(c) PythonPro Limited, RedDeer Limited.
2014-01-23

"""
import os
import uuid
import logging

from pymongo import Connection


def get_log(e=None):
    return logging.getLogger("{0}.{1}".format(__name__, e) if e else __name__)



class DB(object):
    """An lightwrapper around a mongodb connection.

    The init is given the configuration dict::

        dict(
            dbname='<name>',  # test-db is default.
            port=<mongodb tcp port>,  # 27012 by default.
            host=<mongodb host address>,  # localhost by default.
        )

    Create this class and then call instances db property to
    start using.

    The dbname and host must be strings and they will be stripped
    of trailing whitespace prior to use.

    """
    def __init__(self, config={}):
        self.log = get_log("DB")
        self.config = config
        self.dbname = config.get("dbname", "test-db").strip()
        self.port = int(config.get("port", 27017))
        self.host = config.get("host", "localhost").strip()
        self._connection = None

    def mongo_conn(self):
        """Returns a mongodb connection not tied to a database."""
        if not self._connection:
            self.log.debug(
                "mongo_conn: creating connection to host'{}' port'{}'".format(
                    self.host, self.port
                )
            )
            self._connection = Connection(self.host, self.port)
        return self._connection

    def conn(self):
        """Return the db connection.

        :returns: A mongodb Connection instance for the configured db name.

        """
        return self.mongo_conn()[self.dbname]

    def hard_reset(self):
        """Remove the database from mongo clearing out all contents.

        This is used mainly in testing.

        """
        self.log.warn(
            "hard_reset: dropping database '{}'!".format(
                self.dbname
            )
        )
        self.mongo_conn().drop_database(self.dbname)


def doc_id_for(prefix):
    """Recover a new document '_id'.

    :param prefix: A string e.g. therapist, radio.

    :returns: A string in the form 'prefix-UUID'

    """
    docid = uuid.UUID(bytes=os.urandom(16)).hex
    return "{:s}-{:s}-{:s}".format(prefix, docid[:6], docid[6:])


def dump():
    """Dump an entire database into JSON so it can be backed up or loaded.

    :returns: A dict.

    This has the form::

        dumped = [
            {.. user 1 ..},
            :
            etc
        ]

    """
    from reddeer.user.model.user import dump
    return dump()


def load(data):
    """Load the users into the user service.

    :param data: See the return from a call to dump().

    """
    from reddeer.user.model.user import load
    return load(data)


# The internal reference to the DB instance:
#
__db = None


def init(config={}):
    """Set up the default DB instance a call to get_db() will return.

    :param config: See DB() docs for config dict fields.

    :returns: None.

    """
    global __db
    __db = DB(config)


def db():
    """Recover the current configured DB instance.

    If no default instance is configured then ValueError will be raised.

    :returns: The DB instance configured through init().

    """
    if not __db:
        raise ValueError("No DB instance configured! Call init() first.")
    return __db
