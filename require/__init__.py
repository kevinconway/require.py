"""Alternate import logic that provides for multiple dependency versions."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict
import contextlib
import inspect
import os
import sys
from os import path

# If this is the first import of this module then store a reference to the
# original, builtin import statement. This is used later for the optional
# patching, and restoration, of the import command.
BUILTINS_NAME = '__builtin__' if '__builtin__' in sys.modules else 'builtins'
if '__original__import' not in sys.modules:

    sys.modules['__original__import'] = sys.modules[BUILTINS_NAME].__import__


class ModuleCache(object):

    """Replacment for sys.modules that respects the physical path of an import.

    The standard sys.modules cache can only cache on version of a module that
    has been imported. This replacement uses the file path of the requesting
    module (the one performing the import) as a secondary key when drawing
    from the cache.
    """

    def __init__(self):
        """Initialize the module cache."""
        self._cache = defaultdict(dict)

    def set(self, name, path, module):
        """Store a module in the cache with the given path key.

        Args:
            name (str): The name of the import.
            path (str): The absolute path of the requesting module directory.
            module (object): The Python module object to store.
        """
        self._cache[name][path] = module

    def cached(self, name, path):
        """Determine if an import is already cached.

        Args:
            name (str): The name of the import.
            path (str): The absolute path of the requesting module directory.

        Returns:
            Bool: True if cached else False.
        """
        return name in self._cache and path in self._cache[name]

    def get(self, name, path, default=None):
        """Fetch a module from the cache with a given path key.

        Args:
            name (str): The name of the import.
            path (str): The absolute path of the requesting module directory.
            default: The value to return if not found. Defaults to None.
        """
        return self._cache[name].get(path, default)

    def get_nearest(self, name, path, default=None):
        """Fetch the module from the cache nearest the given path key.

        Args:
            name (str): The name of the import.
            path (str): The absolute path of the requesting module directory.
            default: The value to return if not found. Defaults to None.

        If the specific path key is not present in the cache, this method will
        search the cache for the nearest parent path with a cached value. If
        a parent cache is found it is returned. Otherwise the given default
        value is returned.
        """
        if self.cached(name, path):

            return self.get(name, path, default)

        for parent in sorted(self._cache[name], key=len, reverse=True):

            if path.startswith(parent):

                # Set the cache for quicker lookups later.
                self.set(name, path, self.get(name, parent))
                return self.get(name, path, default)

        return default


@contextlib.contextmanager
def local_modules(path, pymodules='.pymodules'):
    """Set the nearest pymodules directory to the first sys.path element.

    Args:
        path (str): The path to start the search in.
        pymodules (str): The name of the pymodules directory to search for.
            The default value is .pymodules.

    If no valid pymodules directory is found in the path no sys.path
    manipulation will take place.
    """
    path = os.path.abspath(path)
    previous_path = None
    target_path = None

    while previous_path != path:

        if os.path.isdir(os.path.join(path, pymodules)):

            target_path = path
            break

        previous_path, path = path, os.path.dirname(path)

    if target_path:

        sys.path.insert(1, os.path.join(target_path, pymodules))

    try:

        yield target_path

    finally:

        if target_path:

            sys.path.pop(1)


class Importer(object):

    """An import statement replacement.

    This import statement alternative uses a custom module cache and path
    manipulation to override the default Python import behaviour.
    """

    def __init__(self, cache=None, pymodules='.pymodules'):
        """Initialize the importer with a custom cache.

        Args:
            cache (ModuleCache): An instance of ModuleCache.
            pymodules (str): The name to use when searching for pymodules.
        """
        self._cache = cache or ModuleCache()
        self._pymodules = pymodules or '.pymodules'

    @staticmethod
    def _calling_dir():
        """Get the directory containing the code that called require.

        This function will look 2 or 3 frames up from the stack in order to
        resolve the directory depending on whether require was called
        directly or proxied through __call__.
        """
        stack = inspect.stack()
        current_file = __file__
        if not current_file.endswith('.py'):

            current_file = current_file[:-1]

        calling_file = inspect.getfile(stack[2][0])
        if calling_file == current_file:

            calling_file = inspect.getfile(stack[3][0])

        return path.dirname(path.abspath(calling_file))

    def require(
            self,
            name,
            locals=None,
            globals=None,
            fromlist=None,
            level=None,
    ):
        """Import modules using the custom cache and path manipulations."""
        # Default and allowed values change after 3.3.
        level = -1 if sys.version_info[:2] < (3, 3) else 0
        calling_dir = self._calling_dir()
        module = self._cache.get_nearest(name, calling_dir)
        if module:

            return module

        with local_modules(calling_dir, self._pymodules) as pymodules:

            module = sys.modules['__original__import'](
                name,
                locals,
                globals,
                fromlist,
                level,
            )

        if self._pymodules in repr(module):

            del sys.modules[name]
            # Create the module cache key if it doesn't already exist.
            self._cache.set(name, pymodules, module)

        # Enjoy your fresh new module object.
        return module

    def __call__(self, *args, **kwargs):
        """Proxy functions for require."""
        return self.require(*args, **kwargs)


require = Importer()


def patch_import(importer=require):
    """Replace the builtin import statement with the wrapped version.

    This function may be called multiple times without having negative side
    effects.
    """

    sys.modules[BUILTINS_NAME].__import__ = importer


def unpatch_import():
    """Restore the builtin import statement to the original version.

    This function may be called multiple time without having negative side
    effects.
    """

    sys.modules[BUILTINS_NAME].__import__ = sys.modules['__original__import']
