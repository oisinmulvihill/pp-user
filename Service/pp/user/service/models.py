# -*- coding: utf-8 -*-
"""
pp-user-service

PythonPro Limited

"""
import logging


def get_log(fn=''):
    if fn and fn.strip():
        fn = ".%s" % fn
    return logging.getLogger('%s%s' % (__name__, fn))

#import transaction
# from sqlalchemy import Column
# from sqlalchemy import Integer
# from sqlalchemy import Unicode
# from sqlalchemy.exc import IntegrityError
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import scoped_session
# from sqlalchemy.orm import sessionmaker
# from zope.sqlalchemy import ZopeTransactionExtension


#DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
# Base = declarative_base()


def populate():
    # session = DBSession()
    # model = MyModel(name=u'root', value=55)
    # session.add(model)
    # session.flush()
    # transaction.commit()
    pass


def initialize_sql(engine):
    # DBSession.configure(bind=engine)
    # Base.metadata.bind = engine
    # Base.metadata.create_all(engine)
    # try:
    #     populate()
    # except IntegrityError:
    #     transaction.abort()
    pass
