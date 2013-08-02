PyPm
====

**A new way to manage dependencies in Python.**

What Is PyPm?
=============

PyPm is two basic pieces.

The first is an extension of the Python `import` statement that allows Python
files to import dependencies from a local source before attempting to load
those dependencies from the normal system path. This allows the same Python
process to load different version of the same module at the same time.

The second part of PyPm is a command line package management utility, similar
to `easy_install` or `pip`, that can install packages at the local level.

Local Module Importing
======================

A huge component of PyPm is our extension to the normal Python `import`
statement. Our extension is transparent and still utilizes the built-in
functionality.

The `pypm` package exposes two methods at the top level: `patch_import` and
`unpatch_import`. These functions enable and disable the import logic
extensions. Using the import extensions allows Python to use the following
logic::

    import somepackage

    # Has this module imported `somepackage` before?

    # If so then return the loaded module from the import cache.

    # If not then has a parent module imported `somepackage` before?

    # If so then return the loaded module from the import cache.

    # If not then is there a ".pymodules" folder in the same directory?

    # If so then try to import `somepackage` from ".pymodules".

        # If module not found then continue with logic.

    # If not then is there a ".pymodules" folder in a parent directory?

    # If so then try to import `somepackage` from those ".pymodules".

        # If module not found then continue with logic.

    # Fall back on normal import from sys.path.

Alternatively, the module loading functionality may be used without patching
the built-in import by using the `require` function that is also exposed at
the top level of the pypm package. It takes the same arguments and behaves
the same way as the built-in `__import__` function::

    mymodule = pypm.require('mypackage.mymodule')

Package Management
==================

With the above extensions to the import logic, we need a package manager that
can install modules from PyPi into those local ".pymodules" folders. This
package, when installed, will add a script called `pypm` that allows users
to install and uninstall local dependencies.

License
=======

This project is released and distributed under the Apache 2.0 license.

Contributing
============

Contributions to this project are protected by a contributor's agreement
detailed in CONTRIBUTING. All contributors are urged to read the document
before contributing.
