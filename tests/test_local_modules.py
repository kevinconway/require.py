"""Test suite for the sys.path manipulation context manager."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import sys

from require import local_modules


def test_manager_modifies_nothing_when_no_pymodules(tmpdir):
    """Check that nothing happens when no pymodules present on the path."""
    sys_path_length = len(sys.path)
    with local_modules(str(tmpdir)) as pymodules_path:

        assert pymodules_path is None
        assert len(sys.path) == sys_path_length


def test_manager_returns_path_when_pymodules(tmpdir):
    """Check if the correct path is yielded when pymodules are present."""
    pymodules = tmpdir.mkdir('.pymodules')
    with local_modules(str(tmpdir)) as pymodules_path:

        assert pymodules_path == str(tmpdir)


def test_manager_sets_sys_path_when_pymodules(tmpdir):
    """Check if the correct path is yielded when pymodules are present."""
    pymodules = tmpdir.mkdir('.pymodules')
    sys_path_length = len(sys.path)
    with local_modules(str(tmpdir)):

        assert str(pymodules) == sys.path[1]
        assert len(sys.path) == (sys_path_length + 1)

    assert len(sys.path) == sys_path_length
