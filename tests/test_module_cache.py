"""Test suite for the sys.modules cache replacement."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from require import ModuleCache


def test_set_allows_get_with_same_path():
    """Ensure an object stored with set is available via get."""
    cache = ModuleCache()
    module = object()
    name = 'test'
    path = '/some/path/to/test'
    cache.set(name=name, path=path, module=module)
    assert cache.get(name=name, path=path) is module


def test_set_prevents_get_with_different_path():
    """Ensure an object stored with set only matches one patch."""
    cache = ModuleCache()
    module = object()
    name = 'test'
    path = '/some/path/to/test'
    cache.set(name=name, path=path, module=module)
    assert cache.get(name=name, path=path + '/notsame') is not module


def test_cached_is_false_before_set():
    """Ensure an object not stored with set is not cached."""
    cache = ModuleCache()
    name = 'test'
    path = '/some/path/to/test'
    assert cache.cached(name=name, path=path) is False


def test_cached_is_true_after_set():
    """Ensure an object stored with set is cached."""
    cache = ModuleCache()
    module = object()
    name = 'test'
    path = '/some/path/to/test'
    cache.set(name=name, path=path, module=module)
    assert cache.cached(name=name, path=path) is True


def test_get_nearest_returns_parent_cache_if_found():
    """Ensure an object stored with set only matches one patch."""
    cache = ModuleCache()
    module = object()
    name = 'test'
    path = '/some/path/to/test'
    cache.set(name=name, path=path, module=module)
    assert cache.get_nearest(name=name, path=path + '/notsame') is module


def test_get_nearest_not_returns_child_cache_if_found():
    """Ensure an object stored with set only matches one patch."""
    cache = ModuleCache()
    module = object()
    name = 'test'
    path = '/some/path/to/test'
    child_path = path + '/some/child'
    cache.set(name=name, path=child_path, module=module)
    assert cache.get_nearest(name=name, path=path) is not module
