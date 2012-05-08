pp-user-service
===============

This provides the User Service to authenticate and recover metadata about
people stored. This repository provides two egg packages. The REST service and
client packages.

For more information see the sphinx documentation.

E.g.::

    # From a clean checkout set up all parts of this project (once off):
    python setup.py develop

    # To (re)build the sphinx documentation:
    python setup.py docs

    # Open the documentation in a browser on your machine:
    firefox docs/build/html/index.html


Quick start
-----------

Run the server
~~~~~~~~~~~~~~

Run the server using the default development.ini do::

    python setup.py runserver
