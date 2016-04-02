========================
How to install and test?
========================

How to install?
===============

Requirements
------------

* python **3.3** or newer
* See ``README.md`` for full details on external dependencies.


PyPI (recommended)
---------------------------------

`See Pypi <https://pypi.python.org/pypi/libbmc/>`_

To install with pip:

.. code-block:: sh

    pip install libbmc


Manual installation (recommended for packagers)
-----------------------------------------------

`Download <ihttps://github.com/Phyks/libbmc/archive/master.zip>`_ the archive.

.. code-block:: sh

    python setup.py install


How to run the test suite?
==========================

This page briefly describes how to run the test suite.
This is useful for contributors, for packagers but also for users who wants to check their environment.


Virtualenv
----------

You can make a virtualenv. I like `pew <https://pypi.python.org/pypi/pew/>`_ for that because the API is easier.

The first time, you need to make a virtualenv

.. code-block:: sh

    pew mkproject libbmc
    pip install -r requirements.txt
    python setup.py install
    nosetest


If you already have a virtualenv, you can use workon

.. code-block:: sh

    pew workon libbmc
