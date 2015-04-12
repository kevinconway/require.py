import os
import sys

# Modify the sys.path to allow tests to be run without
# installing the module.
test_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(1, test_path + '/../')

import require
import pytest


def test_patch_replaces_and_restores():

    i = __import__

    require.patch_import()

    assert i is not __import__

    require.unpatch_import()

    assert i is __import__


def test_require_gets_local():

    t1_import_test = require.require('import_test')

    assert '.pymodules' in repr(t1_import_test)


def test_require_uses_module_cache():

    t2_import_test = require.require('import_test')
    t3_import_test = require.require('import_test')

    assert t2_import_test is t3_import_test


def test_require_not_conflict_with_import():

    setuptools = require.require('setuptools')

    import setuptools as setuptools2

    assert setuptools2 is not setuptools


@pytest.mark.xfail
def test_BUG_require_cannot_override_standard_lib():

    re2 = require.require('re')

    assert '.pymodules' in repr(re2)
