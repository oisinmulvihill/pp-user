pp-user
=======

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

Running all tests
~~~~~~~~~~~~~~~~~

The py.test lib is used for this and is called as follows::

    pytest


Run the server
~~~~~~~~~~~~~~

Run the server using the default development.ini do::

    python setup.py runserver
