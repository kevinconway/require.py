require.py
==========

**A way to manage dependency conflicts.**

What Is require.py?
===================

The core of require.py is a hack of the Python import statement. By default,
all Python modules are installed at the global, site-packages level. This
makes it difficult, and sometimes impossible, to install libraries with
conflicting dependency requirements. To a large extent, virtual environments
have solved this problem by providing sandboxes in which Python modules can
be installed without affecting other virtual environments. Even virtualenvs,
however, do not allow a single Python process to load multiple, conflicting
versions of a dependency as the same time.

This project provides tools for managing dependencies at a Python package
level. This means each Python package (a directory containing an
`__init__.py`) can have a unique version of a dependency that is isolated from
the other packages around it.

Import Behaviour
================

The import logic, and name for this project, are heavily inspired by the
node.js module and import system. The relevant behaviour in node is documented
`here <https://nodejs.org/api/modules.html#modules_loading_from_node_modules_folders>`_.

This package exposes a callable named `require` that can be used to provide the
alternate import logic. Alternatively, there are `patch_import` and
`unpatch_import` available to affect an entire Python process. Here is a
scenario to illustrate the import logic. Given the following project structure:

::

    /myproject/__init__.py
    /myproject/subpackage/__init__.py
    /myproject/subpackage/subsubpackage/__init__.py

Where the `__init__.py` of subsubpackage has the following content:

.. code-block:: python

    from require import require
    requests = require('requests')

The custom import logic will first look for a '.pymodules' directory in
subsubpackage. If found, it will attempt to import requests from that
directory. If not found, it will continue walking the file system upwards
until it hits '/'. After hitting the root, if no '.pymodules' directories are
found the function falls back to the default Python import logic.

Package Management
==================

Keep using pip. This project includes a helper command called `requirepy` that
can be used to help install dependencies into the right subdirectories. It
wraps pip.

License
=======

::

    Copyright 2014 Kevin Conway

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

Contributing
============

All contributions to this project are protected under the agreement found in
the `CONTRIBUTING` file. All contributors should read the agreement but, as
a summary::

    You give us the rights to maintain and distribute your code and we promise
    to maintain an open source distribution of anything you contribute.
