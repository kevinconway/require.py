"""Test suite for the custom import logic."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
import sys

import require


def test_patch_replaces_and_restores():
    """Ensure the import function is patched and restored correctly."""
    i = __import__
    require.patch_import()
    assert i is not __import__

    require.unpatch_import()
    assert i is __import__


def test_require_gets_local():
    """Check if require finds the local pymodule."""
    t1_import_test = require.require('import_test')
    assert '.pymodules' in repr(t1_import_test)


def test_require_uses_module_cache():
    """Check if modules are cached when working with pymodules."""
    t2_import_test = require.require('import_test')
    t3_import_test = require.require('import_test')
    assert t2_import_test is t3_import_test


def test_require_not_conflict_with_import():
    """Ensure that using require does not interfere with normal imports."""
    setuptools = require.require('setuptools')
    import setuptools as setuptools2
    assert setuptools2 is not setuptools


def test_require_not_conflict_site_py():
    """Ensure require does not clobber pre-loaded builtins."""
    re2 = require.require('re')
    assert '.pymodules' not in repr(re2)
