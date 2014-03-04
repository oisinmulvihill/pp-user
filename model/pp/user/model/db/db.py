# -*- coding: utf-8 -*-
"""
"""
import uuid
import logging

from pymongo import Connection


__all__ = [
    "DB", "init", "db", "load", "dump", "doc_id_for", "split_docid"
]


class DB(object):
    """An lightwrapper around a mongodb connection.

    The init is given the configuration dict::

        dict(
            db_name='<name>',  # test-db is default.
            port=<mongodb tcp port>,  # 27012 by default.
            host=<mongodb host address>,  # localhost by default.
        )

    Create this class and then call instances db property to
    start using.

    The db_name and host must be strings and they will be stripped
    of trailing whitespace prior to use.

    """
    def __init__(self, config={}):
        self.log = logging.getLogger("%s.DB" % __name__)
        self.config = config
        self.dbname = config.get("dbname", "test-db").strip()
        self.port = int(config.get("port", 27017))
        self.host = config.get("host", "localhost").strip()
        self._connection = None

    def mongo_conn(self):
        """Returns a mongodb connection not tied to a database."""
        if not self._connection:
            self._connection = Connection(self.host, self.port)
        return self._connection

    def conn(self):
        """Return the db connection.

        :returns: A mongodb Connection instance for the configured db name.

        """
        return self.mongo_conn()[self.dbname]['everyone']

    def hard_reset(self):
        """Remove the database from mongo clearing out all contents.

        This is used mainly in testing.

        """
        self.mongo_conn().drop_database(self.dbname)


# The
#
__db = None


def doc_id_for(prefix):
    """Recover a new document '_id'.

    :param prefix: A string e.g. therapist, radio.

    :returns: A string in the form 'prefix-UUID'

    """
    docid = "{:s}".format(uuid.uuid4())

    # strip out the uuid '-' hyphons leaving only one to
    # separate the prefix and id.
    docid = docid.replace("-", "")

    return "{:s}-{:s}".format(prefix, docid)


def split_docid(docid):
    """Split a '_id' into a prefix and uuid.

    :param docid: A string e.g. therapist-2b3..., radio-3c36...

    :returns: (prefix, uuid)

    E.g.::
        (therapist, 2b3...)

    """
    parts = docid.split("-")
    prefix = parts[0]
    uuid = "".join(parts[0:])
    return (prefix, uuid)


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
    from pp.user.model.user import dump
    return dump()


def load(data):
    """Load the users into the user service.

    :param data: See the return from a call to dump().

    """
    from pp.user.model.user import load
    return load(data)


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
