import sys
from os import path
import inspect

# If this is the first import of this module then store a reference to the
# original, builtin import statement.
if '__original__import' not in sys.modules:

    sys.modules['__original__import'] = sys.modules['__builtin__'].__import__

# Replacement dict for sys.modules. This is used to allows multiple versions
# of the same modules to be loaded into a single Python process.
MODULE_CACHE = {}


def require(name, locals=None, globals=None, fromlist=None, level=-1):
    """This function wraps the native import to provide pypm routing.

    The basic idea behind pypm routing is to manipulate the sys.path to allow
    the native python import statement to load local dependencies before
    falling back on global imports.

    The purpose of this is to allow each package to use a different copy, or
    even a different version, of a particular dependency.

    In the case of global singletons exposed by a module, this allows packages
    importing those singletons to maintain their own private copies that are
    unaltered by other packages importing the same singletons.

    In the case of two packages requiring different versions of the same
    libraries, this allows each package to have the appropriate version loaded
    in the same python process without causing conflicts.
    """

    # Generate a path to the local pymodules_dir by using the inspect library.
    # Inspect allows us to get the location of the file from which the import
    # statement was called. Using that we can derive the absolute path of the
    # directory the file is in and use that as the base for the pymodules_dir.
    calling_file = inspect.getfile(inspect.stack()[1][0])
    calling_dir = path.dirname(path.abspath(calling_file))
    pymodules_dir = path.join(calling_dir, '.pymodules')
    pymodules_dir_exists = path.isdir(pymodules_dir)

    # Reimplement the sys.modules cache to account for removing localized
    # modules from the global module cache. This allows us to both cache
    # modules once they are imported as well as providing for the ability
    # to load multiple versions of the same module in the same python process.
    if name in MODULE_CACHE:

        # See if this module has already attempted to import the requested
        # module before. Return it if already loaded.
        if calling_dir in MODULE_CACHE[name]:

            return MODULE_CACHE[name][calling_dir]

        # Scan the import cache for an instance where a parent module has
        # already imported the requested module. If a parent has imported
        # the module then we want that version of the module.
        for k in sorted(MODULE_CACHE[name], key=len, reverse=True):

            if calling_dir.startswith(k):

                # Set the cache for quicker lookups later.
                MODULE_CACHE[name][calling_dir] = MODULE_CACHE[name][k]

                return MODULE_CACHE[name][calling_dir]

    if pymodules_dir_exists is True:

        # Make the pymodules_dir the first item on the import path.
        # Note, sys.path[0] should not be modified.
        sys.path.insert(1, pymodules_dir)

    # Use the builtin import function to grab the modules for us.
    # It will scan the search path and import the appropriate module.
    # It also registers the modules with sys.modules.
    try:

        module = sys.modules['__original__import'](name,
                                                   locals,
                                                   globals,
                                                   fromlist,
                                                   level)

    # Once the module is imported, remove the pymodules_dir from the search
    # path to prevent accidental imports from the wrong location.
    finally:

        if pymodules_dir_exists is True:

            sys.path.pop(1)

    # The import statement caches modules in sys.modules so that it does not
    # have to reload them each time. This is what allows modules to expose
    # global singletons across multiple imports. By removing modules loaded
    # from pymodules_dir from the sys.modules cache we are both preventing
    # cache conflicts when multiple versions of the same modules are loaded
    # from different pymodules_dir and breaking the expected functionality of
    # python imports which is that we expect to get the same module with each
    # subsequent call to import. This functionality must be replaced with a
    # custom module cache to replicate the expected behaviour of import.
    if '.pymodules' in repr(module):

        del sys.modules[name]

        # Create the module cache key if it doesn't already exist.
        MODULE_CACHE[name] = MODULE_CACHE.get(name, {})
        # Set the module cache for future calls.
        MODULE_CACHE[name][calling_dir] = module

    # Enjoy your fresh new module object.
    return module


def patch_import():
    """Replace the builtin import statement with the wrapped version.

    This function may be called multiple times without having negative side
    effects.
    """

    sys.modules['__builtin__'].__import__ = require


def unpatch_import():
    """Restore the builtin import statement to the original version.

    This function may be called multiple time without having negative side
    effects.
    """

    sys.modules['__builtin__'].__import__ = sys.modules['__original__import']
