Welcome to pp-user-service documentation!
=========================================

Contents:

.. toctree::
   :maxdepth: 3


Quick start
-----------

The paver pavement.py allows the repo to appear as one python project. I
implement the different commands for the contained egg packages.

For example, to set up all contained eggs in development mode::

    python setup.py develop


Run the server
~~~~~~~~~~~~~~

Run the server using the default development.ini do::

    python setup.py develop


service
-------

The REST service which provides user identity and management.

pp.user.service


userservice-admin
~~~~~~~~~~~~~~~~~

The command line tool to manage the user service. It can add / remove users.

client
------

The REST client which talks to the REST service.

pp.user.client



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`